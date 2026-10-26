"""Offline intake and exploratory batch-level analysis; never fabricates runs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from statistics import mean, variance

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import nct, t

from . import manual_batch_v5 as batch
from .pivot_inference_v2 import ENDPOINTS, holm_adjust, paired_inference

PREFIXES = (1, 2, 5, 10, 20, 40)
CHAIN_PREFIXES = (5, 10, 20, 30, 40, 50)
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
    # Immutable first-receipt order, independent of file modification times.
    index_path = Path(root) / "attempt_order.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    attempts = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines()] if index_path.exists() else []
    identity = receipt.get("batch_id") or receipt["source_sha256"]
    previous = next((entry for entry in attempts if entry["identity"] == identity), None)
    if previous and previous["model"] != receipt.get("model"):
        raise ValueError("Same batch cannot be assigned to another model")
    if previous is None:
        previous = dict(identity=identity, model=receipt.get("model"), order=len(attempts) + 1,
                        first_received_utc=datetime.now(timezone.utc).isoformat())
        with index_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(previous) + "\n")
    receipt["attempt_order"] = previous["order"]
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
    return sorted(receipts, key=lambda r: r["attempt_order"]), sorted(eligible, key=lambda r: r["attempt_order"])


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
    paths = dict(controller=src / "manual_weekly_v3.py", coordinator=src / "manual_batch_v5.py",
                 analysis=Path(__file__), inference=src / "pivot_inference_v2.py",
                 protocol=exp / "hypotheses/MANUAL_BATCH_V5.md",
                 builder=exp.parent.parent / "scripts/prepare_manual_batch_v5.py")
    # Uploaded file names are the manifest's first two keys.
    paths["beergame_controller.py"] = paths.pop("controller")
    paths["batch_runner.py"] = paths.pop("coordinator")
    for key, source in paths.items():
        if sha(source) != m["source_hashes"][key]:
            raise ValueError("Frozen scientific source changed: " + key)
    for name, expected in m["prompts"].items():
        if sha(exp / "prompts/LARGE_SAMPLE_V5" / name) != expected:
            raise ValueError("Exact prompt changed: " + name)
    if sha(exp / "prompts/LARGE_SAMPLE_V5/beer_game_tools.zip") != m["zip_sha256"]:
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
    ax.axvline(MAX_BATCHES * batch.CHAINS, color="black", ls=":", lw=1, label=f"Planned {MAX_BATCHES} chats / {MAX_BATCHES * batch.CHAINS:,} chains per condition")
    ax.set(xlabel=f"Accumulated chains PER CONDITION ({batch.CHAINS} dependent chains per fresh chat)",
           ylabel="Probability of detection under assumed nonzero effect",
           ylim=(0, 1), title="Sample-size planning — assumed effects, no new observed results")
    ax.secondary_xaxis("top", functions=(lambda x: x / batch.CHAINS, lambda x: x * batch.CHAINS)).set_xlabel("Independent fresh-chat batches per model")
    ax.legend(fontsize=9, loc="lower right")
    fig.text(.02, .01, "Normal paired-difference approximation; two-sided alpha .0025 (20 endpoints). No guaranteed significance.", fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, 1))
    for ext in ("png", "pdf", "svg"):
        fig.savefig(output / f"SAMPLE_SIZE_PLANNING.{ext}", dpi=220)
    plt.close(fig)
    pd.DataFrame(curves).to_csv(output / "power_assumptions.csv", index=False)
    pd.DataFrame(sizes).to_csv(output / "required_samples_assuming_effect.csv", index=False)
    return sizes


def chain_metrics(payload):
    """Extract observed chain outcomes after strict batch audit, not extra samples."""
    result = []
    for arm in "ABC":
        raw = payload["games"][arm]
        game = batch.core.WebsiteGame(raw["case_id"], arm, raw["replicate"], raw["chains"],
                                     seed=raw["seed"], study_id=raw["study_id"])
        for initial, final in zip(raw["initial_orders"], raw["final_orders"]):
            game.display()
            game.submit_initial(dict(zip(game.chain_ids, initial)))
            if arm == "A":
                game.display()
                game.submit_revision(dict(zip(game.chain_ids, final)))
        if len(game.final_orders) != 24 or raw["probe_final"] is None:
            raise ValueError("Only completed, reviewed batches enter chain-prefix summaries")
        probes = game.display()["hypothetical_independent_decisions"]
        pairs = {}
        for probe in probes:
            key = (probe["chain_id"], probe["role"], probe["backlog"])
            pairs.setdefault(key, {})[probe["supply_line"]] = raw["probe_final"][probe["probe_id"]]
        for index, cid in enumerate(game.chain_ids):
            rows = [r for r in game.rows if r["chain_id"] == cid]
            demand_var = variance([d[index] for d in game.realized_demand])
            order_vars = [variance([r["order"] for r in rows if r["role"] == role]) for role in batch.core.ROLES]
            result.append(dict(model=payload["requested_model_slot"], batch_id=payload["batch_id"], arm=arm,
                chain_id=cid, chain_index=index + 1, chain_total_cost=sum(r["cost"] for r in rows),
                mean_role_order_variance=mean(order_vars),
                mean_role_bullwhip=mean(order_vars) / demand_var if demand_var else None,
                pipeline_sensitivity=mean((pair[8] - pair[32]) / 24 for key, pair in pairs.items() if key[0] == cid)))
    return result


def chain_prefix_summary(chain_rows):
    """Deterministic first-k chains; descriptive means, deliberately no p-values."""
    frame = pd.DataFrame(chain_rows)
    if frame.empty:
        return pd.DataFrame()
    metrics = list(dict.fromkeys(e[1] for e in ENDPOINTS))
    rows = []
    for (model, batch_id, arm), group in frame.groupby(["model", "batch_id", "arm"], sort=False):
        for n in CHAIN_PREFIXES:
            sub = group[group.chain_index <= n]
            if len(sub) != n:
                raise ValueError("Missing chain in fixed prefix")
            row = dict(model=model, batch_id=batch_id, arm=arm, chains_per_condition=n)
            row.update({metric: float(sub[metric].mean()) if sub[metric].notna().all() else None for metric in metrics})
            rows.append(row)
    return pd.DataFrame(rows)


def save_figure(fig, output, stem):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(Path(output) / f"{stem}.{ext}", dpi=220)
    plt.close(fig)


def plot_chain_prefixes(table, output):
    metrics = ("pipeline_sensitivity", "chain_total_cost", "mean_role_order_variance", "mean_role_bullwhip")
    titles = ("H1/H3: pipeline responsiveness", "H2: cost per chain", "H4a: individual order variance", "H4b: bullwhip")
    for model in batch.SLOTS:
        selected = table[table.model == model]
        if selected.empty:
            continue
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        for ax, metric, title in zip(axes.flat, metrics, titles):
            for arm in "ABC":
                subset = selected[selected.arm == arm]
                grouped = subset.groupby("chains_per_condition")[metric]
                # No silent averaging over undefined ratios.
                means = grouped.mean().where(grouped.count() == grouped.size())
                ax.plot(means.index, means.values, marker="o", label=arm)
            ax.set(title=title, xlabel="First k chains per condition WITHIN each chat", ylabel="Mean outcome")
            ax.set_xticks(CHAIN_PREFIXES)
            ax.legend(title="Condition")
        fig.suptitle(f"{model}: size sensitivity within {selected.batch_id.nunique()} returned chat(s)\nDescriptive only; chains share the model context")
        fig.tight_layout()
        save_figure(fig, output, f"WITHIN_RESPONSE_SIZE_{model}")


def plot_p_values(table, output):
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    lower = max(1e-12, min(1e-4, float(table.p_holm_20.dropna().min()) / 2))
    for ax, endpoint in zip(axes.flat, ENDPOINTS):
        for model in batch.SLOTS:
            sub = table[(table.model == model) & (table.hypothesis == endpoint[0]) & table.p_holm_20.notna()]
            if not sub.empty:
                ax.plot(sub.chains_per_condition, sub.p_holm_20.clip(lower=1e-12), marker="o", label=model)
        ax.axhline(.05, color="grey", ls="--", label="Adjusted p = .05")
        ax.set(title=endpoint[0], xlabel=f"Chains per condition ({batch.CHAINS} per chat)", ylabel="Holm-adjusted p-value", yscale="log", ylim=(lower, 1.2))
        ax.secondary_xaxis("top", functions=(lambda x: x / batch.CHAINS, lambda x: x * batch.CHAINS)).set_xlabel("Fresh chats")
    axes.flat[-1].axis("off")
    axes.flat[-1].legend(*axes.flat[0].get_legend_handles_labels(), loc="center")
    fig.suptitle("Observed statistical evidence versus accumulated size\nDescriptive prefixes; no stopping or extrapolation at a significance crossing")
    fig.tight_layout()
    save_figure(fig, output, "OBSERVED_ADJUSTED_P_VALUES")


def preserve_previous_report(output, evidence_id):
    """Keep every existing report's bytes before replacing its current view."""
    output = Path(output)
    pointer = output / "RESULTS.json"
    if not pointer.exists():
        return
    previous = json.loads(pointer.read_text(encoding="utf-8"))
    if previous.get("evidence_id") == evidence_id:
        return
    old_id = previous.get("evidence_id") or sha(pointer)[:16]
    archive = output / "history" / old_id
    for path in output.iterdir():
        if path.is_file():
            freeze(archive / path.name, path.read_bytes())


