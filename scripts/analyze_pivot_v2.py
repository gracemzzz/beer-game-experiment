"""Offline analysis of frozen, preaggregated independent pivot blocks."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.pivot_inference_v2 import analyze, load_inputs, report_markdown


def _new(path, value):
    data = value.encode("utf-8")
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refuse to overwrite prior analysis; use a new output directory: " + str(path))
        return
    with path.open("xb") as stream:
        stream.write(data)


def _csv(rows):
    if not rows:
        return ""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})
    return stream.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True, help="One aggregated CSV row per model/block/arm.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    plan, rows, evidence = load_inputs(args.plan, args.input)
    result = analyze(plan, rows, input_evidence=evidence)
    args.output.mkdir(parents=True, exist_ok=True)
    products = {"ANALYSIS.json": json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                "REPORT.md": report_markdown(result)}
    products.update({name + ".csv": _csv(result[key]) for name, key in (
        ("hypotheses", "primary"), ("sample_size_sweeps", "sweeps"),
        ("paired_block_contrasts", "contrasts"), ("missing_block_arm_rows", "missing_cluster_arm_rows"))})
    # Preflight every product before writing any, so reruns cannot mix versions.
    for name, value in products.items():
        destination = args.output / name
        if destination.exists() and destination.read_bytes() != value.encode("utf-8"):
            raise ValueError("Output differs from saved analysis; choose a new output directory.")
    for name, value in products.items():
        _new(args.output / name, value)
    print(str((args.output / "REPORT.md").resolve()))
    print(f"Rows {result['received_cluster_arm_rows']}/{result['expected_cluster_arm_rows']}; "
          f"provenance={evidence['provenance_status']}; source={result['source_kind']}")
    return result


if __name__ == "__main__":
    main()
