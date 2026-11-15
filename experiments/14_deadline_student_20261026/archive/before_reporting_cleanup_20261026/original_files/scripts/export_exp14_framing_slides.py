"""Presentation-only exports of the completed fixed framing sample.

Reads the frozen analysis outputs; never changes choices, inclusion or tests.
Refuses to publish inferential slides before all ten reviewed blocks qualify.
"""
from pathlib import Path
from hashlib import sha256
import json
import csv
import shutil
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/14_deadline_student_20261026"
SOURCE = EXP / "analysis/student_framing_v3/RESULTS.json"
FOLDER = EXP / "reports/student_framing_v3/slides"
LABELS = {"H1": "Pipeline response", "H2": "Total cost", "H3": "Pipeline response",
          "H4a": "Order variance", "H4b": "Bullwhip"}
UNITS = {"H1": "Order cases / outstanding case", "H2": "Game cost units",
         "H3": "Order cases / outstanding case", "H4a": "Cases squared", "H4b": "Ratio"}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def fmt(value):
    return f"{value:.4g}"


def conclusions(ends, folder, concordant):
    """One-page readable summary; numbers are copied from the frozen outputs."""
    by_id = {r["hypothesis"]: r for r in ends}
    sentences = []
    for key, text in (("H1", "Pressure - adequate, pipeline response"),
                      ("H2", "Pressure - adequate, total holding/backlog cost"),
                      ("H3", "Education - control, pipeline response")):
        r = by_id[key]
        sentences.append(f"{key}: {text}: mean difference {r['mean_difference']:+.4g}; Holm p={fmt(r['p_holm_family_5'])}.")
    a, b = by_id["H4a"], by_id["H4b"]
    sentences.append(f"H4: Education - control: order variance {a['mean_difference']:+.4g} (Holm p={fmt(a['p_holm_family_5'])}); bullwhip {b['mean_difference']:+.4g} (Holm p={fmt(b['p_holm_family_5'])}).")
    rows = [[r["hypothesis"], LABELS[r["hypothesis"]] + " (" + UNITS[r["hypothesis"]] + ")",
             f"{r['mean_difference']:+.4g}", f"{fmt(r['ci95_low'])} to {fmt(r['ci95_high'])}",
             fmt(r["p_two_sided"]), fmt(r["p_holm_family_5"])] for r in ends]
    intro = "GPT-6 Astra / extra high. Ten matched chain pairs; 40 fictional roles per condition; 24 weeks. Development responses are excluded."
    methods = "H1/H2 compare pressure with adequate time. H3/H4 compare education with control under pressure. Tests are exact two-sided paired sign flips; Holm adjusts the five endpoints. Intervals are pointwise 95% paired-block bootstrap intervals."
    if concordant:
        methods += " All ten paired differences have the predicted sign for every endpoint, so each exact raw p equals 2/1024; the identical p-values are expected."
    limits = "These are AI student-roleplay results, not observations of real students. Actual model runtime was unlimited; every answer came from the model. Pipeline response is a proxy for underweighting. Shared project context and the block6 service interruption are documented in the full report/context note."
    lines = ["# Experiment 14: H1-H4 conclusions", "", intro, ""]
    lines.extend(f"{i}. {s}" for i, s in enumerate(sentences, 1))
    lines.extend(["", "| H | Quantity / units | Mean contrast | 95% interval | Raw p | Holm 5 |", "|---|---|---:|---|---:|---:|"])
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.extend(["", methods, "", limits, "", "[Full report](../REPORT.pdf) | [Figures and plotting data](README.md)", ""])
    (folder / "CONCLUSIONS.md").write_bytes("\n".join(lines).encode("utf-8"))
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from xml.sax.saxutils import escape
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ShortBody", fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=9))
    styles.add(ParagraphStyle(name="ShortCell", fontName="Helvetica", fontSize=8, leading=10))
    body = styles["ShortBody"]
    story = [Paragraph("Experiment 14: H1-H4 conclusions", styles["Title"]), Paragraph(escape(intro), body), Spacer(1, 8)]
    story += [Paragraph(escape(f"{i}. {s}"), body) for i, s in enumerate(sentences, 1)]
    table_data = [["H", "Quantity / units", "Mean", "95% interval", "Raw p", "Holm 5"], *rows]
    table = Table([[Paragraph(escape(cell), styles["ShortCell"]) for cell in row] for row in table_data],
                  colWidths=[32, 165, 65, 105, 58, 58], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e4edf4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("LINEBELOW", (0, 0), (-1, -1), .3, colors.HexColor("#ccd6df"))]))
    story += [Spacer(1, 8), table, Spacer(1, 15), Paragraph(escape(methods), body), Paragraph(escape(limits), body)]
    SimpleDocTemplate(str(folder / "CONCLUSIONS.pdf"), pagesize=A4, rightMargin=36, leftMargin=36,
                      topMargin=36, bottomMargin=36, title="Experiment 14: H1-H4 conclusions").build(story)


