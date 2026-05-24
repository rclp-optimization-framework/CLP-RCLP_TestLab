from core.converter.core.data_loader import DataLoader
from core.converter.core.converter_engine import ConverterEngine
import json
from pathlib import Path

input_folder=Path('external/jits2022/Code/data/cork-1-line')
distances,_=DataLoader.load_distances(input_folder)
line0=json.loads(Path('external/jits2022/Code/data/cork-1-line/buses_input_20_0.json').read_text(encoding='utf-8'))[0]
conv=ConverterEngine(distances_dict=distances)
processed=conv.process_bus_line(line0)
bus=processed[0]
idx=39
print('station_ids around', bus['station_ids'][idx-3:idx+2])
print('times around', bus['times'][idx-3:idx+2])
print('rest flags around', bus['rest_flags'][idx-3:idx+2])
print('T values around', bus['time_deltas_seconds'][idx-3:idx+1])
for j in range(idx-3, idx+2):
    s=line0['buses'][0]['path'][j]
    print(j+1, s)
