import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
p=ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line' / 'buses_input_20_0.json'
with p.open('r',encoding='utf-8') as f:
    data=json.load(f)
path=data[0]['buses'][0]['path']
for idx in [39,40]:
    s=path[idx-1]
    print('stop',idx,'station',s['station_id'],'time',s['time'],'rest',s.get('rest',False))
from core.converter.core.data_loader import DataLoader
input_folder=ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line'
distances,n=DataLoader.load_distances(input_folder)
prev=path[38]['station_id']
curr=path[39]['station_id']
print('prev,curr',prev,curr,'distance dict has key?', (prev,curr) in distances)
print('distance value:', distances.get((prev,curr)))
