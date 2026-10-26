"""Make presentation figures from the CLOSED experiment-13 CSVs; no API calls.

Run from the repository root:
    python scripts/plot_weekly_review_20261025.py

Observed comparisons remain descriptive. The separate power panel is an
analytic planning calculation, never an estimate from generated student rows.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, PercentFormatter
import numpy as np
import pandas as pd
from scipy.stats import nct, t


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/13_weekly_state_api_20261021"
SOURCE = EXPERIMENT / "analysis/weekly_api_c64d75aa3a03356f/b34972b65bf5"
OUTPUT = EXPERIMENT / "reports/review_20261025"
FIGURES = OUTPUT / "figures"
MODELS = ["gpt-6-luna", "gpt-5.6-luna", "gpt-5.6-sol", "claude-haiku-5-5"]
LABELS = ["GPT-6 Luna", "GPT-5.6 Luna", "GPT-5.6 Sol", "Claude Haiku 5.5"]
COLORS = ["#214fc7", "#547ee0", "#0c2d73", "#72a7d9"]
BLUE = "#2455d3"
DARK = "#21324c"
GREY = "#58677b"
PALE = "#e8effc"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12, "axes.titlesize": 15,
        "axes.labelsize": 12, "text.color": DARK, "axes.labelcolor": DARK,
        "xtick.color": GREY, "ytick.color": DARK, "axes.edgecolor": "#ccd6e5",
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "pdf.fonttype": 42,
        "svg.fonttype": "none", "axes.unicode_minus": True,
    })


def heading(fig, title, subtitle) -> None:
    fig.text(.055, .958, title, fontsize=23, fontweight="bold", color=BLUE, va="top")
    fig.text(.055, .892, subtitle, fontsize=11.5, color=GREY, va="top")


def save(fig, stem) -> None:
    for extension in ("png", "pdf", "svg"):
        fig.savefig(FIGURES / f"{stem}.{extension}", dpi=240)
    plt.close(fig)


def simple_axes(ax) -> None:
    ax.grid(axis="x", alpha=.45, color="#dbe3f0", linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.spines["left"].set_visible(False)


def plot_contrasts(observed) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14.2, 6.1))
    fig.subplots_adjust(left=.18, right=.95, bottom=.23, top=.73, wspace=.48)
    heading(fig, "Pressure framing: four-model comparison", 
            "Observed feasibility pretest | 20 fictional chains per model | 24 decision weeks | descriptive")
    y = np.arange(4)
    for ax, hypothesis in zip(axes, ("H1", "H2")):
        own = observed[observed.hypothesis == hypothesis].set_index("model").loc[MODELS]
        values = own.mean_strong_minus_no.to_numpy()
        ax.barh(y, values, height=.54, color=COLORS)
        ax.scatter(np.zeros(sum(values == 0)), y[values == 0], color=np.array(COLORS)[values == 0],
                   s=45, zorder=4, clip_on=False)
        ax.axvline(0, color=GREY, lw=1)
        ax.set_yticks(y, LABELS)
        ax.invert_yaxis()
        simple_axes(ax)
        if hypothesis == "H1":
            ax.set_title("H1  Pipeline-sensitivity proxy", loc="left", pad=17)
            ax.set_xlim(-.019, .0055)
            ax.set_xlabel("Strong − no pressure (response per case)")
            for j, value in enumerate(values):
                ax.annotate(f"{value:+.4f}", (value, j), xytext=(-8 if value < 0 else 8, 0),
                            textcoords="offset points", ha="right" if value < 0 else "left",
                            va="center", fontsize=11, fontweight="bold")
        else:
            ax.set_title("H2  Cumulative chain cost", loc="left", pad=17)
            ax.set_xlim(-28, 28)
            ax.set_xlabel("Strong − no pressure (game dollars)")
            for j, value in enumerate(values):
                ax.annotate(f"{value:+.2f}", (value, j), xytext=(-8 if value < 0 else 8, 0),
                            textcoords="offset points", ha="right" if value < 0 else "left",
                            va="center", fontsize=11, fontweight="bold")
    fig.text(.055, .113, "Negative H1 and positive H2 follow the predicted proxy directions; zero and opposite results are retained.",
             fontsize=11, color=DARK)
    fig.text(.055, .060, "Imagined pressure; coupled generation. No independent-chain inference, p-values or confidence intervals. Education (H3/H4) was not tested.",
             fontsize=10, color=GREY)
    save(fig, "01_observed_model_comparison")


def prefix_table(contrasts):
    rows = []
    for model in MODELS:
        for hypothesis in ("H1", "H2"):
            own = contrasts[(contrasts.model == model) & (contrasts.hypothesis == hypothesis)].sort_values("block")
            assert own.block.tolist() == list(range(10))
            for pairs in (5, 10):
                prefix = own.iloc[:pairs]
                rows.append({"model": model, "hypothesis": hypothesis,
                             "total_chains": pairs * 2, "matched_pairs": pairs,
                             "blocks_included": ",".join(str(x) for x in prefix.block),
                             "mean_strong_minus_no": prefix.difference.mean(),
                             "inference": "Descriptive prefix of one coupled generation; not independent replications"})
    return pd.DataFrame(rows)


def plot_prefix(prefix):
    fig, axes = plt.subplots(1, 2, figsize=(14.2, 6.2))
    fig.subplots_adjust(left=.09, right=.95, top=.73, bottom=.31, wspace=.27)
    heading(fig, "Including more saved chains changes the descriptive estimate",
            "Observed prefix check | 10 total chains = 5 matched pairs; 20 total chains = 10 matched pairs")
    markers = ["o", "s", "D", "^"]
    for ax, hypothesis in zip(axes, ("H1", "H2")):
        for i, model in enumerate(MODELS):
            own = prefix[(prefix.model == model) & (prefix.hypothesis == hypothesis)]
            ax.plot(own.total_chains, own.mean_strong_minus_no, color=COLORS[i],
                    marker=markers[i], markersize=9 if i == 0 else 6, lw=2,
                    markerfacecolor="white" if i == 0 else COLORS[i],
                    linestyle="--" if i == 0 else "-", label=LABELS[i], zorder=6-i)
        ax.axhline(0, color=GREY, lw=.9)
        ax.set_xticks([10, 20])
        ax.set_xlim(8, 22)
        ax.set_xlabel("Total saved chains included (both conditions)")
        ax.set_ylabel("Pipeline-sensitivity difference" if hypothesis == "H1" else "Cumulative-cost difference (game dollars)")
        ax.set_title(f"{hypothesis}: strong − no pressure", loc="left", pad=14)
        ax.grid(alpha=.35, color="#dbe3f0")
        ax.tick_params(length=0, pad=7)
        ax.yaxis.set_major_locator(MaxNLocator(5))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.5, .15), ncol=4,
               frameon=False, fontsize=11)
    fig.text(.055, .105, "First 5 / all 10 matched blocks, sorted by frozen block ID. GPT-6 Luna and Sol coincide at zero.", fontsize=11)
    fig.text(.055, .055, "Prefixes reuse the same responses. More fictional chains do not create independent AI replications or validate a binding-time effect.",
             fontsize=10, color=GREY)
    save(fig, "02_observed_10_vs_20_chains")


def power_table():
    rows = []
    # Two-sided paired t test: under the stated normality assumption, the
    # statistic has df=n-1 and noncentrality dz*sqrt(n). alpha=.01 is .05/5.
    for n in (10, 20, 40):
        critical = t.ppf(1 - .01 / 2, n - 1)
        for dz in (.3, .5, .8):
            power = nct.sf(critical, n - 1, dz * np.sqrt(n)) + nct.cdf(-critical, n - 1, dz * np.sqrt(n))
            rows.append({"independent_matched_three_arm_blocks": n,
                         "arm_runs_per_model": 3 * n, "standardized_paired_effect_dz": dz,
                         "two_sided_alpha_per_endpoint": .01,
                         "endpoints_in_per_model_family": 5, "assumed_power": float(power),
                         "assumption": "Independent normal block contrasts; fixed n; per-model five-endpoint Bonferroni family only; not an observed effect or guarantee"})
    return pd.DataFrame(rows)


def plot_power(planning):
    fig, ax = plt.subplots(figsize=(12.4, 6.2))
    fig.subplots_adjust(left=.10, right=.96, top=.74, bottom=.28)
    heading(fig, "Planning only: power needs independent replications",
            "Prospective assumption calculation | three arms per block | no observed effects used")
    for dz, color, label in zip((.3, .5, .8), ("#82aae7", "#4375d5", "#12368c"),
                               ("Assumed d_z = 0.3", "Assumed d_z = 0.5", "Assumed d_z = 0.8")):
        own = planning[planning.standardized_paired_effect_dz == dz]
        ax.plot(own.independent_matched_three_arm_blocks, own.assumed_power, marker="o",
                lw=2.5, ms=7, color=color, label=label)
    ax.axhline(.8, color=GREY, ls="--", lw=1)
    ax.text(40.5, .8, "80%", va="center", fontsize=10, color=GREY)
    ax.set_xticks([10, 20, 40], ["10 blocks\n30 arm runs", "20 blocks\n60 arm runs", "40 blocks\n120 arm runs"])
    ax.set_xlabel("Independent matched three-arm blocks / arm runs per model", labelpad=10)
    ax.set_ylabel("Power under the stated assumptions")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylim(0, 1.03)
    ax.set_xlim(8, 44)
    ax.grid(alpha=.35, color="#dbe3f0")
    ax.tick_params(length=0, pad=7)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.04), ncol=3, frameon=False, fontsize=11)
    fig.text(.055, .100, "Two-sided paired t test; α = .01 per endpoint (.05 / 5), normal independent block contrasts; fixed sample size.", fontsize=10.5)
    fig.text(.055, .052, "d_z = mean paired difference / SD of paired differences. Per-model family only; four-model confirmation needs additional multiplicity control.",
             fontsize=9.5, color=GREY)
    save(fig, "03_prospective_power_assumptions")


def plot_results_slide(observed):
    """Standalone 16:9 result page matching the blank slide's white/blue style."""
    fig = plt.figure(figsize=(16, 9))
    fig.text(.055, .925, "Results", color=BLUE, fontsize=30, fontweight="bold")
    fig.text(.055, .868, "AI feasibility pretest | descriptive", color=DARK, fontsize=19, fontweight="bold")
    fig.add_artist(plt.Line2D([.65, 1], [.962, .962], transform=fig.transFigure, color=BLUE, lw=1))
    fig.add_artist(plt.Line2D([0, 1], [.055, .055], transform=fig.transFigure, color=BLUE, lw=1))
    fig.text(.055, .814, "4 models • 20 fictional chains/model • 24 weeks • 104/104 responses accepted", color=GREY, fontsize=15)
    ax = fig.add_axes([.075, .337, .85, .40])
    ax.set_axis_off()
    cells = []
    for model, label in zip(MODELS, LABELS):
        own = observed[observed.model == model].set_index("hypothesis")
        cells.append([label, f"{own.loc['H1','mean_strong_minus_no']:+.4f}", f"{own.loc['H2','mean_strong_minus_no']:+.2f}"])
    table = ax.table(cellText=cells, colLabels=["Model", "H1: pipeline-proxy difference", "H2: cost difference"],
                     cellLoc="left", colLoc="left", bbox=[0, 0, 1, 1], colWidths=[.36, .34, .30])
    table.auto_set_font_size(False)
    table.set_fontsize(16)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("white")
        cell.PAD = .07
        if row == 0:
            cell.set_facecolor(BLUE)
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor(PALE if row % 2 else "#f5f8fe")
            cell.set_text_props(color=DARK)
    fig.text(.075, .274, "All differences = strong − no pressure. H1: lower follows prediction; H2: higher follows prediction.", fontsize=14)
    fig.text(.075, .209, "Two models had identical outcomes across the pressure conditions.", fontsize=17, color=BLUE, fontweight="bold")
    fig.text(.075, .150, "No enforced time restriction; chains generated jointly. H3/H4 education contrasts were not collected.", fontsize=13, color=GREY)
    fig.text(.075, .106, "These results do not establish statistical significance or human decision-time effects.", fontsize=13, color=GREY)
    save(fig, "04_presentation_results_slide")


