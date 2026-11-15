"""Add measured-value plots for the two control-reading conditions only.

Existing reports, plots, tables, statistical tests and raw records are read-only.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import shutil
import statistics as st
import sys
import textwrap
from exp14_slide_labels import hypothesis_heading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_publication import EXPERIMENT, read, sha, verify_preservation

REPORTS = EXPERIMENT / "reports"
DESTINATION = REPORTS / "figures/control_reading_only"
CONDITIONS = {"A": "120 seconds + control reading", "B": "8 seconds + control reading"}
COLORS = {"A": "#24628A", "B": "#C16C25"}
INTERVAL_METHOD = "Pointwise 95% Student t interval for a condition mean: mean ± t(0.975, n−1) × SD / sqrt(n)."
METRICS = [
    ("pipeline_sensitivity", "Pipeline response", "Order reduction per extra\noutstanding case", 6,
     "Within each chain, average the 8 matched probe slopes: (order with low outstanding replenishment − order with high outstanding replenishment) / increase in outstanding cases. Then average 10 chains.",
     "Pipeline underweighting—measured using the response proxy.\nProxy per chain = mean of 8 slopes (order decrease / extra outstanding case)."),
    ("chain_total_cost", "Total holding and backlog cost", "24-week holding and backlog cost\n(game cost units / chain)", 2,
     "Sum (0.5 × remaining inventory + 1 × unfilled demand) across all 4 roles and 24 weeks for each chain. Then average 10 chain totals.",
     "Total holding and backlog cost = sum of\n(0.5 × inventory + backlog) over 4 roles × 24 weeks."),
    ("complete_holding_cost", "Inventory-holding cost", "24-week holding cost\n(game cost units / chain)", 2,
     "Sum 0.5 × remaining inventory across all 4 roles and 24 weeks for each chain. Then average 10 chain totals.",
     "Holding cost = sum of 0.5 × inventory\nover 4 roles × 24 weeks, per chain."),
    ("complete_backlog_cost", "Backlog cost", "24-week backlog cost\n(game cost units / chain)", 2,
     "Sum 1 × unfilled demand across all 4 roles and 24 weeks for each chain. Then average 10 chain totals.",
     "Backlog cost = sum of 1 × unfilled demand\nover 4 roles × 24 weeks, per chain."),
    ("mean_role_order_variance", "Weekly order variance", "Mean within-role\norder variance (cases²)", 4,
     "For each role, calculate sample variance of its 24 weekly orders: sum of squared deviations from that role's mean divided by 23. Average the 4 role variances, then average 10 chains.",
     "Order variance = mean of 4 role sample variances;\neach uses 24 weekly orders and divisor 23."),
    ("mean_role_bullwhip", "Bullwhip ratio", "Order / consumer-demand\nvariance ratio (unitless)", 4,
     "Within each chain, divide each role's 24-week sample order variance by that chain's 24-week sample final-consumer-demand variance. Average its 4 role ratios, then average 10 chains. Do not divide pooled means.",
     "Bullwhip = mean of 4 role order variances divided\nby their own chain's final-consumer-demand variance."),
]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, records):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def check_existing(publication):
    for name, expected in publication["artifacts"].items():
        if sha(REPORTS / name) != expected:
            raise ValueError("Existing publication changed: " + name)


def main():
    publication = read(REPORTS / "PUBLICATION.json")
    check_existing(publication)
    preservation = verify_preservation(EXPERIMENT)
    sources = [Path(__file__), Path(__file__).with_name("exp14_slide_labels.py"), EXPERIMENT / "hypotheses/STUDENT_FRAMING_V3.md", REPORTS / "PUBLICATION.json", REPORTS / "tables/CHAIN_VALUES.csv",
               REPORTS / "tables/ALL_MEASURED_VALUES.csv", REPORTS / "tables/HYPOTHESIS_COMPARISONS.csv"]
    inputs = {path.relative_to(ROOT).as_posix(): sha(path) for path in sources}
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    manifest = DESTINATION / "MANIFEST.json"
    if manifest.exists():
        old = read(manifest)
        if old["fingerprint"] == fingerprint and all(sha(DESTINATION / p) == h for p, h in old["artifacts"].items()):
            print(json.dumps(dict(folder=str(DESTINATION), cached=True, original_publication_unchanged=True)))
            return
        archive = EXPERIMENT / "archive/publication_versions/control_reading_only" / old["fingerprint"][:16]
        for name in [*old["artifacts"], "MANIFEST.json"]:
            source, target = DESTINATION / name, archive / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and sha(target) != sha(source):
                raise ValueError("Refusing to overwrite archived control-reading figures")
            if not target.exists():
                shutil.copyfile(source, target)

    data = [row for row in rows(REPORTS / "tables/CHAIN_VALUES.csv") if row["arm"] in CONDITIONS]
    summary = {row["variable"]: row for row in rows(REPORTS / "tables/ALL_MEASURED_VALUES.csv")}
    by_block = {(row["block_id"], row["arm"]): row for row in data}
    blocks = sorted({row["block_id"] for row in data})
    if len(data) != 20 or len(blocks) != 10 or len(by_block) != 20:
        raise ValueError("Expected ten complete matched control-reading pairs")
    for block in blocks:
        for arm in CONDITIONS:
            row = by_block[(block, arm)]
            if row["stage"] != "main" or row["complete_24_weeks"] != "True":
                raise ValueError("Incomplete or non-main chain")

    from scipy.stats import t
    n_chains = len(blocks)
    critical_t = float(t.ppf(.975, n_chains - 1))
    point_rows, mean_rows = [], []
    for key, name, ylabel, digits, formula, short_formula in METRICS:
        for arm, condition in CONDITIONS.items():
            values = [float(by_block[(block, arm)][key]) for block in blocks]
            mean = st.mean(values)
            sd = st.stdev(values)
            se = sd / math.sqrt(n_chains)
            margin = critical_t * se
            if not math.isclose(mean, float(summary[key][arm + "_value"]), rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError("Condition mean disagrees with the current report: " + key)
            mean_rows.append(dict(variable=key, measured_quantity=name, arm=arm, condition=condition,
                                  mean=mean, sd_across_chains=sd, se_mean=se,
                                  ci95_half_width=margin, ci95_low=mean-margin, ci95_high=mean+margin,
                                  ci_method=INTERVAL_METHOD, ci_df=n_chains-1, ci_critical_t=critical_t,
                                  minimum=min(values), maximum=max(values),
                                  n_chains=n_chains, units=summary[key]["units"], calculation=formula))
            point_rows.extend(dict(variable=key, measured_quantity=name, arm=arm, condition=condition,
                                   block_id=block, value=float(by_block[(block, arm)][key]), units=summary[key]["units"])
                              for block in blocks)

    # Only these frozen primary tests compare the two displayed conditions.
    tests = {row["metric"]: row for row in rows(REPORTS / "tables/HYPOTHESIS_COMPARISONS.csv")
             if row["contrast"] == "B-A"}
    if {row["hypothesis"] for row in tests.values()} != {"H1", "H2"}:
        raise ValueError("Expected the existing H1/H2 pressure comparisons")
    for key, test in tests.items():
        difference = st.mean(float(by_block[(block, "B")][key])-float(by_block[(block, "A")][key]) for block in blocks)
        if int(test["n_pairs"]) != n_chains or not math.isclose(difference, float(test["mean_difference"]), abs_tol=1e-12):
            raise ValueError("Displayed comparison disagrees with the saved paired test")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch, Rectangle
    from matplotlib.legend_handler import HandlerTuple
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 16,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "svg.hashsalt": "exp14-control-reading-only",
                         "pdf.fonttype": 42})
    means = {(row["variable"], row["arm"]): row["mean"] for row in mean_rows}
    intervals = {(row["variable"], row["arm"]): row for row in mean_rows}
    legend = [Line2D([0], [0], marker="o", color="#9AA6AE", markersize=8, linestyle="none",
                     label="Dot: one chain"),
              (Patch(facecolor="#24628A", alpha=.24),
               Line2D([0], [0], marker="|", color="#24628A", linestyle="none", markersize=18, markeredgewidth=3))]
    legend_labels = ["Dot: one chain", "Band: 95% CI of mean; center mark: mean"]

    def p_label(key):
        if key in tests:
            test = tests[key]
            assert 0 <= float(test['p_holm_family_5']) < .01
            return f"{test['hypothesis']} · p < 0.01 (Holm)"
        return "Descriptive · no planned test"

    def panel(ax, metric, compact=False):
        key, name, ylabel, digits, formula, short_formula = metric
        highest, lowest = 0, 0
        for j, block in enumerate(blocks):
            offset = (j - 4.5) * .012
            yy = [float(by_block[(block, arm)][key]) for arm in CONDITIONS]
            for i, (arm, value) in enumerate(zip(CONDITIONS, yy)):
                ax.scatter([value], [i + .22 + offset], color=COLORS[arm], s=42 if compact else 65,
                           alpha=.65, edgecolors="white", linewidths=.5, zorder=3)
            highest = max(highest, *yy)
        for i, arm in enumerate(CONDITIONS):
            score = intervals[(key, arm)]
            low, high, mean = score["ci95_low"], score["ci95_high"], score["mean"]
            highest, lowest = max(highest, high), min(lowest, low)
            ax.add_patch(Rectangle((low, i-.10), high-low, .20, facecolor=COLORS[arm],
                                   edgecolor=COLORS[arm], alpha=.24, linewidth=1.2, zorder=2))
            ax.vlines(mean, i-.14, i+.14, color=COLORS[arm], linewidth=3.5, zorder=5)
            display_digits = min(digits, 4) if compact else digits
            ax.text(.98, i-.20, f"{mean:.{display_digits}f} ± {score['ci95_half_width']:.{display_digits}f}",
                    transform=ax.get_yaxis_transform(), ha="right", va="bottom", color=COLORS[arm],
                    fontsize=16 if compact else 22, fontweight="bold")
        title = name
        if key == "pipeline_sensitivity":
            title = "Pipeline underweighting"
            ax.text(0, 1.21 if compact else 1.15, "Measured proxy: pipeline response", transform=ax.transAxes,
                    fontsize=14 if compact else 18, color="#455665", va="bottom")
        elif compact and key == "chain_total_cost":
            title = "Total holding and\nbacklog cost"
        ax.set_title(title, loc="left", fontsize=20 if compact else 26, fontweight="bold",
                     pad=(58 if compact else 66) if key == "pipeline_sensitivity" else 38)
        ax.text(0, 1.035, p_label(key), transform=ax.transAxes, fontsize=14 if compact else 18,
                color="#455665", va="bottom")
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["120 seconds\nControl reading", "8 seconds\nControl reading"])
        ax.tick_params(axis="both", labelsize=16 if compact else 22, pad=7)
        if compact and key == "chain_total_cost":
            ylabel = "24-week holding and backlog\ncost (game cost units / chain)"
        ax.set_xlabel(ylabel, fontsize=18 if compact else 22, labelpad=12)
        ax.set_ylabel("Fictional decision allowance", fontsize=18 if compact else 22, labelpad=12)
        ax.set_xlim(min(lowest*1.1, -highest*.02), max(highest*1.08, .01))
        ax.set_ylim(1.5, -.65)
        ax.grid(axis="x", alpha=.16)
        ax.set_axisbelow(True)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        # There are no connections between chains or conditions.
        assert not ax.lines

    DESTINATION.mkdir(parents=True, exist_ok=True)
    write_csv(DESTINATION / "CONDITION_MEANS.csv", mean_rows)
    write_csv(DESTINATION / "CHAIN_VALUES.csv", point_rows)
    write_csv(DESTINATION / "TEST_ANNOTATIONS.csv", list(tests.values()))
    figures, catalog = [], []
    fig = plt.figure(figsize=(16, 9), facecolor="white")
    fig.suptitle("Hypotheses and results", fontsize=30, fontweight="bold", x=.055, ha="left", y=.98)
    fig.text(.055, .915, "10 matched chains · 24 weeks", fontsize=17, color="#455665")
    overview_legend = [Patch(facecolor=COLORS[arm], alpha=.8) for arm in CONDITIONS]
    overview_legend.append((Patch(facecolor="#657887", alpha=.24),
                            Line2D([0], [0], marker="|", color="#657887", linestyle="none",
                                       markersize=18, markeredgewidth=3)))
    fig.legend(handles=overview_legend, labels=["120 s", "8 s", "Mean & 95% CI"],
               handler_map={tuple: HandlerTuple(ndivide=1)}, loc="upper center",
               bbox_to_anchor=(.515, .875), frameon=False, ncol=3, fontsize=16, columnspacing=2)
    short_axes = {"pipeline_sensitivity": "Response proxy (cases/case)",
                  "chain_total_cost": "Cost units / chain", "complete_holding_cost": "Cost units / chain",
                  "complete_backlog_cost": "Cost units / chain", "mean_role_order_variance": "Cases²",
                  "mean_role_bullwhip": "Ratio"}
    primary_predictions = [hypothesis_heading(h) for h in ("H1", "H2")]
    presentation_hypotheses = []
    axes = []
    for index, metric in enumerate(METRICS):
        key, name, _, digits, _, _ = metric
        primary = index < 2
        if primary:
            left = .055 + index*.495
            ax = fig.add_axes([left, .435, .40, .19])
            fig.text(left, .775, primary_predictions[index], fontsize=22, fontweight="bold",
                     color="#172E40", va="top", linespacing=1.15)
            change = (means[(key, 'B')]/means[(key, 'A')]-1)*100
            outcome = "Response" if index == 0 else "Cost"
            result_label = f"{outcome} {change:+.1f}%  ·  Holm p < 0.01".replace('-', '−')
            fig.text(left, .66, result_label, fontsize=18, fontweight="bold", color="#24628A")
            presentation_hypotheses.append(dict(hypothesis=tests[key]['hypothesis'],
                prediction=primary_predictions[index].replace('\n', ' '), result_label=result_label,
                measured_quantity="Pipeline response (proxy)" if index == 0 else name,
                percent_change=change, mean_difference=float(tests[key]['mean_difference']),
                p_holm_family_5=float(tests[key]['p_holm_family_5']),
                comparison="8 s + control reading minus 120 s + control reading"))
        else:
            left = .055 + (index-2)*.24
            ax = fig.add_axes([left, .105, .19, .125])
            ax.set_title(name, loc="left", fontsize=17, fontweight="bold", pad=20)
        axes.append(ax)
        high = max(intervals[(key, arm)]['ci95_high'] for arm in CONDITIONS)
        low = min(0, *(intervals[(key, arm)]['ci95_low'] for arm in CONDITIONS))
        for i, arm in enumerate(CONDITIONS):
            score = intervals[(key, arm)]
            ax.add_patch(Rectangle((score['ci95_low'], i-.11), score['ci95_high']-score['ci95_low'], .22,
                                   facecolor=COLORS[arm], alpha=.26, edgecolor="none"))
            ax.vlines(score['mean'], i-.16, i+.16, color=COLORS[arm], linewidth=3.5)
            label_digits = 4 if key == 'pipeline_sensitivity' else 2
            ax.text(score['mean'], i-.23, f"{score['mean']:.{label_digits}f}", ha="center", va="bottom",
                    color=COLORS[arm], fontsize=19 if primary else 15, fontweight="bold")
        ax.set_xlim(low, high*1.16)
        ax.set_ylim(1.45, -.65)
        ax.set_yticks([])
        ax.set_xlabel(short_axes[key], fontsize=17 if primary else 14, labelpad=9 if primary else 7)
        ax.tick_params(axis='x', labelsize=15 if primary else 13, pad=6)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=4))
        ax.grid(axis='x', alpha=.12)
        ax.set_axisbelow(True)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#9AA6AE')
        assert not ax.lines
    fig.text(.055, .305, "Descriptive outcomes", fontsize=16, color="#455665")
    figures.append(("00_ALL_MEASURED_OUTCOMES", fig))
    catalog.append(dict(file="00_ALL_MEASURED_OUTCOMES", title="Hypotheses and results",
                        variables=[m[0] for m in METRICS], display="H1/H2 prediction and observed percentage change above primary mean/CI panels; four descriptive panels below; shared legend",
                        hypotheses=presentation_hypotheses,
                        axes=[dict(title=primary_predictions[i].replace('\n', ' ') if i<2 else ax.get_title(loc="left"), x_label=ax.get_xlabel(),
                                   y_label="Condition identified by shared legend: blue 120 s, orange 8 s") for i,ax in enumerate(axes)]))

    stems = ["01_PIPELINE_RESPONSE", "02_TOTAL_COST", "03_HOLDING_COST", "04_BACKLOG_COST", "05_ORDER_VARIANCE", "06_BULLWHIP"]
    for metric, stem in zip(METRICS, stems):
        fig, ax = plt.subplots(figsize=(16, 9))
        fig.suptitle("120 seconds vs 8 seconds: control reading", fontsize=30, fontweight="bold", x=.055, ha="left", y=.98)
        fig.text(.055, .915, "10 chains per condition · 4 roles per chain · 24 game weeks", fontsize=20, color="#455665")
        panel(ax, metric)
        fig.subplots_adjust(left=.23, right=.96, top=.75, bottom=.405)
        fig.legend(handles=legend, labels=legend_labels, handler_map={tuple: HandlerTuple(ndivide=1)},
                   loc="upper left", bbox_to_anchor=(.05, .26), frameon=False, fontsize=18, ncol=2)
        formula = "Calculation: " + metric[4]
        fig.text(.055, .17, textwrap.fill(formula, 104), fontsize=18, va="top", linespacing=1.3)
        fig.text(.055, .04, "Numbers: mean ± 95% CI margin (t, n=10). P-values use paired comparisons; CI bands describe each mean.", fontsize=15, color="#455665")
        fig.text(.055, .012, "Fictional time framing; actual model runtime was unrestricted.", fontsize=15, color="#455665")
        figures.append((stem, fig))
        catalog.append(dict(file=stem, title=metric[1], variables=[metric[0]], calculation=metric[4],
                            p_annotation=p_label(metric[0]),
                            axes=[dict(title=ax.get_title(loc="left"), x_label=ax.get_xlabel(), y_label=ax.get_ylabel())]))

    with PdfPages(DESTINATION / "ALL_CONTROL_FIGURES.pdf", metadata={"CreationDate": None, "ModDate": None}) as collection:
        for stem, fig in figures:
            for extension in ("png", "pdf", "svg"):
                metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else {"Date": None} if extension == "svg" else None
                fig.savefig(DESTINATION / (stem + "." + extension), dpi=200, facecolor="white", metadata=metadata)
            collection.savefig(fig, facecolor="white")
            plt.close(fig)

    definition = dict(conditions=CONDITIONS, n_chains_per_condition=10, paired_blocks=10, weeks=24,
                      data_displayed="Actual measured levels and condition-mean intervals, with existing H1/H2 paired p-values annotated",
                      markers="Overview: colored band width spans each mean's 95% CI; center mark and printed number show the mean. Shared colors identify conditions. Individual figures additionally show unconnected chain dots and mean ± CI half-width.",
                      confidence_interval=dict(method=INTERVAL_METHOD, confidence_level=.95, degrees_of_freedom=n_chains-1,
                                               critical_t=critical_t, simultaneous=False,
                                               note="Intervals describe individual condition means, not paired differences; their overlap does not determine the paired p-value."),
                      p_values=dict(source="reports/tables/HYPOTHESIS_COMPARISONS.csv", displayed_hypotheses=["H1", "H2"],
                                    test="Exact two-sided paired sign-flip", n_pairs=10,
                                    adjustment="Holm across the original five planned tests", display="p < 0.01; exact values retained in TEST_ANNOTATIONS.csv", newly_computed_tests=False),
                      connecting_lines=False,
                      typography=dict(overview_primary_title_pt=22, overview_primary_mean_pt=19,
                                      overview_primary_axis_labels_pt=17, overview_primary_ticks_pt=15,
                                      overview_secondary_title_pt=17, overview_secondary_mean_pt=15,
                                      overview_secondary_axis_labels_pt=14, overview_secondary_ticks_pt=13,
                                      single_axis_labels_pt=22, single_ticks_pt=22,
                                      overview_figure_size_inches=[16, 9], single_figure_size_inches=[16, 9]),
                      no_education_condition_plotted=True, no_new_hypothesis_tests=True, figures=catalog)
    write_json(DESTINATION / "FIGURE_DEFINITIONS.json", definition)
    readme = ["# Measured outcomes: control reading only", "",
              "**120 seconds + control reading versus 8 seconds + control reading.** These figures add a two-condition view of the closed experiment-14 data. The existing figures remain unchanged.", "",
              "[Overview PNG](00_ALL_MEASURED_OUTCOMES.png) · [Overview PDF](00_ALL_MEASURED_OUTCOMES.pdf) · [All seven figures in one PDF](ALL_CONTROL_FIGURES.pdf) · [Existing figure set](../README.md)", "",
              "**Slide overview:** the two large upper panels combine each H1/H2 prediction with its observed result, condition means and **95% confidence bands**. H1 predicts greater pipeline underweighting under time constraint; its measured response proxy falls 38.5%. H2 predicts higher cumulative total holding and backlog cost; observed cost rises 11.9%. Percent change is `(8-second mean / 120-second mean − 1) × 100`; these are descriptive changes in condition means, with the original paired tests shown as **p < 0.01** after Holm correction. The lower four panels are explicitly descriptive, not additional H1/H2 tests. One shared color legend identifies blue = 120 seconds and orange = 8 seconds. Band width shows the condition-mean CI; its center mark and numeric label show the mean. Detailed individual figures retain chain dots and mean ± CI half-width labels; all exact statistics and calculations remain in the CSV files.", "",
              "**Error-band calculation:** " + INTERVAL_METHOD + f" Here n=10 chains per condition, df=9, and the critical t value is {critical_t:.9f}. SD is the sample standard deviation across chain scores. These are approximate pointwise mean intervals under independent, approximately normal chain-score assumptions; they are not SD bands, prediction intervals or simultaneous intervals. The dots show the observed spread.", "",
              "**Terminology:** H1 is pipeline underweighting; the plotted response proxy is labeled on its x-axis. One case/case means one case of order reduction per additional outstanding case. Lower response is consistent with greater underweighting, but no optimal-response benchmark was estimated. The plotted values are response scores, not direct underweighting scores. H2 uses the full name total holding and backlog cost; this is the same quantity previously shortened to total cost. Labels changed; observations, means, intervals and tests did not.", "",
              "**P-values:** pipeline underweighting's response proxy (H1) and total holding and backlog cost (H2) display the existing exact two-sided paired sign-flip p-values, Holm-adjusted across all five original planned tests: **p=0.009765625** each (raw p=0.001953125). Both compare **8 seconds + control reading minus 120 seconds + control reading**, using ten matched differences. Mean intervals describe each condition separately, while the tests use the pairing; overlapping mean intervals do not imply a nonsignificant paired comparison. The other four panels are descriptive: no primary test was planned for those outcomes with this two-condition comparison. No new hypothesis tests were added.", "",
              "All figures use a 16:9 layout. The overview prioritizes H1/H2 with 22-point hypothesis headings, 19-point mean labels and 17-point axis labels; the four supplementary panels use 17-point titles and 15-point mean labels. Individual figures use 22-point axis labels and ticks. Use PDF or SVG for scalable slide graphics; PNG copies are also provided.", "",
              "These are absolute measured values. Fictional student seconds do not restrict actual model runtime. Only the two control-reading conditions enter these plots; the education condition remains in the original report and figures.", "",
              "| Measured quantity | 120 seconds + control reading: mean ± 95% CI margin | 8 seconds + control reading: mean ± 95% CI margin | Unit |", "|---|---:|---:|---|"]
    for metric in METRICS:
        key, name, ylabel, digits, formula, short_formula = metric
        readme.append(f"| {name} | {means[(key, 'A')]:.{digits}f} ± {intervals[(key, 'A')]['ci95_half_width']:.{digits}f} | {means[(key, 'B')]:.{digits}f} ± {intervals[(key, 'B')]['ci95_half_width']:.{digits}f} | {summary[key]['units']} |")
    readme.extend(["", "[Exact means, SDs and CI limits](CONDITION_MEANS.csv) · [Every plotted chain value](CHAIN_VALUES.csv) · [Saved p-value annotations](TEST_ANNOTATIONS.csv) · [Machine-readable axis definitions](FIGURE_DEFINITIONS.json)", ""])
    for metric, stem in zip(METRICS, stems):
        readme.extend(["## " + metric[1], "", f"[PNG]({stem}.png) · [PDF]({stem}.pdf) · [SVG]({stem}.svg)", "", metric[4], ""])
    readme.extend(["Pipeline response is a responsiveness proxy rather than an identified optimal supply-line weight. Total holding and backlog cost equals the sum of the two separately plotted cost components. Order variance and bullwhip here are descriptive comparisons between the control-reading conditions; the original H4 tests compare different conditions and are not redefined.", "",
                  "Rebuild offline from the repository root: `python scripts/export_exp14_control_figures.py`. No model calls. [Preservation and source hashes](MANIFEST.json).", ""])
    (DESTINATION / "README.md").write_text("\n".join(readme), encoding="utf-8")
    check_existing(publication)
    if any(sha(ROOT / name) != expected for name, expected in inputs.items()):
        raise ValueError("An input changed while making the figures")
    write_json(manifest, dict(schema="exp14-control-reading-figures-v1", fingerprint=fingerprint, inputs=inputs,
                             conditions=list(CONDITIONS.values()), figures=len(figures), plotted_chain_values=len(point_rows),
                             reported_condition_means=len(mean_rows), mean_values_reconciled=True,
                             original_publication_unchanged=True, preserved_publication_artifacts=publication["artifacts"],
                             **preservation, new_model_calls=0,
                             artifacts={path.relative_to(DESTINATION).as_posix(): sha(path) for path in sorted(DESTINATION.iterdir()) if path.is_file() and path != manifest}))
    print(json.dumps(dict(folder=str(DESTINATION), overview=str(DESTINATION / "00_ALL_MEASURED_OUTCOMES.png"),
                          pdf=str(DESTINATION / "ALL_CONTROL_FIGURES.pdf"), figures=len(figures),
                          original_publication_unchanged=True, cached=False), indent=2))


if __name__ == "__main__":
    main()
