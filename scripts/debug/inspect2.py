import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
p=ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line' / 'buses_input_20_0.json'
with p.open('r',encoding='utf-8') as f:
    data=json.load(f)
path=data[0]['buses'][0]['path']
for idx in [37,38,39,40,41]:
    s=path[idx-1]
    print(idx, s['station_id'], s['time'], s.get('rest',False))
