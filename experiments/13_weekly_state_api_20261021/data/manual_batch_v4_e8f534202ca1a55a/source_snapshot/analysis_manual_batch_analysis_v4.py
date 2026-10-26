"""Offline intake and exploratory batch-level analysis; never fabricates runs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import nct, t

from . import manual_batch_v4 as batch
from .pivot_inference_v2 import ENDPOINTS, holm_adjust, paired_inference

PREFIXES = (1, 2, 5, 10, 20, 40)
MAX_BATCHES = 40


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze(path, data):
    path = Path(path)
    data = data if isinstance(data, bytes) else (json.dumps(data, indent=2, allow_nan=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ValueError("Refusing to overwrite an existing receipt")
    if not path.exists():
        path.write_bytes(data)


def intake(root, json_path, *, website_label, reasoning_setting, transcript_path=None,
           reviewed=False, fresh_chat_confirmed=False, reviewer="", note=""):
    if not website_label.strip() or not reasoning_setting.strip():
        raise ValueError("Record actual displayed settings separately from requested model")
    if type(reviewed) is not bool or type(fresh_chat_confirmed) is not bool:
        raise ValueError("Review and fresh-chat confirmations must be explicit Booleans")
    if reviewed and (not reviewer.strip() or not note.strip() or not transcript_path):
        raise ValueError("Review requires a full transcript, reviewer and adherence note")
    raw = Path(json_path).read_bytes()
    transcript = Path(transcript_path).read_bytes() if transcript_path else None
    if transcript is not None and (not transcript or transcript == raw):
        raise ValueError("The results JSON cannot serve as the chat/tool transcript")
    receipt = dict(source_sha256=hashlib.sha256(raw).hexdigest(), website_label=website_label,
                   reasoning_setting=reasoning_setting, transcript_reviewed=reviewed,
                   fresh_chat_confirmed=fresh_chat_confirmed, reviewer=reviewer, review_note=note,
                   transcript_sha256=hashlib.sha256(transcript).hexdigest() if transcript else None,
                   provider_identity_verified=False, eligible=False, error=None)
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
        if isinstance(payload, dict):
            receipt.update(batch_id=payload.get("batch_id"), model=payload.get("requested_model_slot"))
        rows = batch.audit(payload)
        receipt.update(batch_id=payload["batch_id"], model=payload["requested_model_slot"],
                       complete=payload["complete"], outcomes=rows, replay_passed=True,
                       eligible=payload["complete"] and reviewed and fresh_chat_confirmed)
    except (ValueError, KeyError, TypeError, IndexError, AttributeError, UnicodeDecodeError) as exc:
        receipt.update(error=f"{type(exc).__name__}: {exc}", replay_passed=False, outcomes=[])
    folder = Path(root) / "intake" / batch.core.digest(receipt)[:20]
    freeze(folder / "original.json", raw)
    if transcript is not None:
        freeze(folder / "transcript.bin", transcript)
    freeze(folder / "receipt.json", receipt)
    return receipt


def collect(root):
    receipts, eligible, seen, settings = [], [], set(), {}
    for path in sorted((Path(root) / "intake").glob("*/receipt.json"), key=lambda p: (p.stat().st_mtime_ns, str(p))):
        r = json.loads(path.read_text())
        if sha(path.parent / "original.json") != r["source_sha256"]:
            raise ValueError("Intake source changed")
        if r.get("transcript_sha256") and sha(path.parent / "transcript.bin") != r["transcript_sha256"]:
            raise ValueError("Intake transcript changed")
        # Re-audit every accepted physical record; receipt is not a substitute.
        if r["replay_passed"]:
            fresh = batch.audit(json.loads((path.parent / "original.json").read_text(encoding="utf-8-sig")))
            if fresh != r["outcomes"]:
                raise ValueError("Receipt outcomes changed")
        receipts.append(r)
        if not r["eligible"]:
            continue
        identity = r["batch_id"]
        if identity in seen:
            raise ValueError("Duplicate batch: keep both receipts, resolve before inference")
        seen.add(identity)
        key = r["model"]
        setting = (r["website_label"], r["reasoning_setting"])
        if key in settings and settings[key] != setting:
            raise ValueError("Mixed displayed model/settings within a model slot")
        settings[key] = setting
        eligible.append(r)
    attempts = {model: {r.get("batch_id") or r["source_sha256"] for r in receipts if r.get("model") == model}
                for model in batch.SLOTS}
    if any(len(ids) > MAX_BATCHES for ids in attempts.values()):
        raise ValueError("More than 40 attempts: preserve them but prepare a new plan before further inference")
    return receipts, eligible


def verify_manifest(root):
    """Check exact sources/prompts against this new protocol's preparation."""
    root = Path(root)
    path = root / "manifest.json"
    if not path.exists():
        raise ValueError("Prepare the frozen batch manifest before analyzing observations")
    m = json.loads(path.read_text())
    if m["study_id"] != batch.study_id():
        raise ValueError("Study fingerprint changed")
    src = Path(__file__).parent
    exp = root.parent.parent
    paths = dict(controller=src / "manual_weekly_v3.py", coordinator=src / "manual_batch_v4.py",
                 analysis=Path(__file__), inference=src / "pivot_inference_v2.py",
                 protocol=exp / "hypotheses/MANUAL_BATCH_V4.md",
                 builder=exp.parent.parent / "scripts/prepare_manual_batch_v4.py")
    # Uploaded file names are the manifest's first two keys.
    paths["beergame_controller.py"] = paths.pop("controller")
    paths["batch_runner.py"] = paths.pop("coordinator")
    for key, source in paths.items():
        if sha(source) != m["source_hashes"][key]:
            raise ValueError("Frozen scientific source changed: " + key)
    for name, expected in m["prompts"].items():
        if sha(exp / "prompts/FOUR_MODEL_MANUAL" / name) != expected:
            raise ValueError("Exact prompt changed: " + name)
    if sha(exp / "prompts/FOUR_MODEL_MANUAL/beer_game_tools.zip") != m["zip_sha256"]:
        raise ValueError("Upload package changed")
    return m


