"""Verify a finished v2 run and its exports using saved evidence only.

No API client is constructed. The scientific runner and frozen sources are not
modified. Run after report generation, including after a pre-game stop.
"""
import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study.anytime_protocol import AnytimeConfig, manipulation_screen
from beergame_study.anytime_report import analyze, read_csv
from beergame_study.anytime_study import load_calibration


def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def audit(directory):
    directory = Path(directory).resolve()
    before = hashes(directory)
    protocol = json.loads((directory/'manifest.json').read_text(encoding='utf-8'))['protocol']
    run_analyze, run_config, rebuild, run_screen = analyze, AnytimeConfig, load_calibration, manipulation_screen
    if protocol == 'student-high-economy-revision-v3':
        from beergame_study.economy_report import analyze as run_analyze
        from beergame_study.economy_protocol import EconomyConfig as run_config, manipulation_screen as run_screen
        from beergame_study.economy_study import load_calibration as rebuild
    result = run_analyze(directory)
    manifest, progress, records = result['manifest'], result['progress'], result['records']
    if progress['phase'] not in ('stopped', 'complete'):
        raise ValueError('Wait for the live run to finish before auditing.')
    if any(r['status'] == 'pending' for r in records):
        raise ValueError('Unresolved pending request: manual accounting review required.')
    rates = manifest['rates']
    measured_charge = 0.0
    for record in records:
        if record.get('usage_observed'):
            usage = record['usage']
            incoming, cached, outgoing = (usage[k] for k in
                ('input_tokens', 'cached_input_tokens', 'output_tokens'))
            assert 0 <= cached <= incoming and 0 <= usage['reasoning_tokens'] <= outgoing
            expected = ((incoming-cached)*rates['input'] + cached*rates['cached']
                        + outgoing*rates['output']) / 1e6
            if protocol == 'student-high-economy-revision-v3' and record.get('returned_service_tier') != 'flex':
                expected *= 2
            assert math.isclose(expected, record['charge_usd'], abs_tol=1e-12)
            assert record['returned_model'] == manifest['config']['model']
            measured_charge += expected
    calibration_verified = False
    if len(result['calibration']) == 16:
        parent = manifest.get('calibration_source') or directory
        rebuilt = pd.DataFrame(rebuild(parent, run_config(**manifest['config'])))
        pd.testing.assert_frame_equal(result['calibration'], rebuilt, check_dtype=False)
        screen = run_screen(rebuilt.to_dict('records'), synthetic=manifest['config']['mode']=='offline')
        assert screen == result['screen']
        calibration_verified = True
    report = ROOT / 'reports' / directory.name
    for name in ('hypotheses', 'groups', 'roles', 'contrasts', 'calibration', 'probes', 'beta_fits'):
        table = read_csv(report / (name+'.csv'))
        exported = pd.read_excel(report / 'DETAILS.xlsx', sheet_name=name)
        pd.testing.assert_frame_equal(table, exported, check_dtype=False, check_index_type=False,
                                      check_column_type=False)
    from docx import Document
    word_name = 'Economy_Study_Report.docx' if protocol == 'student-high-economy-revision-v3' else 'Anytime_Study_Report.docx'
    word = Document(report / word_name)
    assert word.tables and (report / 'REPORT.md').is_file()
    export_manifest = json.loads((report / 'analysis_manifest.json').read_text(encoding='utf-8'))
    for name, expected in export_manifest['inputs_sha256'].items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest() == expected
    stage_charges = {}
    for record in records:
        stage = record['identity']['stage']
        stage_charges[stage] = stage_charges.get(stage, 0.0) + record.get('charge_usd', 0.0)
    assert hashes(directory) == before, 'Audit changed raw evidence.'
    return dict(passed=True, source_run=str(directory), phase=progress['phase'],
                stopped_reason=progress.get('reason'), api_calls_made_by_audit=0,
                raw_files_unchanged=True, raw_file_count=len(before),
                saved_evidence_audit=result['audit'],
                calibration_rebuilt_from_raw_and_screen_verified=calibration_verified,
                csv_workbook_tables_verified=7, word_tables=len(word.tables),
                request_statuses=dict(Counter(r['status'] for r in records)),
                charge_by_stage_usd=stage_charges, measured_charge_usd=measured_charge,
                charged_or_reserved_usd=result['charge_usd'],
                total_campaign_charged_or_reserved_usd=progress['prior_campaign_spend_usd']+result['charge_usd'],
                calibration_screen=result['screen'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run)
    destination = ROOT / 'reports/software_checks' / (args.run.name+'_audit.json')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    print('Audit:', destination)
