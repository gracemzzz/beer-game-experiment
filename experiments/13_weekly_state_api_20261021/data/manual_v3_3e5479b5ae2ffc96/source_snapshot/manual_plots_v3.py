"""Standalone scientific figures from matched manual block outcomes only.

No API, synthetic observations, extrapolation, or empty-data figures are made.
Existing exports are preserved; a changed analysis requires a new directory.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


LABELS = {
    "H1": ("Pipeline response: restricted minus adequate control", "B - A pipeline sensitivity"),
    "H2": ("Cumulative inventory and backlog cost", "B - A mean chain cost ($)"),
    "H3": ("Pipeline response: education minus control", "C - B pipeline sensitivity"),
    "H4a": ("Individual order variation", "C - B mean role order variance (cases squared)"),
    "H4b": ("Bullwhip amplification", "C - B mean role bullwhip ratio"),
}
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00")


def _observed(row):
    value = row.get("mean_difference")
    return row.get("n_pairs", 0) > 0 and type(value) in (float, int) and math.isfinite(value)


def _new(path, text):
    data = text.encode("utf-8")
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Changed plot inputs; use a new analysis directory.")
        return
    with path.open("xb") as stream:
        stream.write(data)


def plot_analysis(result, output):
    """Return one artifact dictionary per endpoint with actual matched data.

    ``output/figures`` holds PNG/PDF/SVG figures and a source/endpoint receipt.
    Prefix points retain their actual matched-block counts; absent prefixes are
    not inferred. Inputs labeled development/synthetic stay visibly labeled.
    """
    observed = [row for row in result.get("primary", []) if _observed(row)]
    if not observed:
        return []
    output = Path(output) / "figures"
    output.mkdir(parents=True, exist_ok=True)
    data_hash = hashlib.sha256(json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    renderer_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    _new(output / "PLOT_SOURCE.json", json.dumps(dict(analysis_sha256=data_hash, renderer_sha256=renderer_hash), indent=2) + "\n")
    synthetic = result.get("source_kind") == "synthetic_software_control"
    development = result.get("collection_kind") == "development"
    kind = "SYNTHETIC SOFTWARE CONTROL" if synthetic else "DEVELOPMENT" if development else "MODEL SIMULATION"
    artifacts = []
    for hypothesis, (title, metric_label) in LABELS.items():
        rows = [r for r in observed if r["hypothesis"] == hypothesis]
        if not rows:
            continue
        incomplete = not result.get("all_planned_games_complete", False) or any(not r.get("planned_sample_complete", False) for r in rows)
        status = "INTERIM" if incomplete else "FIXED SAMPLE COMPLETE"
        figure = Figure(figsize=(12.5, max(4.8, 3.5 + .3 * len(rows))), facecolor="white")
        FigureCanvasAgg(figure)
        left, right = figure.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1]})
        figure.subplots_adjust(left=.22, right=.97, bottom=.24, top=.78, wspace=.36)
        figure.suptitle(f"{hypothesis} | {title}\n{kind} | {status}", fontsize=13, fontweight="bold", y=.97)
        left.axvline(0, color="#777777", linestyle="--", linewidth=1)
        right.axhline(0, color="#777777", linestyle="--", linewidth=1)
        for index, row in enumerate(rows):
            color = COLORS[index % len(COLORS)]
            mean = row["mean_difference"]
            low, high = row.get("ci95_low"), row.get("ci95_high")
            if low is not None and high is not None:
                left.plot([low, high], [index, index], color=color, linewidth=2.4, solid_capstyle="round")
            left.plot(mean, index, "o", color=color, markersize=7)
            prefix = [r for r in result.get("sweeps", []) if r.get("model") == row["model"] and
                      r.get("hypothesis") == hypothesis and _observed(r)]
            prefix.sort(key=lambda r: r["planned_blocks"])
            if prefix:
                xs = [r["planned_blocks"] for r in prefix]
                ys = [r["mean_difference"] for r in prefix]
                right.plot(xs, ys, marker="o", color=color, linewidth=1.6, label=row["model"])
                for point in prefix:
                    right.annotate("n=" + str(point["n_pairs"]), (point["planned_blocks"], point["mean_difference"]),
                                   xytext=(4, 6 + 8 * index), textcoords="offset points", fontsize=8, color=color)
            left.set_yticks(range(len(rows)), [f"{r['model']}\n{r['n_pairs']}/{r['planned_blocks']} matched blocks" for r in rows])
        left.invert_yaxis()
        left.set_xlabel(metric_label, fontsize=9)
        left.set_title("Full planned sample: paired effect and 95% interval", fontsize=10)
        left.grid(axis="x", alpha=.2)
        right.set_title("Fixed sample-size prefixes", fontsize=10)
        right.set_xlabel("Planned independent blocks in prefix", fontsize=9)
        right.set_ylabel(metric_label, fontsize=9)
        right.set_xticks([10, 20, 40])
        right.grid(alpha=.2)
        handles, _ = right.get_legend_handles_labels()
        if handles:
            right.legend(fontsize=8, frameon=False, loc="best")
        else:
            right.text(.5, .5, "No matched 10/20/40 prefix data yet", ha="center", va="center",
                       transform=right.transAxes, fontsize=9, color="#666666")
        for ax in (left, right):
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.tick_params(labelsize=9)
        figure.text(.03, .09, "Points are paired independent-block mean contrasts; chains within one chat do not increase n.\n"
                    "Intervals are unadjusted paired-bootstrap 95% CIs. Fixed prefixes are descriptive, not a stopping rule.\n"
                    "Review opportunities are an AI analogue; binding human decision time and student fidelity are unverified.",
                    fontsize=8, color="#444444", va="center")
        files = {}
        for extension in ("png", "pdf", "svg"):
            destination = output / (hypothesis + "." + extension)
            if not destination.exists():
                with destination.open("xb") as stream:
                    figure.savefig(stream, format=extension, dpi=240, facecolor="white")
            files[extension] = destination.relative_to(output.parent).as_posix()
        artifacts.append(dict(hypothesis=hypothesis, status=status, data_kind=kind, files=files,
                              file_sha256={extension: hashlib.sha256((output.parent / name).read_bytes()).hexdigest()
                                           for extension, name in files.items()},
                              matched_blocks={r["model"]: r["n_pairs"] for r in rows},
                              prefix_counts={r["model"]: {str(p["planned_blocks"]): p["n_pairs"]
                                  for p in result.get("sweeps", []) if p.get("model") == r["model"] and
                                  p.get("hypothesis") == hypothesis and _observed(p)} for r in rows}))
    _new(output / "FIGURES.json", json.dumps(artifacts, indent=2, ensure_ascii=False) + "\n")
    return artifacts