def analyze(root, output):
    verify_manifest(root)
    receipts, eligible = collect(root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    evidence_id = batch.core.digest(receipts)[:16]
    preserve_previous_report(output, evidence_id)
    rows = [row for r in eligible for row in r["outcomes"]]
    pd.DataFrame(rows).to_csv(output / "extracted_results.csv", index=False)
    eligible_sources = {r["source_sha256"] for r in eligible}
    per_chain = []
    for path in sorted((Path(root) / "intake").glob("*/original.json")):
        identity = sha(path)
        if identity in eligible_sources:
            per_chain.extend(chain_metrics(json.loads(path.read_text(encoding="utf-8-sig"))))
            eligible_sources.remove(identity)  # A later review receipt does not duplicate chains.
    pd.DataFrame(per_chain).to_csv(output / "per_chain_results.csv", index=False)
    chain_table = chain_prefix_summary(per_chain)
    chain_table.to_csv(output / "within_response_size_statistics.csv", index=False)
    if not chain_table.empty:
        plot_chain_prefixes(chain_table, output)
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
            ax.set(title=f"{endpoint[0]}: {endpoint[1]}", xlabel=f"Chains per condition ({batch.CHAINS} per chat)", ylabel="Mean paired chat difference")
            ax.secondary_xaxis("top", functions=(lambda x: x / batch.CHAINS, lambda x: x * batch.CHAINS)).set_xlabel("Fresh chats")
        axes.flat[-1].axis("off")
        handles, labels = axes.flat[0].get_legend_handles_labels()
        axes.flat[-1].legend(handles, labels, loc="center")
        fig.suptitle("Observed joint-context model responses — pointwise 95% block bootstrap intervals")
        fig.tight_layout(h_pad=3)
        save_figure(fig, output, "OBSERVED_H1_H4_SWEEP")
        if table.p_holm_20.notna().any():
            plot_p_values(table, output)
    sizes = power_figures(output)
    attempted = {m: len({r.get("batch_id") or r["source_sha256"] for r in receipts if r.get("model") == m}) for m in batch.SLOTS}
    result = dict(study_id=batch.study_id(), evidence_id=evidence_id, received_files=len(receipts), attempted_chats=attempted,
                  eligible_fresh_chat_batches=counts, fixed_target_per_model=MAX_BATCHES,
                  primary_sample_complete=all(n == MAX_BATCHES for n in counts.values()),
                  observations=estimates, planning=sizes, api_calls=0,
                  chain_prefixes=list(CHAIN_PREFIXES), chat_prefixes=list(PREFIXES),
                  chains_per_condition_per_chat=batch.CHAINS, within_response_statistics_are_descriptive=True)
    (output / "RESULTS.json").write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    lines = ["# H1–H4: larger sample and statistics versus size", "",
        f"1. Each model response now contains {batch.CHAINS} chains per condition: 150 chain instances, 600 fictional roles, 14,400 weekly orders and 2,400 final probe choices. Four initial responses give 600 chain instances.",
        f"2. Reviewed fresh-chat batches: {counts}. Target: 40 attempts per model; maximum 2,000 chains per condition / 6,000 total instances per model.",
        "3. Within-response plots use the first 5/10/20/30/40/50 chains: means only, no independent-chain p-values. Across-chat plots use 50/100/250/500/1,000/2,000 chains per condition (1/2/5/10/20/40 fresh chats): effects, pointwise 95% intervals and Holm-adjusted p-values.",
        "4. No new model data were created by enlarging the prompt. Actual plots require returned results; the available power figure is assumption-based planning only.",
        "5. All conditions share a context, allowing education carryover. This tests AI review opportunities; human binding time and isolated education effects remain unverified.", "",
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
        if table.p_holm_20.notna().any():
            lines += ["[Adjusted p-values versus size](OBSERVED_ADJUSTED_P_VALUES.png)", ""]
        for model in batch.SLOTS:
            if counts[model]:
                lines += [f"[{model}: 5 to 50 chains within each response](WITHIN_RESPONSE_SIZE_{model}.png)", ""]
    else:
        lines += ["No new model responses have been collected for this version. An observed significance curve will appear after eligible results arrive.", ""]
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    return result
