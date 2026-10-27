"""Report only simulated student pressure v3; no collection or API calls."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_framing_analysis import EXPERIMENT, REPORTS, generate_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=EXPERIMENT)
    args = parser.parse_args(argv)
    result = generate_report(args.experiment)
    print(json.dumps(dict(report=str(args.experiment / REPORTS / "REPORT.md"), fingerprint=result["fingerprint"],
                          saved_contexts=len(result["runs"]), complete_development_blocks=result["development"]["complete_blocks"],
                          complete_main_blocks=result["main"]["complete_blocks"], main_inference_enabled=result["main"]["inference_enabled"]), indent=2))


if __name__ == "__main__":
    main()
