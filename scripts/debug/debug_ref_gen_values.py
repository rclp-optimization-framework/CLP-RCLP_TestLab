from pathlib import Path
import re

def extract_T(path):
    text = path.read_text(encoding='utf-8')
    m = re.search(r"% --- Travel Time \(T\) ---.*?T = array2d\(1..(\d+), 1..(\d+), \[", text, re.S)
    start = m.end()
    end_match = re.search(r"\]\);", text[start:])
    block = text[start:start+end_match.start()]
    clean = '\n'.join(line.split('%',1)[0] for line in block.splitlines())
    nums = [int(x) for x in re.findall(r'-?\d+', clean)]
    num_buses=int(m.group(1)); max_stops=int(m.group(2))
    T=[nums[i*max_stops:(i+1)*max_stops] for i in range(num_buses)]
    return T

ROOT = Path(__file__).resolve().parents[2]
ref_path=ROOT / 'Trash' / 'instances' / 'battery-java-aligned' / 'cork-1-line_battery-java20_0.dzn'
gen_path=ROOT / 'Trash' / 'instances' / 'generated' / 'cork-1-line_battery-java20_0_generated.dzn'
Tr=extract_T(ref_path)
Tg=extract_T(gen_path)
# print some mismatches
pairs=[(1,39),(1,81),(2,19),(3,39),(4,39)]
for b,s in pairs:
    print('Bus',b,'Stop',s,'ref',Tr[b-1][s-1],'gen',Tg[b-1][s-1])