def export():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    main = data["main"]
    if not main["inference_enabled"] or main["complete_blocks"] != 10:
        raise ValueError("Slides require the full ten-block reviewed main sample; no interim significance plots")
    ends = main["endpoints"]
    assert [r["hypothesis"] for r in ends] == ["H1", "H2", "H3", "H4a", "H4b"]
    checks = []
    for endpoint in ends:
        rows = [r for r in main["contrasts"] if r["hypothesis"] == endpoint["hypothesis"]]
        assert len(rows) == endpoint["n_pairs"] == 10
        assert abs(statistics.fmean(r["difference"] for r in rows) - endpoint["mean_difference"]) < 1e-10
        last = next(r for r in main["prefixes"] if r["hypothesis"] == endpoint["hypothesis"] and r["prefix_size"] == 10)
        assert abs(last["mean_difference"] - endpoint["mean_difference"]) < 1e-10
        assert last["p_two_sided"] == endpoint["p_two_sided"]
        checks.append(dict(hypothesis=endpoint["hypothesis"], n=10, mean_and_final_prefix_match=True,
                           raw_p_matches=True, all_pairs_predicted_direction=all(r["difference"] * endpoint["predicted_sign"] > 0 for r in rows),
                           exact_endpoint=endpoint))
    prefix_rows = []
    for n in range(1, 11):
        own = [dict(next(r for r in main["prefixes"] if r["hypothesis"] == e["hypothesis"] and r["prefix_size"] == n)) for e in ends]
        for row in own:
            row["p_holm_family_5_at_prefix"] = None
        if all(r["p_two_sided"] is not None for r in own):
            bound = 0.0
            for rank, index in enumerate(sorted(range(5), key=lambda i: own[i]["p_two_sided"])):
                bound = max(bound, min(1.0, (5-rank) * own[index]["p_two_sided"]))
                own[index]["p_holm_family_5_at_prefix"] = bound
        if n == 10:
            assert all(r["p_holm_family_5_at_prefix"] == e["p_holm_family_5"] for r, e in zip(own, ends))
        prefix_rows.extend(own)
    fingerprint = sha256((digest(SOURCE) + digest(Path(__file__))).encode()).hexdigest()
    manifest_path = FOLDER / "VALIDATION.json"
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
        if old["fingerprint"] == fingerprint and all((FOLDER / p).exists() and digest(FOLDER / p) == h for p, h in old["artifacts"].items()):
            print(json.dumps(dict(folder=str(FOLDER), cached=True)))
            return
        for name in [*old["artifacts"], "VALIDATION.json"]:
            source = FOLDER / name
            if source.exists():
                target = FOLDER / "history" / old["fingerprint"][:20] / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() and target.read_bytes() != source.read_bytes():
                    raise ValueError("Preserve earlier slide bytes")
                if not target.exists():
                    shutil.copyfile(source, target)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    FOLDER.mkdir(parents=True, exist_ok=True)
    artifacts = []
    figures = []
    common_p = len({(r["p_two_sided"], r["p_holm_family_5"]) for r in ends}) == 1
    fig, axes = plt.subplots(1, 5, figsize=(15, 4.2))
    for ax, endpoint in zip(axes, ends):
        key = endpoint["hypothesis"]
        rows = [r for r in main["contrasts"] if r["hypothesis"] == key]
        values = [r["difference"] for r in rows]
        x = [.12 + i * .065 for i in range(10)]
        ax.scatter(x, values, color="#7898b6", alpha=.85, s=25, zorder=3)
        mu = endpoint["mean_difference"]
        low, high = endpoint["ci95_low"], endpoint["ci95_high"]
        ax.vlines(.95, low, high, color="#183b56", linewidth=2.4, zorder=4)
        ax.scatter([.95], [mu], marker="D", color="#183b56", s=52, zorder=5)
        ax.axhline(0, color="#999999", linewidth=.8)
        ax.set(xlim=(0, 1.15), xticks=[], ylabel=UNITS[key])
        ax.set_title(f"{key}\n{LABELS[key]}", fontsize=12, pad=10)
        ax.set_xlabel("Pressure - adequate" if key in ("H1", "H2") else "Education - control", labelpad=10, fontsize=9)
        if not common_p:
            lo, hi = ax.get_ylim()
            ax.set_ylim(lo, hi + .30 * (hi-lo))
            ax.text(.5, .98, f"p={fmt(endpoint['p_two_sided'])}\nadj={fmt(endpoint['p_holm_family_5'])}",
                    transform=ax.transAxes, ha="center", va="top", fontsize=9)
        ax.tick_params(axis="y", labelsize=8)
    fig.suptitle("GPT-6 Astra: H1-H4", fontsize=17, y=.99)
    if common_p:
        fig.text(.5, .86, f"All five tests: raw p={fmt(ends[0]['p_two_sided'])}; Holm p={fmt(ends[0]['p_holm_family_5'])}", ha="center", fontsize=11)
    fig.text(.5, .015, "10 matched chain pairs | dots: pairs; diamond: mean; bar: pointwise 95% CI | adj: Holm, 5 outcomes | student-pressure framing", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .065, 1, .88))
    figures.append(("H1_H4", fig))
    fig, axes = plt.subplots(2, 5, figsize=(15, 6.2), sharex=True)
    for col, endpoint in enumerate(ends):
        key = endpoint["hypothesis"]
        rows = sorted((r for r in prefix_rows if r["hypothesis"] == key), key=lambda r: r["prefix_size"])
        assert len(rows) == 10 and all(r["complete_prefix"] for r in rows)
        axes[0, col].plot([r["prefix_size"] for r in rows], [r["mean_difference"] for r in rows], "o-", color="#245b8a", markersize=4)
        axes[0, col].axhline(0, color="#999999", linewidth=.8)
        axes[0, col].set(title=key, ylabel=UNITS[key])
        p = [r for r in rows if r["p_holm_family_5_at_prefix"] is not None]
        axes[1, col].plot([r["prefix_size"] for r in p], [r["p_holm_family_5_at_prefix"] for r in p], "o-", color="#245b8a", markersize=4)
        axes[1, col].axhline(.05, color="#c08332", linestyle="--", linewidth=1)
        axes[1, col].set(yscale="log", ylim=(.001, 1.3), xlabel="Chains", ylabel="Holm p", xticks=[1, 2, 4, 6, 8, 10], xlim=(.7, 10.3))
        for ax in axes[:, col]:
            ax.tick_params(labelsize=8)
    fig.suptitle("Chain count and conclusion stability", fontsize=16)
    fig.text(.5, .01, "Fixed prefixes of the completed sample | Holm correction across 5 outcomes at each prefix | N=10 is primary | dashed line: p=.05", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .045, 1, .94))
    figures.append(("CHAIN_SIZE", fig))
    for name, fig in figures:
        for extension in ("png", "svg", "pdf"):
            path = FOLDER / (name + "." + extension)
            fig.savefig(path, dpi=220, bbox_inches="tight")
            artifacts.append(path.name)
    with PdfPages(FOLDER / "SLIDE_FIGURES.pdf") as pdf:
        for _, fig in figures:
            pdf.savefig(fig, bbox_inches="tight")
    artifacts.append("SLIDE_FIGURES.pdf")
    with (FOLDER / "CHAIN_SIZE.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(prefix_rows[0]))
        writer.writeheader()
        writer.writerows(prefix_rows)
    artifacts.append("CHAIN_SIZE.csv")
    concordant = all(c["all_pairs_predicted_direction"] for c in checks)
    conclusions(ends, FOLDER, concordant)
    artifacts.extend(["CONCLUSIONS.md", "CONCLUSIONS.pdf"])
    for _, fig in figures:
        plt.close(fig)
    lines = ["# Slides: current experiment 14", "", "[One-page conclusions PDF](CONCLUSIONS.pdf) ([text](CONCLUSIONS.md)) | [H1-H4](H1_H4.png) ([PDF](H1_H4.pdf), [SVG](H1_H4.svg)) | [Chain size](CHAIN_SIZE.png) ([PDF](CHAIN_SIZE.pdf), [SVG](CHAIN_SIZE.svg)) | [Both slides in PDF](SLIDE_FIGURES.pdf)", "",
             "One Astra/xhigh model, ten matched chain pairs. Positive numbers mean the first named condition is higher. These are fictional student-pressure responses, with unlimited actual model time and no software answers.", "",
             "| Hypothesis | Quantity | Mean contrast | Raw p | Holm 5 |", "|---|---|---:|---:|---:|"]
    for r in ends:
        lines.append(f"| {r['hypothesis']} {r['contrast']} | {LABELS[r['hypothesis']]} | {fmt(r['mean_difference'])} | {fmt(r['p_two_sided'])} | {fmt(r['p_holm_family_5'])} |")
    if concordant:
        lines.extend(["", "All ten paired differences have the predicted sign for every endpoint. Thus the exact two-sided raw p is 2/1024 for each test; identical p-values and lower-panel curves are expected, while the effect magnitudes differ."])
    lines.extend(["", "**H1-H4 slide:** dots show the ten paired differences; the diamond is their mean and the bar is a pointwise 95% interval. H1/H3 measure response to outstanding orders, H2 measures total holding/backlog cost, and H4a/b measure order variance and bullwhip.", "",
        "**Chain-size slide:** the top row shows cumulative mean contrasts and the bottom row Holm-adjusted p-values across the same five outcomes at each fixed prefix of 1 through 10 pairs. Raw and adjusted values are in [the exact plotting data](CHAIN_SIZE.csv); n=1 p is unavailable. The final adjusted values exactly match the main results. N=10 is primary. These completed-sample sensitivity views do not predict a significance threshold or justify selecting a favorable sample size.", "",
        "The pipeline quantity is a responsiveness proxy. No human students were observed; shared project context was visible to the agents. See [full report](../REPORT.pdf) and [context limitations](../CONTEXT.md).", ""])
    (FOLDER / "README.md").write_bytes("\n".join(lines).encode("utf-8"))
    artifacts.append("README.md")
    manifest = dict(fingerprint=fingerprint, source_results_sha256=digest(SOURCE), exporter_sha256=digest(Path(__file__)),
        source_analysis_fingerprint=data["fingerprint"], exact_endpoint_checks=checks, inference_recomputed=False,
        fixed_main_blocks=10, actual_model_timer=False, synthetic_answers=False,
        prefix_holm_interpretation="Exploratory completed-sample display transformation of the five frozen raw prefix p-values; n=10 remains primary",
        artifacts={name: digest(FOLDER / name) for name in artifacts})
    manifest_path.write_bytes((json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(dict(folder=str(FOLDER), endpoint_checks=len(checks), artifacts=len(artifacts)), indent=2))


if __name__ == "__main__":
    export()
