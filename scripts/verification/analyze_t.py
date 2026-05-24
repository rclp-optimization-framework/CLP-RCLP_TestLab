from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

def extract_T(path):
    text = path.read_text(encoding='utf-8')
    # find T block
    m = re.search(r"% --- Travel Time \(T\) ---.*?T = array2d\(1..(\d+), 1..(\d+), \[", text, re.S)
    if not m:
        raise SystemExit('T block not found')
    num_buses = int(m.group(1))
    max_stops = int(m.group(2))
    # find start of [
    start = m.end()
    # find closing ']);' after start
    end_match = re.search(r"\]\);", text[start:])
    if not end_match:
        raise SystemExit('T array end not found')
    block = text[start:start+end_match.start()]
    # remove comments and non-numeric
    clean = '\n'.join(line.split('%',1)[0] for line in block.splitlines())
    nums = [int(x) for x in re.findall(r'-?\d+', clean)]
    if len(nums) != num_buses * max_stops:
        raise SystemExit(f'Unexpected T length: {len(nums)} vs {num_buses*max_stops}')
    # reshape
    T = [nums[i*max_stops:(i+1)*max_stops] for i in range(num_buses)]
    return T, num_buses, max_stops

ref=ROOT / 'Trash' / 'instances' / 'battery-java-aligned' / 'cork-1-line_battery-java20_0.dzn'
gen=ROOT / 'Trash' / 'instances' / 'generated' / 'cork-1-line_battery-java20_0_generated.dzn'
Tr, nb, ms = extract_T(ref)
Tg, _, _ = extract_T(gen)

mismatches=[]
for i in range(nb):
    for j in range(ms):
        if Tr[i][j] != Tg[i][j]:
            mismatches.append((i+1,j+1,Tr[i][j],Tg[i][j]))

print('mismatches', len(mismatches))
for item in mismatches[:100]:
    print('Bus',item[0],'Stop',item[1],'ref',item[2],'gen',item[3])
