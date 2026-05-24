from core.converter.core.data_loader import DataLoader
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
input_folder=ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line'
distances,_=DataLoader.load_distances(input_folder)
line0=json.loads((ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line' / 'buses_input_20_0.json').read_text(encoding='utf-8'))[0]
path=line0['buses'][0]['path']
# list of stop indices to inspect (1-based from analyze)
indices=[39,81,123,165]
for idx in indices:
    prev=path[idx-2]['station_id']
    curr=path[idx-1]['station_id']
    raw=distances.get((prev,curr),0)
    if isinstance(raw, float) or isinstance(raw,int):
        dist_m=float(raw)
    else:
        from decimal import Decimal
        dist_m=float(raw*Decimal('1000'))
    energy_int=int(round(dist_m))
    print('Stop',idx,'prev',prev,'curr',curr,'dist_m',dist_m,'energy_int',energy_int)
