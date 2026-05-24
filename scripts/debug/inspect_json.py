import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
p=ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line' / 'buses_input_20_0.json'
with p.open('r',encoding='utf-8') as f:
    data=json.load(f)
line0 = data[0]
buses=line0.get('buses',[])
print('num buses in first line', len(buses))
bus=buses[0]
path=bus.get('path',[])
stations=[stop.get('station_id') for stop in path]
times=[stop.get('time') for stop in path]
print('stops count',len(stations))
for sidx in [25,39,67,81,105]:
    if sidx-1 < len(stations):
        print('stop',sidx,'station',stations[sidx-1],'time',times[sidx-1])
    else:
        print('stop',sidx,'out of range')
