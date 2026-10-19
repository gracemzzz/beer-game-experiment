"""Compatibility entry point: the one current H1-H4 report lives in CURRENT_BEER_GAME."""
import argparse
from pathlib import Path
from build_current_report import main

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path)
    parser.add_argument('--analysis')
    args=parser.parse_args()
    if args.run is not None and args.run.name!='deadline_cohort_2800524c9b2e0729':
        parser.error('This publication is pinned to the completed website sample.')
    if args.analysis is not None and args.analysis!='daa53a7e838a':
        parser.error('Use the original completed analysis signature.')
    main()
