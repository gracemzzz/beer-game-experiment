"""Compatibility entry point for exporting the completed Claude prompt file."""
import argparse
import json
from pathlib import Path
from export_api_prompts import ROOT, RUN_ID, export

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "data/runs" / RUN_ID)
    args = parser.parse_args()
    print(json.dumps(export(args.run), indent=2))
