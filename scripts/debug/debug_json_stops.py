import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
json_file = ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line' / 'buses_input_20_0.json'
with open(json_file,'r',encoding='utf-8') as f:
    data = json.load(f)

line = data[0]
bus = line['buses'][0]
path = bus['path']
indices = [38,80,122,164,206,248,290,332]  # zero-based indices for stops 39,81,...
for idx in indices:
    stop = path[idx]
    prev = path[idx-1]
    print('Index', idx+1)
    print('prev:', prev)
    print('stop:', stop)
    print('---')
