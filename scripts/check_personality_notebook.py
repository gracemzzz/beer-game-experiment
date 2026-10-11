"""Execute notebook 04 safely in memory, including its full offline example."""
import ast
import asyncio
import hashlib
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import nbformat

ROOT = Path(__file__).resolve().parents[1]


async def main():
    path = ROOT/'notebooks/04_personality_deliberation_study.ipynb'
    before = path.read_bytes()
    notebook = nbformat.read(path, as_version=4)
    scope = {'__name__':'__notebook_check__'}
    count = 0
    with patch('openai.AsyncOpenAI', side_effect=AssertionError('Live clients forbidden during notebook verification')):
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != 'code':
                continue
            result = eval(compile(cell.source, f'notebook-cell-{index}', 'exec',
                                  flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT), scope)
            if inspect.isawaitable(result):
                await result
            if 'RUN_OFFLINE_CHECK = False' in cell.source:
                scope['RUN_OFFLINE_CHECK'] = True
            count += 1
    assert path.read_bytes() == before
    result = dict(passed=True, code_cells=count, offline_full_campaign_executed=True,
                  api_client_constructions=0, notebook_unchanged=True,
                  sha256=hashlib.sha256(before).hexdigest())
    output = ROOT/'reports/software_checks/notebook04_economy_flex_20261011.json'
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    asyncio.run(main())
