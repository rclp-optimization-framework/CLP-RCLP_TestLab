import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ref=ROOT / 'Trash' / 'instances' / 'battery-java-aligned' / 'cork-1-line_battery-java20_0.dzn'
gen=ROOT / 'Trash' / 'instances' / 'generated' / 'cork-1-line_battery-java20_0_generated.dzn'
print('ref exists', ref.exists())
print('gen exists', gen.exists())
if not ref.exists() or not gen.exists():
    raise SystemExit(1)

def nums_from(path):
    text = path.read_text(encoding='utf-8')
    clean = '\n'.join(line.split('%',1)[0] for line in text.splitlines())
    return [int(x) for x in re.findall(r'-?\d+', clean)]

r = nums_from(ref)
g = nums_from(gen)
print('tokens ref', len(r), 'tokens gen', len(g))
if len(r)!=len(g):
    print('Different token lengths')

mismatches = [(i, r[i], g[i]) for i in range(min(len(r), len(g))) if r[i]!=g[i]]
print('mismatch count', len(mismatches))
for i,a,b in mismatches[:20]:
    print('idx', i, 'ref', a, 'gen', b)
