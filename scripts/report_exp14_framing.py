"""Publish the closed student-framing study with explicit variables and values."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_publication import EXPERIMENT, publish


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=EXPERIMENT)
    args = parser.parse_args(argv)
    print(json.dumps(publish(args.experiment), indent=2))


if __name__ == "__main__":
    main()
