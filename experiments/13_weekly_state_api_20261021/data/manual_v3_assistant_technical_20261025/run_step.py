import contextlib
import io
import json
import pickle
import sys
from pathlib import Path
from beergame_controller import WebsiteGame

folder = Path(__file__).resolve().parent
state_file = folder / 'session.pkl'
log_file = folder / 'transcript.txt'
snippet = sys.stdin.read()
namespace = {'json': json, 'Path': Path, 'WebsiteGame': WebsiteGame}
if state_file.exists():
    namespace['game'] = pickle.loads(state_file.read_bytes())
buffer = io.StringIO()
try:
    with contextlib.redirect_stdout(buffer):
        exec(compile(snippet, '<literal_step>', 'exec'), namespace)
finally:
    output = buffer.getvalue()
    if 'game' in namespace:
        state_file.write_bytes(pickle.dumps(namespace['game']))
    with log_file.open('a', encoding='utf-8', newline='') as transcript:
        transcript.write('INPUT\n' + snippet + '\nOUTPUT\n' + output + '\n')
    print(output, end='')
