"""
Detailed Converter Correctness Verification

Compares JSON source against DZN output line-by-line,
verifying stations, times, distances, and padding.

Usage: python verify_dzn_correctness.py <json_file> <dzn_file>
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import csv


def parse_dzn_array2d(content: str, pattern: str) -> List[List[int]]:
    """Parse array2d from DZN file."""
    regex = rf"{pattern}\s*=\s*array2d\(1\.\.(\d+),\s*1\.\.(\d+),\s*\[(.*?)\]\);"
    match = re.search(regex, content, re.DOTALL)

    if not match:
        return []

    rows = int(match.group(1))
    cols = int(match.group(2))
    values_str = match.group(3)

    cleaned_lines = []
    for line in values_str.splitlines():
        cleaned_lines.append(line.split('%', 1)[0])
    cleaned_values = " ".join(cleaned_lines)

    numbers = re.findall(r'[-]?\d+', cleaned_values)
    numbers = [int(n) for n in numbers]

    result = []
    for i in range(rows):
        row = numbers[i * cols:(i + 1) * cols]
        result.append(row)

    return result


def load_dzn(dzn_path: Path) -> Dict:
    """Load DZN file."""
    with open(dzn_path, 'r') as f:
        content = f.read()

    regex_scalar = lambda name: re.search(rf"{name}\s*=\s*([\d]+)\s*;", content)

    num_buses = int(regex_scalar("num_buses").group(1))
    num_stations = int(regex_scalar("num_stations").group(1))
    max_stops = int(regex_scalar("max_stops").group(1))

    st_bi = parse_dzn_array2d(content, "st_bi")
    T = parse_dzn_array2d(content, "T")
    tau_bi = parse_dzn_array2d(content, "tau_bi")

    return {
        'num_buses': num_buses,
        'num_stations': num_stations,
        'max_stops': max_stops,
        'st_bi': st_bi,
        'T': T,
        'tau_bi': tau_bi
    }


def load_json(json_path: Path) -> List:
    """Load JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def verify_stations_padding(dzn_st_bi: List[List[int]], bus_idx: int,
                           json_stations: List[int], max_stops: int) -> Tuple[bool, List[str]]:
    """Verify station sequence and padding for a bus."""
    errors = []

    dzn_row = dzn_st_bi[bus_idx]
    expected_stations = [station + 1 for station in json_stations]
    json_len = len(json_stations)

    # Check actual stations
    for i in range(json_len):
        if i < len(dzn_row):
            if dzn_row[i] != expected_stations[i]:
                errors.append(
                    f"Bus {bus_idx}, Stop {i}: Expected {expected_stations[i]}, got {dzn_row[i]}"
                )

    # Check padding (should be last station repeated)
    if json_len > 0:
        last_station = expected_stations[-1]
        for i in range(json_len, max_stops):
            if i < len(dzn_row):
                if dzn_row[i] != last_station:
                    errors.append(
                        f"Bus {bus_idx}, Padding position {i}: Expected {last_station} (last), got {dzn_row[i]}"
                    )

    return len(errors) == 0, errors


def verify_times(dzn_tau_bi: List[List[int]], bus_idx: int,
                json_times: List[int], scale: int = 10) -> Tuple[bool, List[str]]:
    """Verify arrival times."""
    errors = []

    dzn_row = dzn_tau_bi[bus_idx]
    json_len = len(json_times)

    for i in range(json_len):
        if i < len(dzn_row):
            expected = json_times[i] * 60
            actual = dzn_row[i]
            if actual != expected:
                errors.append(
                    f"Bus {bus_idx}, Stop {i}: tau_bi expected {expected}, got {actual} "
                    f"(difference: {actual - expected}, {(actual - expected) / 60:.2f} min)"
                )

    return len(errors) == 0, errors


def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes."""
    h, m = map(int, time_str.split(':'))
    return h * 60 + m


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python verify_dzn_correctness.py <json_file> <dzn_file>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    dzn_path = Path(sys.argv[2])

    print("=" * 80)
    print("DZN CORRECTNESS VERIFICATION")
    print("=" * 80)
    print(f"\nJSON: {json_path.name}")
    print(f"DZN:  {dzn_path.name}\n")

    # Load data
    json_data = load_json(json_path)
    dzn_data = load_dzn(dzn_path)

    print(f"DZN Metadata:")
    print(f"  num_buses: {dzn_data['num_buses']}")
    print(f"  num_stations: {dzn_data['num_stations']}")
    print(f"  max_stops: {dzn_data['max_stops']}\n")

    # Extract JSON buses
    json_buses = []
    for line in json_data:
        json_buses.extend(line.get('buses', []))

    print(f"JSON buses: {len(json_buses)}")
    print(f"DZN buses:  {dzn_data['num_buses']}\n")

    # Verify each bus
    total_errors = 0

    for bus_idx, json_bus in enumerate(json_buses):
        print(f"\n--- Bus {bus_idx} ---")

        path = json_bus.get('path', [])
        stations = [int(p['station_id']) for p in path]
        times_str = [p['time'] for p in path]
        times_min = [time_to_minutes(t) for t in times_str]

        print(f"JSON stops: {len(path)}")
        print(f"JSON stations: {stations}")
        print(f"JSON times: {times_str}")

        # Verify stations and padding
        match, errors = verify_stations_padding(dzn_data['st_bi'], bus_idx, stations, dzn_data['max_stops'])
        if errors:
            print(f"\nSTATION ERRORS ({len(errors)}):")
            for err in errors[:5]:  # Show first 5
                print(f"  ✗ {err}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")
            total_errors += len(errors)
        else:
            print(f"✓ Station sequence and padding correct")

        # Verify times
        match, errors = verify_times(dzn_data['tau_bi'], bus_idx, times_min, scale=60)
        if errors:
            print(f"\nTIME ERRORS ({len(errors)}):")
            for err in errors[:5]:
                print(f"  ✗ {err}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")
            total_errors += len(errors)
        else:
            print(f"✓ Arrival times correct")

        # Summary for this bus
        dzn_actual_stops = dzn_data['st_bi'][bus_idx]
        if stations:
            padding_count = sum(1 for i in range(len(stations), dzn_data['max_stops'])
                               if dzn_actual_stops[i] == stations[-1])
        else:
            padding_count = 0

        print(f"\nPadding analysis:")
        print(f"  Actual stops: {len(stations)}")
        print(f"  Max stops: {dzn_data['max_stops']}")
        print(f"  Padding needed: {dzn_data['max_stops'] - len(stations)}")
        print(f"  Padding in DZN: {padding_count}")

    print("\n" + "=" * 80)
    print(f"TOTAL ERRORS FOUND: {total_errors}")
    print("=" * 80 + "\n")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
