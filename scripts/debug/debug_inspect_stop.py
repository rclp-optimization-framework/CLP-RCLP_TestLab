from core.converter.core.converter_engine import ConverterEngine
import json
from pathlib import Path

json_file=Path('external/jits2022/Code/data/cork-1-line/buses_input_20_0.json')
with json_file.open('r',encoding='utf-8') as f:
    data=json.load(f)
line0=data[0]
conv=ConverterEngine()
processed=conv.process_bus_line(line0)
# Bus index 0, stop index 25 -> T_values list index 25
bus=processed[0]
idx=25
print('station_ids around', bus['station_ids'][idx-2:idx+3])
print('times around', bus['times'][idx-2:idx+3])
print('rest flags around', bus['rest_flags'][idx-2:idx+3])
print('T values around', bus['time_deltas_seconds'][idx-2:idx+2])
print('Specific T at idx-1 (segment from stop24->25):', bus['time_deltas_seconds'][idx-1])
print('Specific T at idx (segment from stop25->26):', bus['time_deltas_seconds'][idx])

# Print JSON for stops 24,25,26
path=line0['buses'][0]['path']
for j in range(idx-2, idx+3):
    s=path[j]
    print(j+1, s)
