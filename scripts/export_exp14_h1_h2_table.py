"""Render a concise H1/H2 slide table without changing its statistics."""
from pathlib import Path
import csv
import hashlib
import json
import math
import shutil
import sys
from exp14_slide_labels import HYPOTHESIS_LABELS, hypothesis_heading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_publication import EXPERIMENT, read, sha


def main():
    reports = EXPERIMENT / "reports"
    destination = reports / "figures/conclusions"
    source = reports / "tables/HYPOTHESIS_COMPARISONS.csv"
    publication = read(reports / "PUBLICATION.json")
    for name, digest in publication["artifacts"].items():
        assert sha(reports / name) == digest, name
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["hypothesis"] in ("H1", "H2")]
    assert [row["hypothesis"] for row in rows] == ["H1", "H2"]
    for row in rows:
        assert row["contrast"] == "B-A" and int(row["n_pairs"]) == 10
        assert math.isclose(float(row["first_condition_mean"])-float(row["second_condition_mean"]),
                            float(row["mean_difference"]), abs_tol=1e-12)
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in
              [Path(__file__), Path(__file__).with_name("exp14_slide_labels.py"), source]}
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    manifest = destination / "H1_H2_TABLE.json"
    if manifest.exists():
        old = read(manifest)
        if old["fingerprint"] == fingerprint and all(sha(destination/n) == h for n,h in old["artifacts"].items()):
            print(str(destination / "H1_H2_TABLE.png"))
            return
        archive = EXPERIMENT / "archive/publication_versions/h1_h2_table" / old["fingerprint"][:16]
        archive.mkdir(parents=True, exist_ok=True)
        for name in [*old["artifacts"], manifest.name]:
            target = archive / name
            if target.exists():
                assert sha(target) == sha(destination / name)
            else:
                shutil.copyfile(destination / name, target)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "svg.hashsalt": "exp14-h1-h2-table", "pdf.fonttype": 42})
    fig = plt.figure(figsize=(16, 3.8), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 16), ylim=(0, 3.8))
    ax.axis("off")
    texts = []

    def text(x, y, value, size=23, bold=False, ha="center", color="#172E40"):
        artist = ax.text(x, y, value, fontsize=size, fontweight="bold" if bold else "normal",
                         ha=ha, va="center", color=color, linespacing=1.12)
        texts.append(artist)

    left, right = .2, 15.8
    edges = [.2, 6.75, 9.15, 13.35, 15.8]
    centers = [(a+b)/2 for a,b in zip(edges, edges[1:])]
    ax.add_patch(Rectangle((left, 3.0), right-left, .65, facecolor="#E4EDF6", edgecolor="none"))
    ax.add_patch(Rectangle((left, .30), right-left, 1.35, facecolor="#F7F9FC", edgecolor="none"))
    headers = ["Hypothesis", "Mean difference\n(8 s − 120 s)", "95% CI", "Holm p"]
    for i, header in enumerate(headers):
        text(edges[i]+.22 if i == 0 else centers[i], 3.325, header, 19 if i == 1 else 23, True,
             ha="left" if i == 0 else "center")
    display = []
    for i, row in enumerate(rows):
        y = 2.325 - 1.35*i
        digits = 4 if i == 0 else 2
        quantity = "Pipeline underweighting" if i == 0 else "Total holding and backlog cost"
        measured_quantity = "Pipeline response (proxy)" if i == 0 else quantity
        units = "Response proxy (cases/case)" if i == 0 else "Game cost units / chain"
        difference = f"{float(row['mean_difference']):+.{digits}f}".replace("-", "−")
        interval = f"[{float(row['ci95_low']):.{digits}f}, {float(row['ci95_high']):.{digits}f}]".replace("-", "−")
        assert 0 <= float(row['p_holm_family_5']) < .01
        p_holm = "< 0.01"
        text(edges[0]+.22, y+.20, hypothesis_heading(row['hypothesis']), 22, True, ha="left")
        text(edges[0]+.22, y-.40, units, 16, ha="left", color="#4B5E6D")
        for col, value in enumerate([difference, interval, p_holm], start=1):
            text(centers[col], y, value, 26 if col != 2 else 23, bold=col != 2)
        display.append(dict(hypothesis=row["hypothesis"], quantity=quantity, measured_quantity=measured_quantity, units=units,
                            hypothesis_statement=HYPOTHESIS_LABELS[row['hypothesis']],
                            difference=difference, interval=interval, holm_p=p_holm))
    ax.hlines([3.0, 1.65, .30], left, right, color="#B9C9D8", linewidth=1)
    fig.canvas.draw()
    for artist in texts:
        box = artist.get_window_extent(fig.canvas.get_renderer())
        assert box.x0 >= 0 and box.y0 >= 0 and box.x1 <= fig.bbox.width and box.y1 <= fig.bbox.height, artist.get_text()
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for extension in ("png", "pdf", "svg"):
        path = destination / ("H1_H2_TABLE."+extension)
        metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else {"Date": None} if extension == "svg" else None
        fig.savefig(path, dpi=300, facecolor="white", metadata=metadata)
        artifacts.append(path)
    plt.close(fig)
    assert all(sha(ROOT/name) == digest for name,digest in inputs.items())
    assert all(sha(reports/name) == digest for name,digest in publication["artifacts"].items())
    manifest.write_text(json.dumps(dict(fingerprint=fingerprint, inputs=inputs, values=rows,
                        displayed=display, original_publication_unchanged=True, new_model_calls=0,
                        new_hypothesis_tests=0, artifacts={p.name:sha(p) for p in artifacts}),
                        indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(destination / "H1_H2_TABLE.png"))


if __name__ == "__main__":
    main()
