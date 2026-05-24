#!/usr/bin/env python3
"""
================================================================================
Synthetic Data Generator for Battery Own Test Cases
================================================================================

Generates synthetic test cases with varying complexity for testing the CLP model.

Author: EV-CLP Battery Project
Date: 2026-03-25
================================================================================
"""

import random
from pathlib import Path
import logging

SCALE = 10

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def generate_test_case(num_buses: int, num_stations: int, max_stops: int, output_file: Path):
    """Generate a synthetic test case."""

    logger.info(f"Generating {output_file.name}: {num_buses} buses, {num_stations} stations, max {max_stops} stops")

    # Generate random routes
    num_stops_list = []
    st_bi = []
    D = []
    T = []
    tau_bi = []

    for bus_idx in range(num_buses):
        # Random number of stops for this bus
        stops = random.randint(max(3, max_stops // 2), max_stops)
        num_stops_list.append(stops)

        # Generate random station sequence
        route = [0]  # Start at station 0
        for _ in range(stops - 1):
            next_station = random.randint(0, num_stations - 1)
            route.append(next_station)

        # Pad to max_stops
        route += [route[-1]] * (max_stops - len(route))
        st_bi.extend(route)

        # Generate energy consumption (scaled integers)
        energy = [0]  # First stop has 0 consumption
        for _ in range(stops - 1):
            energy.append(random.randint(1, 5) * SCALE)  # 1-5 kWh scaled
        energy += [0] * (max_stops - len(energy))
        D.extend(energy)

        # Generate travel times (scaled integers)
        times = [0]  # First stop has 0 time
        for _ in range(stops - 1):
            times.append(random.randint(5, 20) * SCALE)  # 5-20 minutes scaled
        times += [0] * (max_stops - len(times))
        T.extend(times)

        # Generate schedule (scaled integers)
        schedule = [420 * SCALE]  # Start at 7:00 AM
        current_time = schedule[0]
        for i in range(1, stops):
            current_time += times[i] + random.randint(0, 2) * SCALE  # Add some dwell time
            schedule.append(current_time)
        schedule += [schedule[-1]] * (max_stops - len(schedule))
        tau_bi.extend(schedule)

    # Write DZN file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("% " + "=" * 76 + "\n")
        f.write(f"% Synthetic Test Case: {output_file.stem}\n")
        f.write("% " + "=" * 76 + "\n")
        f.write("% AUTO-GENERATED for testing purposes\n")
        f.write("% All values are INTEGERS scaled by ×10\n")
        f.write("% " + "=" * 76 + "\n\n")

        f.write("% --- Problem Dimensions ---\n")
        f.write(f"num_buses = {num_buses};\n")
        f.write(f"num_stations = {num_stations};\n\n")

        f.write("% --- Energy Parameters (Scaled ×10) ---\n")
        f.write(f"Cmax = {100 * SCALE};  % 100 kWh\n")
        f.write(f"Cmin = {20 * SCALE};   % 20 kWh\n")
        f.write(f"alpha = {10 * SCALE};  % 10 kWh/min\n\n")

        f.write("% --- Time Parameters (Scaled ×10) ---\n")
        f.write(f"mu = {5 * SCALE};\n")
        f.write(f"SM = {1 * SCALE};\n")
        f.write(f"psi = {1 * SCALE};\n")
        f.write(f"beta = {10 * SCALE};\n")
        f.write(f"M = {10000 * SCALE};\n\n")

        f.write("% --- Route Structure ---\n")
        f.write(f"max_stops = {max_stops};\n")
        f.write(f"num_stops = {num_stops_list};\n\n")

        # Write arrays
        f.write("% --- Station Sequence (st_bi) ---\n")
        f.write(f"st_bi = array2d(1..{num_buses}, 1..{max_stops}, [\n")
        for i in range(num_buses):
            start = i * max_stops
            end = start + max_stops
            values = st_bi[start:end]
            f.write("  " + ",".join(map(str, values)) + ("," if i < num_buses - 1 else "") + f"  % Bus {i+1}\n")
        f.write("]);\n\n")

        f.write("% --- Energy Consumption (D) ---\n")
        f.write(f"D = array2d(1..{num_buses}, 1..{max_stops}, [\n")
        for i in range(num_buses):
            start = i * max_stops
            end = start + max_stops
            values = D[start:end]
            f.write("  " + ",".join(map(str, values)) + ("," if i < num_buses - 1 else "") + f"  % Bus {i+1}\n")
        f.write("]);\n\n")

        f.write("% --- Travel Time (T) ---\n")
        f.write(f"T = array2d(1..{num_buses}, 1..{max_stops}, [\n")
        for i in range(num_buses):
            start = i * max_stops
            end = start + max_stops
            values = T[start:end]
            f.write("  " + ",".join(map(str, values)) + ("," if i < num_buses - 1 else "") + f"  % Bus {i+1}\n")
        f.write("]);\n\n")

        f.write("% --- Timetable (tau_bi) ---\n")
        f.write(f"tau_bi = array2d(1..{num_buses}, 1..{max_stops}, [\n")
        for i in range(num_buses):
            start = i * max_stops
            end = start + max_stops
            values = tau_bi[start:end]
            f.write("  " + ",".join(map(str, values)) + ("," if i < num_buses - 1 else "") + f"  % Bus {i+1}\n")
        f.write("]);\n")

    logger.info(f"✓ Created {output_file.name}")


def main():
    """Generate synthetic test cases."""
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "experiments" / "instances" / "battery-own"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("SYNTHETIC DATA GENERATION")
    logger.info("=" * 80)

    # Define test cases: (buses, stations, max_stops, filename)
    test_cases = [
        (3, 6, 5, "synthetic_3buses-6stations-5stops.dzn"),
        (5, 10, 8, "synthetic_5buses-10stations-8stops.dzn"),
        (8, 15, 10, "synthetic_8buses-15stations-10stops.dzn"),
        (10, 20, 12, "synthetic_10buses-20stations-12stops.dzn"),
    ]

    for num_buses, num_stations, max_stops, filename in test_cases:
        output_file = output_dir / filename
        generate_test_case(num_buses, num_stations, max_stops, output_file)

    logger.info("=" * 80)
    logger.info(f"✓ Generated {len(test_cases)} synthetic test cases")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