def main():
    style()
    FIGURES.mkdir(parents=True, exist_ok=True)
    source_files = [SOURCE / name for name in ("hypotheses.csv", "contrasts.csv", "chains.csv")]
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in source_files}
    observed = pd.read_csv(SOURCE / "hypotheses.csv")
    contrasts = pd.read_csv(SOURCE / "contrasts.csv")
    chains = pd.read_csv(SOURCE / "chains.csv")
    assert len(observed) == 8 and len(contrasts) == 80 and len(chains) == 80
    assert set(observed.model) == set(MODELS)
    assert not observed.inference_available.any()
    assert (chains.weeks_observed == 24).all() and chains.complete.all()
    assert observed[["p_raw", "p_holm_8", "paired_bootstrap_95"]].isna().all().all()
    computed = contrasts.groupby(["model", "hypothesis"]).difference.mean()
    for row in observed.itertuples():
        assert np.isclose(computed.loc[row.model, row.hypothesis], row.mean_strong_minus_no, rtol=0, atol=1e-12)
    prefix = prefix_table(contrasts)
    planning = power_table()
    observed.to_csv(FIGURES / "observed_model_comparison.csv", index=False)
    prefix.to_csv(FIGURES / "observed_prefix_10_20_chains.csv", index=False)
    planning.to_csv(FIGURES / "prospective_power_assumptions.csv", index=False)
    plot_contrasts(observed)
    plot_prefix(prefix)
    plot_power(planning)
    plot_results_slide(observed)
    assert all(sha(ROOT / p) == expected for p, expected in source_hashes.items())
    receipt = {"created_for": "2026-10-25 review", "study_id": "weekly_api_c64d75aa3a03356f",
               "source_report_version": "b34972b65bf5", "source_hashes_unchanged": source_hashes,
               "observed_rows": {"hypothesis_rows": len(observed), "chain_rows": len(chains),
                                 "paired_contrast_rows": len(contrasts), "prefix_rows": len(prefix)},
               "observed_inference_available": False, "api_calls": 0,
               "planning_is_not_observed_data": True,
               "planning": {"test": "two-sided noncentral paired t", "alpha_per_endpoint": .01,
                            "family": "Five endpoints within one model, not across four models",
                            "independent_blocks": [10, 20, 40], "assumed_dz": [.3, .5, .8]},
               "artifacts": {str(p.relative_to(OUTPUT)): sha(p) for p in sorted(FIGURES.iterdir()) if p.is_file()}}
    (OUTPUT / "FIGURE_VALIDATION.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "figures": 4, "formats_each": ["png", "pdf", "svg"],
                      "plot_tables": 3, "source_hashes_unchanged": True, "api_calls": 0}, indent=2))


if __name__ == "__main__":
    main()
