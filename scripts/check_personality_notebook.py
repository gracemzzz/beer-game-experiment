"""Execute notebook 04 or 05 in memory, including its full offline example."""
import argparse
import ast
import asyncio
from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import nbformat

ROOT = Path(__file__).resolve().parents[1]


async def main(number):
    filename = {'04':'04_personality_deliberation_study.ipynb', '05':'05_claude_deliberation_study.ipynb'}[number]
    path = ROOT/'notebooks'/filename
    before = path.read_bytes()
    notebook = nbformat.read(path, as_version=4)
    scope = {'__name__':'__notebook_check__'}
    count = 0
    pointer_names = ('ACTIVE_ECONOMY_RUN.json', 'LATEST_ECONOMY_REPORT.json', 'ACTIVE_CLAUDE_RUN.json',
                     'LATEST_CLAUDE_REPORT.json', 'LATEST_REPORT.txt')
    pointers = {ROOT/'reports'/name: (ROOT/'reports'/name).read_bytes() if (ROOT/'reports'/name).exists() else None
                for name in pointer_names}
    try:
        with patch('openai.AsyncOpenAI', side_effect=AssertionError('Live clients forbidden during notebook verification')), \
             patch('anthropic.AsyncAnthropic', side_effect=AssertionError('Live clients forbidden during notebook verification')):
            for index, cell in enumerate(notebook.cells):
                if cell.cell_type != 'code':
                    continue
                result = eval(compile(cell.source, f'notebook-cell-{index}', 'exec',
                                      flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT), scope)
                if inspect.isawaitable(result):
                    await result
                if 'RUN_OFFLINE_CHECK = False' in cell.source:
                    scope['RUN_OFFLINE_CHECK'] = True
                    scope['WATCH_RUNNING'] = False
                    scope['REPLICATE_ID'] = 'notebook-check-' + uuid4().hex[:12]
                    scope['config'] = replace(scope['config'], mode='offline', replicate_id=scope['REPLICATE_ID'])
                count += 1
    finally:
        for pointer, data in pointers.items():
            if data is None:
                pointer.unlink(missing_ok=True)
            else:
                pointer.write_bytes(data)
    assert path.read_bytes() == before
    result = dict(passed=True, code_cells=count, offline_full_campaign_executed=True,
                  api_client_constructions=0, notebook_unchanged=True, active_report_pointers_restored=True,
                  source_run=str(scope['OFFLINE_RUN']), pairs=scope['config'].groups_per_condition,
                  sha256=hashlib.sha256(before).hexdigest())
    output = ROOT/'reports/software_checks'/f'notebook{number}_cross_provider_20261011.json'
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook', choices=['04', '05'], default='04')
    asyncio.run(main(parser.parse_args().notebook))
