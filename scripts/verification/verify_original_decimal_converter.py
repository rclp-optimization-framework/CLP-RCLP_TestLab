#!/usr/bin/env python3
"""
Original Decimal Converter Verification

Generates DZN files using the original decimal output mode and verifies that
station mapping, travel times, and energy values match the source JSON/CSV data
without normalization or precision loss.

Usage:
    python scripts/verification/verify_original_decimal_converter.py <instance_dir>

Example:
    python scripts/verification/verify_original_decimal_converter.py external/jits2022/Code/data/cork-1-line
"""

from __future__ import annotations

import json
import logging
import re
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.data_loader import DataLoader
from core.converter.core.experiment_config import ExperimentConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_json_buses(json_path: Path) -> List[dict]:
    with open(json_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    buses: List[dict] = []
    for line_data in data:
        buses.extend(line_data.get("buses", []))
    return buses


def parse_dzn_numbers(content: str, name: str) -> List[List[Decimal]]:
    pattern = rf"{name}\s*=\s*array2d\(1\.\.(\d+),\s*1\.\.(\d+),\s*\[(.*?)\]\);"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []

    rows = int(match.group(1))
    cols = int(match.group(2))
    raw_values = match.group(3)
    cleaned_values = "\n".join(line.split("%", 1)[0] for line in raw_values.splitlines())

    numbers = re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", cleaned_values)
    values = [Decimal(number) for number in numbers]

    matrix: List[List[Decimal]] = []
    for row_index in range(rows):
        start = row_index * cols
        end = start + cols
        matrix.append(values[start:end])
    return matrix


def parse_scalar(content: str, name: str) -> Decimal:
    match = re.search(rf"{name}\s*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*;", content)
    if not match:
        raise ValueError(f"Could not find scalar {name} in DZN content")
    return Decimal(match.group(1))


def minutes_from_hhmm(time_str: str) -> int:
    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes


def build_expected_values(buses: List[dict], distances: Dict[Tuple[int, int], Decimal]) -> Tuple[List[List[int]], List[List[int]], List[List[int]], List[List[Decimal]]]:
    station_ids = sorted({stop["station_id"] for bus in buses for stop in bus.get("path", [])})
    station_to_index = {station_id: index + 1 for index, station_id in enumerate(station_ids)}
    max_stops = max(len(bus.get("path", [])) for bus in buses)

    expected_st_bi: List[List[int]] = []
    expected_T: List[List[int]] = []
    expected_tau_bi: List[List[int]] = []
    expected_D: List[List[Decimal]] = []

    for bus in buses:
        path = bus.get("path", [])
        stations = [station_to_index[stop["station_id"]] for stop in path]
        schedule_minutes = [minutes_from_hhmm(stop["time"]) for stop in path]

        travel_times = [0]
        for index in range(1, len(path)):
            delta = schedule_minutes[index] - schedule_minutes[index - 1]
            if delta <= 0:
                delta = 1
            if path[index - 1].get("rest", False):
                delta += 10
            travel_times.append(delta)

        energy_values: List[Decimal] = [Decimal("0")]
        for index in range(1, len(path)):
            prev_station = path[index - 1]["station_id"]
            curr_station = path[index]["station_id"]
            distance_km = distances.get((prev_station, curr_station), Decimal("0"))
            if not isinstance(distance_km, Decimal):
                distance_km = Decimal(str(distance_km))
            energy_values.append(distance_km * Decimal("0.25"))

        padded_stations = stations + ([stations[-1]] * (max_stops - len(stations)) if stations else [])
        padded_times = travel_times + [0] * (max_stops - len(travel_times))
        padded_schedule = schedule_minutes + ([schedule_minutes[-1]] * (max_stops - len(schedule_minutes)) if schedule_minutes else [])
        padded_energy = energy_values + [Decimal("0")] * (max_stops - len(energy_values))

        expected_st_bi.append(padded_stations)
        expected_T.append(padded_times)
        expected_tau_bi.append(padded_schedule)
        expected_D.append(padded_energy)

    return expected_st_bi, expected_T, expected_tau_bi, expected_D


def verify_instance(instance_dir: Path, pattern: str = "buses_input_*.json") -> Tuple[bool, List[str]]:
    errors: List[str] = []
    json_files = sorted(instance_dir.glob(pattern))
    if not json_files:
        return False, [f"No JSON files found in {instance_dir} matching {pattern}"]

    config = ExperimentConfig()
    distances, _ = DataLoader.load_distances(instance_dir, preserve_precision=True)

    with tempfile.TemporaryDirectory(prefix="converter-original-") as temp_dir:
        output_dir = Path(temp_dir)
        success_count, failure_count, messages = ConverterEngine.batch_convert_files(
            json_files=json_files,
            output_dir=output_dir,
            source_dir_name=instance_dir.name,
            config=config,
            distances_dict=distances,
            output_format="original",
        )

        if failure_count:
            errors.append("Conversion reported failures:")
            errors.extend(messages)
            return False, errors

        for json_file in json_files:
            output_subdir = output_dir / instance_dir.name
            base_suffix = json_file.stem.replace("buses_input", "").strip("_")
            candidates = sorted(output_subdir.glob(f"*{base_suffix}.dzn"))
            if not candidates:
                errors.append(f"Missing DZN output for {json_file.name} in {output_subdir}")
                continue

            output_file = candidates[0]

            buses = load_json_buses(json_file)
            content = output_file.read_text(encoding="utf-8")

            try:
                num_buses = int(parse_scalar(content, "num_buses"))
                num_stations = int(parse_scalar(content, "num_stations"))
                max_stops = int(parse_scalar(content, "max_stops"))
            except Exception as exc:
                errors.append(f"{json_file.name}: could not parse metadata ({exc})")
                continue

            expected_st_bi, expected_T, expected_tau_bi, expected_D = build_expected_values(buses, distances)
            unique_station_count = len({stop["station_id"] for bus in buses for stop in bus.get("path", [])})

            if num_buses != len(buses):
                errors.append(f"{json_file.name}: expected {len(buses)} buses, got {num_buses}")
            if num_stations != unique_station_count:
                errors.append(f"{json_file.name}: expected {unique_station_count} stations, got {num_stations}")
            if max_stops != max(len(bus.get("path", [])) for bus in buses):
                errors.append(f"{json_file.name}: max_stops mismatch")

            if "ORIGINAL DECIMAL VALUES" not in content:
                errors.append(f"{json_file.name}: original decimal format marker not found in DZN header")

            dzn_st_bi = parse_dzn_numbers(content, "st_bi")
            dzn_T = parse_dzn_numbers(content, "T")
            dzn_tau_bi = parse_dzn_numbers(content, "tau_bi")
            dzn_D = parse_dzn_numbers(content, "D")

            if dzn_st_bi != [[Decimal(value) for value in row] for row in expected_st_bi]:
                errors.append(f"{json_file.name}: station mapping mismatch")
            if dzn_T != [[Decimal(value) for value in row] for row in expected_T]:
                errors.append(f"{json_file.name}: travel time mismatch")
            if dzn_tau_bi != [[Decimal(value) for value in row] for row in expected_tau_bi]:
                errors.append(f"{json_file.name}: schedule time mismatch")
            if dzn_D != expected_D:
                errors.append(f"{json_file.name}: energy values mismatch")

    return len(errors) == 0, errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/verification/verify_original_decimal_converter.py <instance_dir>")
        return 1

    instance_dir = Path(sys.argv[1])
    if not instance_dir.exists():
        print(f"Instance directory not found: {instance_dir}")
        return 1

    ok, errors = verify_instance(instance_dir)
    print("=" * 80)
    print("ORIGINAL DECIMAL CONVERTER VERIFICATION")
    print("=" * 80)
    print(f"Instance directory: {instance_dir}")
    print(f"Status: {'PASS' if ok else 'FAIL'}")

    if not ok:
        print("\nIssues:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("All checked instances matched the original decimal expectations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
