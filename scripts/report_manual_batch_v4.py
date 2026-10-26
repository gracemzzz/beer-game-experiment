"""Presentation extension: plot already-computed adjusted p-values, no new tests.

No collection, model calls, extrapolated p-values or change to inference.
"""
from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "experiments/13_weekly_state_api_20261021/reports/four_model_manual"


def render(folder=REPORT):
    folder = Path(folder)
    result = json.loads((folder / "RESULTS.json").read_text(encoding="utf-8"))
    observations = result["observations"]
    if not observations:
        return "No observed significance plot: this version has no reviewed model responses yet."
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    names = ("H1", "H2", "H3", "H4a", "H4b")
    models = list(result["eligible_fresh_chat_batches"])
    for ax, name in zip(axes.flat, names):
        for model in models:
            rows = sorted((r for r in observations if r["model"] == model and r["hypothesis"] == name
                           and r["p_holm_20"] is not None), key=lambda r: r["prefix_chats"])
            if rows:
                ax.plot([r["chains_per_condition"] for r in rows],
                        [-math.log10(max(r["p_holm_20"], 1e-12)) for r in rows], marker="o", label=model)
        ax.axhline(-math.log10(.05), color="grey", ls="--", label="Adjusted p = .05")
        ax.set(title=name, xlabel="Chains per condition (10 per chat)", ylabel="−log10(Holm-adjusted p)", ylim=(0, None))
    axes.flat[-1].axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    axes.flat[-1].legend(handles, labels, loc="center")
    fig.suptitle("Observed evidence as fresh chats accumulate — descriptive prefixes, no stopping rule")
    fig.text(.02, .01, "A line crossing is not confirmation: direction, full planned collection and design limitations still apply. No extrapolation.", fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, .96))
    for ext in ("png", "pdf", "svg"):
        fig.savefig(folder / f"OBSERVED_ADJUSTED_P_VALUES.{ext}", dpi=220)
    plt.close(fig)
    lines = ["# H1–H4: observed evidence", "",
             "1. These are model-response comparisons within a shared chat context, not verified human deadline effects.",
             "2. Prefix p-values describe accumulation; they do not authorize stopping or further sampling until significance.",
             "3. H4 needs both components in the predicted direction. Small p-values in the opposite direction do not support a hypothesis.", "",
             "| Model | Endpoint | Chats | Chains/condition | Difference | Adjusted p | Status |",
             "|---|---|---:|---:|---:|---:|---|"]
    for model in models:
        for name in names:
            rows = [r for r in observations if r["model"] == model and r["hypothesis"] == name]
            if not rows:
                continue
            r = max(rows, key=lambda row: row["prefix_chats"])
            p = r["p_holm_20"]
            right = r["mean_difference"] * r["expected_direction"] > 0
            status = "Interim; not established"
            if result["primary_sample_complete"]:
                status = "Supported for this AI analogue" if p is not None and p < .05 and right else "Not supported"
            p_text = "unavailable" if p is None else f"{p:.6g}"
            lines.append(f"| {model} | {name} | {r['prefix_chats']} | {r['chains_per_condition']} | {r['mean_difference']:.6g} | {p_text} | {status} |")
    lines += ["", "[Observed effects](OBSERVED_H1_H4_SWEEP.png) · [Observed adjusted p-values](OBSERVED_ADJUSTED_P_VALUES.png) · [Methods](REPORT.md)", ""]
    (folder / "OBSERVED_FINDINGS.md").write_text("\n".join(lines), encoding="utf-8")
    return str(folder / "OBSERVED_FINDINGS.md")


if __name__ == "__main__":
    print(render())
