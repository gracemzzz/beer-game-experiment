"""Build experiment 14's current offline report without collecting observations."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_analysis import EXPERIMENT, generate_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=EXPERIMENT,
                        help="Experiment 14 directory; alternate locations are useful for synthetic software checks")
    args = parser.parse_args(argv)
    result = generate_report(args.experiment)
    print(json.dumps(dict(report=str(args.experiment / "reports/REPORT.md"), fingerprint=result["fingerprint"],
                          saved_attempts=len(result["runs"]), complete_main_blocks=result["main"]["complete_matched_blocks"],
                          main_inference_enabled=result["main"]["eligible"]), indent=2))


if __name__ == "__main__":
    main()
