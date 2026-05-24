from pathlib import Path
import json
import math

from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.data_loader import DataLoader
from core.converter.core.experiment_config import ExperimentConfig


def inspect_segment(conv: ConverterEngine, bus, seg_idx: int) -> None:
    station_ids = bus['station_ids']
    times = bus['times']
    rest_flags = bus['rest_flags']

    prev = station_ids[seg_idx - 1]
    curr = station_ids[seg_idx]
    raw_distance = conv.distances_dict.get((prev, curr), 0)
    distance_m = float(raw_distance)
    energy_int = int(distance_m)

    delta_minutes = times[seg_idx] - times[seg_idx - 1]
    delta_seconds = int(delta_minutes * 60)
    time_needed = 30 if delta_seconds == 0 else delta_seconds

    min_speed_mps = (conv.MIN_SPEED_KMH * 1000.0) / 3600.0
    max_speed_mps = (conv.MAX_SPEED_KMH * 1000.0) / 3600.0

    required_speed = None
    segment_speed = None
    if energy_int == 0:
        seg_time = 0
    else:
        required_speed = float(energy_int) / float(time_needed) if time_needed != 0 else max_speed_mps
        required_speed = min(required_speed, max_speed_mps)
        segment_speed = max(required_speed, min_speed_mps)
        seg_time = int(round(float(energy_int) / segment_speed))

    if rest_flags[seg_idx - 1]:
        seg_time += int(conv.REST_TIME_SECONDS)

    post_bucket = int(math.ceil(float(seg_time) / 60.0)) * 60 if seg_time > 0 else 0
    repeated = curr == prev and times[seg_idx] == times[seg_idx - 1]
    if repeated:
        post_bucket = 0

    print(f"--- Segment index {seg_idx} ---")
    print("prev_station", prev, "curr_station", curr)
    print("prev_time", times[seg_idx - 1], "curr_time", times[seg_idx])
    print("delta_seconds", delta_seconds, "time_needed", time_needed)
    print("rest_prev", rest_flags[seg_idx - 1], "repeated_stop", repeated)
    print("raw_distance", raw_distance, "distance_m", distance_m, "energy_int", energy_int)
    print("required_speed", required_speed, "segment_speed", segment_speed)
    print("seg_time_before_bucket", seg_time, "seg_time_after_bucket", post_bucket)
    print()


if __name__ == '__main__':
    ROOT = Path(__file__).resolve().parents[2]
    input_folder = ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line'
    distances, _ = DataLoader.load_distances(input_folder)
    cfg = ExperimentConfig(model_speed=20, rest_time=10)
    conv = ConverterEngine(config=cfg, distances_dict=distances)

    json_file = input_folder / 'buses_input_20_0.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    line = data[0]
    processed = conv.process_bus_line(line)
    bus = processed[0]

    for idx in (39, 81, 123):
        inspect_segment(conv, bus, idx)
