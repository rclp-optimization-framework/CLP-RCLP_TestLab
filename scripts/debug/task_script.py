import sys
import json
from pathlib import Path
from collections import Counter

# Configuration
ROOT = Path(__file__).resolve().parents[2]
input_json = ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line' / 'buses_input_20_0.json'

with open(input_json, 'r') as f:
    data = json.load(f)

# The analyze_t script uses 1-based indexing for buses and stops.
# Let's identify the mismatches. We'll run the analyze_t logic first.
def extract_T(path):
    import re
    text = path.read_text(encoding='utf-8')
    m = re.search(r'% --- Travel Time \(T\) ---.*?T = array2d\(1..(\d+), 1..(\d+), \[', text, re.S)
    if not m: return None, 0, 0
    num_buses, max_stops = int(m.group(1)), int(m.group(2))
    start = m.end()
    end_match = re.search(r'\]\);', text[start:])
    if not end_match: return None, 0, 0
    block = text[start:start+end_match.start()]
    clean = '\n'.join(line.split('%',1)[0] for line in block.splitlines())
    nums = [int(x) for x in re.findall(r'-?\d+', clean)]
    T = [nums[i*max_stops:(i+1)*max_stops] for i in range(num_buses)]
    return T, num_buses, max_stops

ref_path = ROOT / 'Trash' / 'instances' / 'battery-java-aligned' / 'cork-1-line_battery-java20_0.dzn'
gen_path = ROOT / 'Trash' / 'instances' / 'generated' / 'cork-1-line_battery-java20_0_generated.dzn'

if not ref_path.exists() or not gen_path.exists():
    # Try alternate paths if they don't exist
    gen_path = ROOT / 'experiments' / 'instances' / 'Battery-Final' / 'cork-1-line_Battery-Final20_0.dzn'

Tr, nb, ms = extract_T(ref_path)
Tg, _, _ = extract_T(gen_path)

mismatches = []
if Tr and Tg:
    for i in range(nb):
        for j in range(ms):
            if Tr[i][j] != Tg[i][j]:
                mismatches.append((i+1, j+1, Tr[i][j], Tg[i][j]))

# Stop indices in JSON are 0-based for the list of stops.
# In dzn, T[bus, stop] represents the travel time to reach that stop.
# T[b, s] usually corresponds to arrival_time[s] - arrival_time[s-1].

station_mismatches = []
pairs = []

for bus_idx, stop_idx, ref_val, gen_val in mismatches:
    # bus_idx is 1-based, stop_idx is 1-based.
    # In buses_input, 'buses' is a list.
    bus_data = data['buses'][bus_idx - 1]
    stops = bus_data['stops']
    
    # Normally T[bus, stop_idx] is time from stop_idx-1 to stop_idx
    if stop_idx > 1 and stop_idx <= len(stops):
        prev_stop = stops[stop_idx-2]
        curr_stop = stops[stop_idx-1]
        
        prev_station = prev_stop['station_id']
        curr_station = curr_stop['station_id']
        prev_time = prev_stop['arrival_time']
        curr_time = curr_stop['arrival_time']
        
        station_mismatches.append((bus_idx, stop_idx, prev_station, curr_station, prev_time, curr_time, ref_val, gen_val))
        pairs.append((prev_station, curr_station))

print(f"{'Bus':<4} {'Stp':<4} {'Prev':<6} {'Curr':<6} {'P_Time':<7} {'C_Time':<7} {'Ref':<5} {'Gen':<5}")
for m in station_mismatches[:50]:
    print(f"{m[0]:<4} {m[1]:<4} {m[2]:<6} {m[3]:<6} {m[4]:<7} {m[5]:<7} {m[6]:<5} {m[7]:<5}")

print("\nDistinct Station Pairs and Counts:")
counts = Counter(pairs)
for pair, count in counts.most_common():
    print(f"{pair[0]} -> {pair[1]}: {count}")