def power(n, effect, alpha=.05 / 20):
    """Planning approximation: paired normal differences, NOT observed power."""
    n = np.asarray(n)
    cutoff = t.isf(alpha / 2, n - 1)
    delta = abs(effect) * np.sqrt(n)
    return nct.sf(cutoff, n - 1, delta) + nct.cdf(-cutoff, n - 1, delta)


def power_figures(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    curves, sizes = [], []
    fig, ax = plt.subplots(figsize=(11, 6))
    for effect in (0., .2, .3, .5, .8):
        counts = np.arange(2, 301)
        values = power(counts, effect)
        ax.plot(counts * batch.CHAINS, values, label=f"Assumed effect d = {effect:g}")
        curves.extend(dict(independent_chats=int(n), chains_per_condition=int(n * batch.CHAINS),
                           total_chain_instances=int(n * batch.CHAINS * 3), assumed_d=effect,
                           approximate_power=float(p)) for n, p in zip(counts, values))
        grid = np.arange(2, 10001)
        ps = power(grid, effect)
        for target in (.8, .9):
            found = grid[ps >= target]
            count = int(found[0]) if len(found) else None
            sizes.append(dict(assumed_d=effect, target_power=target, independent_chats=count,
                              chains_per_condition=count * batch.CHAINS if count else None))
    ax.axhline(.8, color="grey", ls="--", lw=1)
    ax.axvline(400, color="black", ls=":", lw=1, label="Planned 40 chats / 400 chains per condition")
    ax.set(xlabel="Accumulated chains PER CONDITION (10 dependent chains per fresh chat)",
           ylabel="Probability of detection under assumed nonzero effect",
           ylim=(0, 1), title="Sample-size planning — assumed effects, no new observed results")
    ax.secondary_xaxis("top", functions=(lambda x: x / 10, lambda x: x * 10)).set_xlabel("Independent fresh-chat batches per model")
    ax.legend(fontsize=9, loc="lower right")
    fig.text(.02, .01, "Normal paired-difference approximation; two-sided alpha .0025 (20 endpoints). No guaranteed significance.", fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, 1))
    for ext in ("png", "pdf", "svg"):
        fig.savefig(output / f"SAMPLE_SIZE_PLANNING.{ext}", dpi=220)
    plt.close(fig)
    pd.DataFrame(curves).to_csv(output / "power_assumptions.csv", index=False)
    pd.DataFrame(sizes).to_csv(output / "required_samples_assuming_effect.csv", index=False)
    return sizes


