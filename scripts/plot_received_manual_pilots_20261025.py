"""Replay received MW3 development pilots and export descriptive figures.

Run from the repository root with the project environment:
    .venv/Scripts/python.exe scripts/plot_received_manual_pilots_20261025.py

This reads the three original exports without editing them. It makes no API
calls. Arithmetic replay cannot authenticate how the model chose its orders.
There is only one matched development block; no inference is performed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from statistics import mean, variance
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.manual_weekly_v3 import WebsiteGame, audit_export, digest


EXPERIMENT = ROOT / "experiments/13_weekly_state_api_20261021"
STUDY = EXPERIMENT / "data/manual_v3_3e5479b5ae2ffc96"
MANIFEST = STUDY / "manifest.json"
OUTPUT = EXPERIMENT / "reports/manual_pilot_review_20261025/figures"
INPUTS = {
    "A": STUDY / "chat_runs/MW3_PILOT_A_20261025/MW3_PILOT_A.json",
    "B": EXPERIMENT / "data/manual_v3_chat_MW3_PILOT_B_20261025/MW3_PILOT_B.json",
    "C": EXPERIMENT / "data/manual_chat_20261025_MW3_PILOT_C_source_exposure/MW3_PILOT_C.json",
}
COLORS = {"A": "#2454ce", "B": "#82a8e9", "C": "#263f70"}
BLUE, DARK, GREY = "#2454ce", "#21324c", "#58677b"
ARMS = {
    "A": "A: two opportunities / control",
    "B": "B: one opportunity / control",
    "C": "C*: one opportunity / causal education",
}
MODEL = "GPT-6 Astra / ultra (user-reported)"
STATUS = "Development pilots | descriptive | one matched block"
SOURCE_EXPOSURE = "C: source exposure reported"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def replay_rows(payload):
    """Use the frozen controller to replay the received literal choices only."""
    recorded = payload["model_metadata"]
    game = WebsiteGame(payload["case_id"], payload["arm"], payload["replicate"], payload["chains"],
                       seed=payload["seed"], study_id=payload["study_id"],
                       provider=recorded["provider"], model=recorded["model"],
                       reasoning_setting=recorded["reasoning_setting"])
    for initial, final in zip(payload["initial_orders"], payload["final_orders"]):
        game.display()
        game.submit_initial(dict(zip(game.chain_ids, initial)))
        if payload["arm"] == "A":
            game.display()
            game.submit_revision(dict(zip(game.chain_ids, final)))
    return game.rows


def collect():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    protected = [MANIFEST, MANIFEST.with_suffix(".sha256"), *INPUTS.values()]
    sources = {}
    for name, expected in manifest["source_hashes"].items():
        current = ROOT / "src/beergame_study" / name
        actual = sha(current)
        if actual != expected:
            raise ValueError(f"Frozen source hash differs: {name}")
        sources[name] = {"path": rel(current), "expected_sha256": expected, "actual_sha256": actual}
        protected.append(current)
    controller = EXPERIMENT / "prompts/manual_v3_3e5479b5ae2ffc96/beergame_controller.py"
    if sha(controller) != manifest["controller_source_sha256"]:
        raise ValueError("Uploaded controller differs from the frozen manifest")
    protected.append(controller)
    manifest_hash = MANIFEST.with_suffix(".sha256").read_text(encoding="utf-8").strip()
    if manifest_hash != digest(manifest):
        raise ValueError("Canonical JSON digest does not match manifest.sha256")
    before = {rel(path): sha(path) for path in protected}
    results, states, chain_metrics = [], [], []
    for arm, path in INPUTS.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        prepared = next(case for case in manifest["cases"] if case["case_id"] == f"MW3_PILOT_{arm}")
        expected_case = {key: prepared[key] for key in ("case_id", "arm", "replicate", "chains", "seed")}
        expected_case["study_id"] = manifest["study_id"]
        outcome = audit_export(payload, expected_case=expected_case,
                               expected_source_sha256=manifest["controller_source_sha256"])
        if not payload["complete"] or not outcome["probe_complete"] or outcome["weeks"] != 24:
            raise ValueError(f"Incomplete pilot: {arm}")
        outcome.update(displayed_model_user_reported=MODEL,
                       status=STATUS, source_exposure_reported=arm == "C",
                       arithmetic_replay_passed=True,
                       interpretation="Development observation; no independent replication inference")
        results.append(outcome)
        rows = replay_rows(payload)
        for row in rows:
            row = row.copy()
            row.update(arm=arm, case_id=payload["case_id"], source_exposure_reported=arm == "C")
            # Shared nested inventory is already encoded in the original data;
            # the plotting table stores only the fields that underlie figures.
            row.pop("shared_inventory", None)
            states.append(row)
        for index, cid in enumerate(payload["chain_ids"]):
            own = [row for row in rows if row["chain_id"] == cid]
            demand_variance = variance([week[index] for week in payload["realized_customer_demand"]])
            role_variances = [variance([row["order"] for row in own if row["role"] == role])
                              for role in ("retailer", "wholesaler", "distributor", "factory")]
            chain_metrics.append(dict(arm=arm, chain_id=cid,
                                      cumulative_holding_backlog_cost=sum(row["cost"] for row in own),
                                      mean_role_order_variance=mean(role_variances),
                                      customer_demand_variance=demand_variance,
                                      mean_role_bullwhip=mean(role_variances) / demand_variance,
                                      source_exposure_reported=arm == "C",
                                      independence="Dependent chains within one chat/arm"))
        if len(rows) != 24 * 4 * 10:
            raise ValueError(f"Unexpected replay row count: {arm}")
    results = pd.DataFrame(results)
    states = pd.DataFrame(states)
    chains = pd.DataFrame(chain_metrics)
    weekly = states.groupby(["arm", "week"], as_index=False).agg(
        cluster_weekly_cost=("cost", "sum"), state_rows=("cost", "size"))
    weekly["mean_chain_weekly_cost"] = weekly["cluster_weekly_cost"] / 10
    weekly["mean_chain_cumulative_cost"] = weekly.groupby("arm")["mean_chain_weekly_cost"].cumsum()
    for arm in INPUTS:
        observed = results.loc[results.arm == arm].iloc[0]
        last = weekly.loc[weekly.arm == arm, "mean_chain_cumulative_cost"].iloc[-1]
        if not np.isclose(last, observed.chain_total_cost):
            raise ValueError("Weekly cost accumulation does not match strict audit")
        for column in ("mean_role_order_variance", "mean_role_bullwhip"):
            if not np.isclose(chains.loc[chains.arm == arm, column].mean(), observed[column]):
                raise ValueError(f"Chain calculation differs: {arm}, {column}")
    # All three arms use the same prepared demand/profile block. This is not
    # three independent blocks or thirty independent model replications.
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS.values()]
    for field in ("realized_customer_demand", "profile_ids", "replicate", "seed", "chain_ids"):
        if not all(item[field] == payloads[0][field] for item in payloads):
            raise ValueError(f"Matched-block field differs: {field}")
    return results, states, chains, weekly, before, sources, manifest


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12, "axes.titlesize": 16,
        "axes.labelsize": 12, "text.color": DARK, "axes.labelcolor": DARK,
        "xtick.color": GREY, "ytick.color": DARK, "axes.edgecolor": "#cdd6e5",
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "pdf.fonttype": 42, "svg.fonttype": "none",
    })


def heading(fig, title):
    fig.text(.06, .965, title, fontsize=24, color=BLUE, fontweight="bold", va="top")
    fig.text(.06, .914, STATUS, fontsize=12, color=DARK, va="top")
    fig.text(.06, .877, MODEL + " | " + SOURCE_EXPOSURE, fontsize=10.5, color=GREY, va="top")


def footer(fig):
    fig.text(.06, .070, "* C: source exposure reported. Ten dependent chains per chat; one matched development block, not 30 independent AI replications.",
             fontsize=9.5, color=GREY)
    fig.text(.06, .037, "One versus two decision opportunities is not a verified binding deadline. Replay checks arithmetic, not transcript adherence.",
             fontsize=9.5, color=GREY)


def save(fig, name):
    for extension in ("png", "pdf", "svg"):
        fig.savefig(OUTPUT / f"{name}.{extension}", dpi=220)
    plt.close(fig)


def plot_outcomes(results):
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.subplots_adjust(left=.09, right=.96, bottom=.20, top=.79, hspace=.64, wspace=.27)
    heading(fig, "Received website pilots: outcomes")
    metrics = [
        ("pipeline_sensitivity", "Pipeline sensitivity", "Order reduction / extra pipeline case", ".3f"),
        ("chain_total_cost", "24-week holding + backlog cost", "Mean cost per chain (game $)", ",.2f"),
        ("mean_role_order_variance", "Individual order variation", "Mean order variance (cases²)", ".2f"),
        ("mean_role_bullwhip", "Bullwhip ratio", "Mean order variance / demand variance", ".3f"),
    ]
    ordered = results.set_index("arm").loc[list(INPUTS)]
    x = np.arange(3)
    for ax, (column, title, ylabel, number_format) in zip(axes.ravel(), metrics):
        values = ordered[column].to_numpy(dtype=float)
        bars = ax.bar(x, values, width=.56, color=list(COLORS.values()), edgecolor="white", zorder=3)
        bars[2].set_hatch("///")
        ax.set_title(title, loc="left", pad=16, fontweight="bold")
        ax.set_xticks(x, ["A · control\n2 opportunities", "B · control\n1 opportunity", "C* · education\n1 opportunity"])
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", color="#dbe3f0", alpha=.65, zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(length=0, pad=7)
        ax.yaxis.set_major_locator(MaxNLocator(5))
        high = max(values.max(), .01)
        ax.set_ylim(0, high * 1.27)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + high * .045,
                    format(value, number_format), ha="center", va="bottom", fontsize=13, fontweight="bold")
    footer(fig)
    save(fig, "01_pilot_outcomes")


def plot_cost(weekly):
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=.10, right=.96, bottom=.20, top=.77)
    heading(fig, "Received website pilots: cost through the game")
    for arm in INPUTS:
        own = weekly[weekly.arm == arm]
        final = own.mean_chain_cumulative_cost.iloc[-1]
        ax.plot(own.week, own.mean_chain_cumulative_cost, color=COLORS[arm], lw=2.6,
                linestyle="--" if arm == "C" else "-", marker="o" if arm != "C" else "s",
                markersize=4, markevery=3,
                label=f"{ARMS[arm]}  |  week 24: {final:,.2f}")
    ax.set_xlim(1, 24)
    ax.set_ylim(bottom=0)
    ax.set_xticks([1, 4, 8, 12, 16, 20, 24])
    ax.set_xlabel("Decision week", labelpad=10)
    ax.set_ylabel("Mean cumulative holding + backlog cost per chain (game $)", labelpad=11)
    ax.tick_params(length=0, pad=8)
    ax.grid(color="#dbe3f0", alpha=.60)
    ax.legend(loc="upper left", frameon=False, fontsize=11, labelspacing=.9)
    footer(fig)
    save(fig, "02_pilot_cumulative_cost")


def main():
    results, states, chains, weekly, before, sources, manifest = collect()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, frame in (("arm_outcomes.csv", results), ("weekly_cost.csv", weekly),
                        ("chain_metrics.csv", chains), ("replayed_state_rows.csv", states)):
        frame.to_csv(OUTPUT / name, index=False, encoding="utf-8", lineterminator="\n")
    style()
    plot_outcomes(results)
    plot_cost(weekly)
    (OUTPUT / "CAPTIONS.md").write_text(
        "# Development pilot figures\n\n"
        "1. **Outcomes.** All three pilots have pipeline sensitivity 1.000. Cost, order variation and bullwhip are descriptive averages of the received decisions. C has reported source exposure and cannot establish an education effect.\n\n"
        "2. **Cumulative cost.** Mean holding plus backlog cost through 24 weeks for the same prepared demand block. The three chats are one matched development block; no p-values or confidence intervals are estimated.\n\n"
        "Model: GPT-6 Astra / ultra, user-reported. A has two decision opportunities and a control reading; B has one opportunity and the control; C has one opportunity and causal education. Opportunity count is not a verified binding deadline.\n",
        encoding="utf-8")
    after = {name: sha(ROOT / name) for name in before}
    if after != before:
        raise ValueError("An input or frozen file changed during plotting")
    outputs = {path.name: sha(path) for path in sorted(OUTPUT.iterdir())
               if path.is_file() and path.name != "VALIDATION.json"}
    write_json(OUTPUT / "VALIDATION.json", dict(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        script=rel(Path(__file__).resolve()), script_sha256=sha(Path(__file__).resolve()),
        api_calls=0, original_files_modified=False, protected_hashes_unchanged=after == before,
        study_id=manifest["study_id"], protocol=manifest["protocol"],
        source_hash_verification=sources, protected_inputs_sha256=before,
        frozen_manifest_bytes_sha256=sha(MANIFEST), frozen_manifest_canonical_json_sha256=digest(manifest),
        arithmetic_audit_passed_cases=results.case_id.tolist(),
        model_metadata={"displayed_label_user_reported": "gpt 6 astra ultra",
                        "provider_api_identifier": None, "raw_export_metadata_preserved": True},
        completed_weeks_per_arm=24, chains_per_chat=10, matched_development_blocks=1,
        replay_state_rows=len(states), education_arm_source_exposure_reported=True,
        transcript_authenticated=False, inference="Descriptive only; no p-values or confidence intervals",
        outcome_definitions={
            "pipeline_sensitivity": "Mean (order with pipeline 8 - order with pipeline 32) / 24 across matched probe cases",
            "chain_total_cost": "Mean across ten chains of sum over 24 weeks/four roles of .5*inventory + backlog",
            "mean_role_order_variance": "Mean of 40 role-wise sample variances of the 24 weekly orders",
            "mean_role_bullwhip": "Mean of 40 role-wise order variances divided by own chain customer-demand sample variance",
        },
        artifact_sha256=outputs))
    print(results[["arm", "pipeline_sensitivity", "chain_total_cost", "mean_role_order_variance", "mean_role_bullwhip"]].to_string(index=False))
    print("Wrote descriptive figures and tables to " + str(OUTPUT))
    print("Strict replay passed for all three exports; all protected hashes unchanged; no API calls.")


if __name__ == "__main__":
    main()
