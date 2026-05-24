from core.converter.core.converter_engine import ConverterEngine
from pathlib import Path
import json

mismatches = [
    (1,39),(1,81),(1,123),(1,165),(1,207),(1,249),(1,291),(1,333),(1,375),(1,417),(1,459),(1,501),(1,543),
    (2,19),(2,61),(2,103),(2,145),(2,187),(2,229),(2,271),(2,313),(2,355),(2,397),(2,439),(2,481),(2,523),(2,565),
    (3,39),(3,81),(3,123),(3,165),(3,207),(3,249),(3,291),(3,333),(3,375),
    (4,39),(4,81),(4,123),(4,165),(4,207),(4,249),(4,291),(4,333)
]

from core.converter.core.data_loader import DataLoader

ROOT = Path(__file__).resolve().parents[2]
input_folder = ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line'
distances, _ = DataLoader.load_distances(input_folder)
engine = ConverterEngine(distances_dict=distances)
json_file = ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line' / 'buses_input_20_0.json'
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

line = data[0]
processed = engine.process_bus_line(line)

for bus_no, stop_idx in mismatches:
    bus_idx = bus_no - 1
    i = stop_idx
    bus = processed[bus_idx]
    station_ids = bus['station_ids']
    times = bus['times']
    rest_flags = bus['rest_flags']
    prev = station_ids[i-1]
    curr = station_ids[i]
    # distances
    raw_distance = engine.distances_dict.get((prev, curr), 0)
    distance_m = float(raw_distance)
    energy_int = int(round(distance_m))
    delta_minutes = times[i] - times[i-1]
    delta_seconds = int(delta_minutes * 60)
    # recompute seg_time per current code
    if delta_seconds <= 0:
        time_needed = 30
    else:
        time_needed = delta_seconds
    if energy_int == 0:
        seg_time = 0
    else:
        required_speed = distance_m / float(time_needed) if time_needed > 0 else engine.MAX_SPEED_KMH
        # convert km/h min/max? here distances in meters, speeds in m/s
        min_speed_mps = (engine.MIN_SPEED_KMH * 1000.0) / 3600.0
        max_speed_mps = (engine.MAX_SPEED_KMH * 1000.0) / 3600.0
        required_speed = min(required_speed, max_speed_mps)
        segment_speed = max(required_speed, min_speed_mps)
        seg_time = int(round(distance_m / segment_speed))
    if rest_flags[i-1]:
        seg_time += int(engine.REST_TIME_SECONDS)
    # bucket using ceil
    if seg_time > 0:
        import math
        bucketed = int(math.ceil(float(seg_time)/60.0))*60
    else:
        bucketed = 0
    print(f"Bus {bus_no} Stop {stop_idx}: prev={prev} curr={curr} dist={distance_m} energy={energy_int} delta_s={delta_seconds} rest_prev={rest_flags[i-1]} seg_time_raw={seg_time} bucketed={bucketed}")
