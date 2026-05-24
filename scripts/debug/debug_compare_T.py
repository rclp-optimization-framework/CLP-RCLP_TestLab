import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def extract_T(path):
    text=Path(path).read_text(encoding='utf-8')
    m=re.search(r"T = array2d\(1..(\d+), 1..(\d+), \[", text, re.S)
    start=m.end()
    end=text.find(']);', start)
    block=text[start:end]
    clean='\n'.join(line.split('%',1)[0] for line in block.splitlines())
    nums=[int(x) for x in re.findall(r'-?\d+', clean)]
    num_buses=int(m.group(1)); max_stops=int(m.group(2))
    T=[nums[i*max_stops:(i+1)*max_stops] for i in range(num_buses)]
    return T

ref=extract_T(ROOT / 'Trash' / 'instances' / 'battery-java-aligned' / 'cork-1-line_battery-java20_0.dzn')
gen=extract_T(ROOT / 'Trash' / 'instances' / 'generated' / 'cork-1-line_battery-java20_0_generated.dzn')
# bus 1 stop 25 -> index 24
b=0; s=24
print('ref', ref[b][s])
print('gen', gen[b][s])
print('neighboring gen', gen[b][22:27])
print('neighboring ref', ref[b][22:27])