def analyze(root, output):
    verify_manifest(root)
    receipts, eligible = collect(root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows = [row for r in eligible for row in r["outcomes"]]
    pd.DataFrame(rows).to_csv(output / "extracted_results.csv", index=False)
    counts = {model: sum(r["model"] == model for r in eligible) for model in batch.SLOTS}
    if any(n > MAX_BATCHES for n in counts.values()):
        raise ValueError("The fixed 40-chat plan is exceeded; freeze a new protocol before extending")
    estimates = []
    for prefix in PREFIXES:
        group = []
        for model in batch.SLOTS:
            selected = [r for r in eligible if r["model"] == model][:prefix]
            if len(selected) != prefix:
                continue  # No extrapolated points or placeholder zero outcomes.
            for name, metric, plus, minus, direction in ENDPOINTS:
                differences = []
                for r in selected:
                    arms = {row["arm"]: row for row in r["outcomes"]}
                    if arms[plus][metric] is not None and arms[minus][metric] is not None:
                        differences.append(arms[plus][metric] - arms[minus][metric])
                if len(differences) != prefix:
                    continue
                result = paired_inference(differences) if prefix >= 2 else dict(
                    n_pairs=1, mean_difference=differences[0], ci95_low=None, ci95_high=None, p_two_sided=None)
                group.append(dict(model=model, hypothesis=name, metric=metric,
                                  prefix_chats=prefix, chains_per_condition=prefix * batch.CHAINS,
                                  contrast=plus + "-" + minus, expected_direction=direction, **result))
        index = {(r["model"], r["hypothesis"]): r for r in group}
        family = [(m, e[0]) for m in batch.SLOTS for e in ENDPOINTS]
        adjusted = holm_adjust([index[k]["p_two_sided"] if k in index else None for k in family])
        for key, p in zip(family, adjusted):
            if key in index:
                index[key]["p_holm_20"] = p
        estimates.extend(group)
    table = pd.DataFrame(estimates)
    table.to_csv(output / "observed_sample_size_sweep.csv", index=False)
    if estimates:
        fig, axes = plt.subplots(2, 3, figsize=(16, 8))
        for ax, endpoint in zip(axes.flat, ENDPOINTS):
            for model in batch.SLOTS:
                subset = table[(table.model == model) & (table.hypothesis == endpoint[0])]
                if subset.empty:
                    continue
                ax.plot(subset.chains_per_condition, subset.mean_difference, marker="o", label=model)
                mask = subset.ci95_low.notna()
                ax.fill_between(subset.chains_per_condition[mask].astype(float), subset.ci95_low[mask].astype(float), subset.ci95_high[mask].astype(float), alpha=.1)
            ax.axhline(0, color="grey", lw=1)
            ax.set(title=f"{endpoint[0]}: {endpoint[1]}", xlabel="Chains per condition (10 per chat)", ylabel="Mean paired chat difference")
        axes.flat[-1].axis("off")
        handles, labels = axes.flat[0].get_legend_handles_labels()
        axes.flat[-1].legend(handles, labels, loc="center")
        fig.suptitle("Observed joint-context model responses — pointwise 95% block bootstrap intervals")
        fig.tight_layout()
        for ext in ("png", "pdf", "svg"):
            fig.savefig(output / f"OBSERVED_H1_H4_SWEEP.{ext}", dpi=220)
        plt.close(fig)
    sizes = power_figures(output)
    attempted = {m: len({r.get("batch_id") or r["source_sha256"] for r in receipts if r.get("model") == m}) for m in batch.SLOTS}
    result = dict(study_id=batch.study_id(), received_files=len(receipts), attempted_chats=attempted,
                  eligible_fresh_chat_batches=counts, fixed_target_per_model=MAX_BATCHES,
                  primary_sample_complete=all(n == MAX_BATCHES for n in counts.values()),
                  observations=estimates, planning=sizes, api_calls=0)
    (output / "RESULTS.json").write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    lines = ["# H1–H4: four-model manual collection", "",
        f"1. Reviewed fresh-chat batches: {counts}. Target: 40 per model; 10 chains per condition per chat.",
        "2. No H1–H4 verification can be claimed from a single batch or an uncollected sample.",
        "3. Observed sweeps use only returned, replayed, transcript-reviewed batches; planning curves use stated hypothetical effects.",
        "4. This simplified design shares all conditions in one context. It tests joint-context AI responses, with possible education carryover; it cannot establish human time-pressure or isolated education effects.", "",
        "## Where the hypotheses are measured", "",
        "| Hypothesis | Measurement | Contrast / predicted sign |", "|---|---|---|",
        "| H1 | Pipeline-response sensitivity (proxy for outstanding-order use) | B − A < 0 |",
        "| H2 | 24-week holding + backlog cost per chain | B − A > 0 |",
        "| H3 | Pipeline-response sensitivity | C − B > 0 |",
        "| H4a | Mean individual weekly order variance | C − B < 0 |",
        "| H4b | Mean order variance / external demand variance | C − B < 0 |", "",
        "A = control reading + extra review. B = control + initial committed. C = causal education + initial committed.", "",
        "[Sample-size planning](SAMPLE_SIZE_PLANNING.png) · [Assumed required samples](required_samples_assuming_effect.csv) · [Extracted results](extracted_results.csv) · [Observed sweep table](observed_sample_size_sweep.csv)", "",
        "No elapsed human deadline is enforced. Sensitivity is not an identified underweighting coefficient. A model can rationally produce no difference. Within-chat chains, weeks and roles are not independent observations.", "",
        "Inference is exploratory and conditional on independent fresh chats and symmetric paired differences. Two-sided paired sign flips and Holm correction retain all 20 model/endpoints. Prefixes 1/2/5/10/20/40 are descriptive; no stopping at first significance. A single batch has no inferential p-value or interval. Full-sample inference is planned at 40 chats per model. Pointwise bootstrap intervals are not simultaneous intervals.", "",
        "Planning assumes normally distributed paired chat differences and d = mean difference / between-chat SD. It uses a paired-t approximation and conservative alpha .05/20; it is not a power guarantee for the sign-flip test. Zero true effect has no sample size that produces reliable support. The old pilot does not estimate the new design's between-chat variance.", "",
        "Methods: [SciPy noncentral t](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nct.html).", ""]
    if estimates:
        lines += ["## Returned observations", "", "[Observed effects and sample sizes](OBSERVED_H1_H4_SWEEP.png)", "", "See observed_sample_size_sweep.csv for exact estimates, intervals and p-values.", ""]
    else:
        lines += ["No new model responses have been collected for this version. An observed significance curve will appear after eligible results arrive.", ""]
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    return result
