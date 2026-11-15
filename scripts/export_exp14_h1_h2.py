"""Presentation-only H1/H2 summary with the user's requested condition labels."""
from pathlib import Path
import csv
import hashlib
import json
import math
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_publication import EXPERIMENT, read, sha, verify_preservation

REPORTS = EXPERIMENT / "reports"
DESTINATION = REPORTS / "figures/conclusions"
STEM = "H1_H2_CONCLUSIONS"
LABELS = {"A": "No time constraint", "B": "Time constraint"}


def main():
    publication = read(REPORTS / "PUBLICATION.json")
    protected = {REPORTS / name: digest for name, digest in publication["artifacts"].items()}
    original = EXPERIMENT / "analysis/student_framing_v3/publication_review/CONCLUSIONS.png"
    protected[original] = sha(original)
    for folder in (DESTINATION, REPORTS / "figures/control_reading_only"):
        manifest = folder / "MANIFEST.json"
        if manifest.exists():
            protected[manifest] = sha(manifest)
            protected.update({folder / name: digest for name, digest in read(manifest)["artifacts"].items()})
    for path, digest in protected.items():
        if sha(path) != digest:
            raise ValueError("Existing publication changed: " + str(path))
    preservation = verify_preservation(EXPERIMENT)
    source = REPORTS / "tables/HYPOTHESIS_COMPARISONS.csv"
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in (Path(__file__), source, REPORTS / "PUBLICATION.json")}
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    receipt = DESTINATION / (STEM + "_MANIFEST.json")
    if receipt.exists():
        previous = read(receipt)
        if previous["fingerprint"] == fingerprint and all(sha(DESTINATION / n) == h for n, h in previous["artifacts"].items()):
            print(json.dumps(dict(image=str(DESTINATION / (STEM + ".png")), cached=True)))
            return
        archive = EXPERIMENT / "archive/publication_versions/h1_h2_conclusions" / previous["fingerprint"][:16]
        for name in [*previous["artifacts"], receipt.name]:
            old, new = DESTINATION / name, archive / name
            new.parent.mkdir(parents=True, exist_ok=True)
            if new.exists() and sha(new) != sha(old):
                raise ValueError("Conflicting archived version")
            if not new.exists():
                shutil.copyfile(old, new)

    with source.open(encoding="utf-8-sig", newline="") as handle:
        data = [r for r in csv.DictReader(handle) if r["hypothesis"] in ("H1", "H2")]
    if [r["hypothesis"] for r in data] != ["H1", "H2"]:
        raise ValueError("Expected the original H1 and H2 comparisons")
    for row in data:
        before, after = float(row["second_condition_mean"]), float(row["first_condition_mean"])
        if row["contrast"] != "B-A" or int(row["n_pairs"]) != 10:
            raise ValueError("Unexpected comparison")
        if not math.isclose(after-before, float(row["mean_difference"]), abs_tol=1e-12):
            raise ValueError("The condition means disagree with the saved difference")
        row.update(display_first_condition=LABELS["A"], display_second_condition=LABELS["B"],
                   display_difference="Time constraint minus No time constraint",
                   percentage_change=100*(after-before)/before)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "svg.hashsalt": "exp14-h1-h2-conclusions", "pdf.fonttype": 42})
    navy, muted, blue, orange = "#173247", "#526575", "#24628A", "#B65E22"
    fig = plt.figure(figsize=(16, 9), facecolor="#F6F8FB")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 16), ylim=(0, 9))
    ax.axis("off")
    artists = []

    def text(x, y, value, size, color=navy, bold=False, ha="left"):
        artist = ax.text(x, y, value, fontsize=size, color=color,
                         fontweight="bold" if bold else "normal", va="top", ha=ha, linespacing=1.2)
        artists.append(artist)

    def number(value, digits, signed=False):
        return format(float(value), ("+" if signed else "") + f".{digits}f").replace("-", "−")

    text(.55, 8.58, "Experiment 14: H1–H2 conclusions", 34, bold=True)
    text(.55, 7.97, "Time constraint vs no time constraint", 25, bold=True)
    text(.55, 7.43, "10 matched chain pairs · 4 simulated roles per chain · 24 weeks · Same control reading", 18, muted)
    descriptions = [
        ("H1  Pipeline underweighting", "Measured proxy: pipeline response\nOrder decrease / extra outstanding case", 4),
        ("H2  Total holding and backlog cost", "Sum across 4 roles and 24 weeks\nGame cost units / chain; mean across 10 chains", 2),
    ]
    displayed_text = []
    for i, (row, (title, description, digits)) in enumerate(zip(data, descriptions)):
        x = [.55, 8.20][i]
        ax.add_patch(FancyBboxPatch((x, 2.05), 7.25, 4.76,
                                   boxstyle="round,pad=0,rounding_size=.12",
                                   facecolor="white", edgecolor="#DEE6EE", linewidth=1))
        text(x+.25, 6.54, title, 24, bold=True)
        text(x+.25, 6.06, description, 17, muted)
        no_constraint, constraint = number(row["second_condition_mean"], digits), number(row["first_condition_mean"], digits)
        for y, label, value, color in [(5.20, LABELS["A"], no_constraint, blue),
                                       (4.55, LABELS["B"], constraint, orange)]:
            text(x+.25, y, label, 22, color)
            text(x+6.99, y+.09, value, 34, color, True, "right")
        ax.hlines(4.05, x+.25, x+7.00, color="#E2E8EF", linewidth=1)
        difference = number(row["mean_difference"], digits, signed=True)
        interval = "95% CI: " + number(row["ci95_low"], digits, signed=True) + " to " + number(row["ci95_high"], digits, signed=True)
        p_text = "Holm-adjusted p = " + number(row["p_holm_family_5"], 6)
        text(x+.25, 3.76, "Mean difference", 22)
        text(x+6.99, 3.83, difference, 30, bold=True, ha="right")
        text(x+.25, 3.23, interval, 21, muted)
        text(x+.25, 2.76, p_text, 23, bold=True)
        direction = "lower" if float(row["percentage_change"]) < 0 else "higher"
        measure = "proxy response" if row["hypothesis"] == "H1" else "holding and backlog cost"
        percent_text = f"{abs(float(row['percentage_change'])):.1f}% {direction} {measure}"
        text(x+.25, 2.30, percent_text, 18, orange, bold=True)
        displayed_text.append(dict(hypothesis=row["hypothesis"], no_time_constraint_mean=no_constraint,
                                   time_constraint_mean=constraint, difference=difference,
                                   interval=interval, adjusted_p=p_text, percent_change=percent_text,
                                   hypothesis_title=title, measured_quantity="Pipeline response (proxy)" if i == 0 else "Total holding and backlog cost"))

    text(.55, 1.70, "Mean difference = Time constraint − No time constraint. 95% CIs describe paired mean differences.", 18)
    text(.55, 1.35, "H1: lower pipeline response is consistent with more underweighting; no optimal benchmark was estimated.", 16)
    text(.55, 1.00, "Exact paired tests: raw p = 0.001953 each; Holm adjustment retained across the original five planned tests.", 16, muted)
    text(.55, .65, "Prompt labels: No time constraint = 120-second scenario; Time constraint = 8-second scenario.", 17)
    text(.55, .30, "Fictional student scenarios; actual model runtime unrestricted.", 16, muted)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for artist in artists:
        bounds = artist.get_window_extent(renderer)
        if bounds.x0 < 0 or bounds.y0 < 0 or bounds.x1 > fig.bbox.width or bounds.y1 > fig.bbox.height:
            raise ValueError("Text outside slide: " + artist.get_text())

    DESTINATION.mkdir(parents=True, exist_ok=True)
    output_names = []
    for extension in ("png", "pdf", "svg"):
        name = STEM + "." + extension
        metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else {"Date": None} if extension == "svg" else None
        fig.savefig(DESTINATION / name, dpi=240, facecolor=fig.get_facecolor(), metadata=metadata)
        output_names.append(name)
    plt.close(fig)
    csv_name = STEM + "_VALUES.csv"
    with (DESTINATION / csv_name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
    output_names.append(csv_name)
    guide_name = STEM + "_README.md"
    guide = """# H1 and H2 presentation image

[PNG](H1_H2_CONCLUSIONS.png) · [PDF](H1_H2_CONCLUSIONS.pdf) · [SVG](H1_H2_CONCLUSIONS.svg) · [Exact values](H1_H2_CONCLUSIONS_VALUES.csv)

Only the original H1 and H2 results are shown. The requested presentation labels map to the frozen conditions as follows:

| Presentation label | Actual prompt condition |
|---|---|
| No time constraint | 120 fictional seconds + control reading |
| Time constraint | 8 fictional seconds + the same control reading |

“No time constraint” is a presentation shorthand for the adequate-time scenario, not a literal unlimited student allowance. Both conditions had unrestricted actual model runtime. These data are LLM portrayals, not observations of human students.

Condition values are means across ten chains. Every displayed mean difference is **Time constraint minus No time constraint**. Percent change uses the no-time-constraint mean as its denominator. The 95% intervals are the existing paired-block bootstrap intervals for the mean difference; they are not intervals for individual condition means. The tests are the original exact two-sided paired sign-flip tests with ten matched pairs; the Holm adjustment is retained across the original five planned tests even though only H1 and H2 are displayed. No new tests, exclusions or participants were added.

H1's hypothesis concept is **pipeline underweighting**. Its recorded proxy is **pipeline response**: the chain's average of eight matched probe slopes, (order with low outstanding supply − order with high outstanding supply) / increase in outstanding cases. The condition value averages ten chains. The terms are not synonyms: a lower response is consistent with more underweighting, but establishing actual underweighting requires an appropriate benchmark that this experiment did not estimate. The displayed −0.1228 and −38.5% describe the response proxy, not an underweighting score. Labels are clarified without changing the hypothesis, original measurement, sign, estimates or tests.

H2 is **total holding and backlog cost**: the sum of 0.5 × remaining inventory + 1 × backlog across four roles and 24 weeks for a chain, then averaged across ten chains. Its unit is game cost units per chain. “Total cost” in the earlier image was shorthand for this same measure, not another outcome.

The exact source is [HYPOTHESIS_COMPARISONS.csv](../../tables/HYPOTHESIS_COMPARISONS.csv). The original conclusions images, full report and other figures are preserved. Rebuild offline with `python scripts/export_exp14_h1_h2.py` from the repository root; no model calls are made.
"""
    (DESTINATION / guide_name).write_text(guide, encoding="utf-8")
    output_names.append(guide_name)
    for path, digest in protected.items():
        if sha(path) != digest:
            raise ValueError("A protected publication changed: " + str(path))
    if any(sha(ROOT / name) != digest for name, digest in inputs.items()):
        raise ValueError("An input changed during rendering")
    receipt.write_text(json.dumps(dict(
        schema="exp14-h1-h2-conclusions-v1", fingerprint=fingerprint, inputs=inputs,
        label_mapping={"No time constraint": "120 fictional seconds + control reading", "Time constraint": "8 fictional seconds + control reading"},
        display_text=displayed_text, paired_n=10, correction_family_size=5, figure_inches=[16, 9],
        protected_publication_artifacts={p.relative_to(ROOT).as_posix(): h for p, h in protected.items()},
        original_publications_unchanged=True, rendered_text_in_bounds=True, new_model_calls=0,
        new_hypothesis_tests=0, **preservation,
        artifacts={name: sha(DESTINATION / name) for name in output_names},
    ), indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(dict(image=str(DESTINATION / (STEM + ".png")), pdf=str(DESTINATION / (STEM + ".pdf")), cached=False), indent=2))


if __name__ == "__main__":
    main()
