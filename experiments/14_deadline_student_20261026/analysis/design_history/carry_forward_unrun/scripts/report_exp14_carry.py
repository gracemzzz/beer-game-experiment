"""Generate only experiment 14 carry-forward amendment reports; no model calls."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_carry_analysis import EXPERIMENT, REPORTS, generate_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=EXPERIMENT)
    args = parser.parse_args(argv)
    result = generate_report(args.experiment)
    print(json.dumps(dict(report=str(args.experiment / REPORTS / "REPORT.md"), fingerprint=result["fingerprint"],
                          saved_contexts=len(result["runs"]), development_games=result["development"]["complete_physical_games"],
                          complete_actor_cases=result["development"]["complete_actor_cases"],
                          main_inference_enabled=result["main"]["inference_enabled"]), indent=2))


if __name__ == "__main__":
    main()
