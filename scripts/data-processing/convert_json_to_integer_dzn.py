#!/usr/bin/env python3
"""
================================================================================
JSON to Integer DZN Converter for Electric Bus Charging Station Problem
================================================================================

This script converts bus schedule JSON files to MiniZinc DZN format with
INTEGER values Only, applying a consistent scaling factor (SCALE=10) throughout.

The conversion ensures compatibility with the CLP model which requires integer
arithmetic for the chuffed solver.

All floating-point values in the original JSON are multiplied by 10 and
rounded to the nearest integer to maintain precision while working with integers.

Author: EV-CLP Battery Project
Date: 2026-03-25
================================================================================
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import logging

# ============================================================================
# CONFIGURATION
# ============================================================================

# Scaling factor: all floating-point values are multiplied by this
SCALE = 10

# Model parameters (original values in comments)
CMAX_ORIGINAL = 100.0  # Maximum battery capacity (kWh)
CMIN_ORIGINAL = 20.0   # Minimum battery reserve (kWh)
ALPHA_ORIGINAL = 10.0  # Fast charging rate (kWh per minute)
MU_ORIGINAL = 5.0      # Maximum delay allowed (minutes)
SM_ORIGINAL = 1.0      # Safety margin between charging (minutes)
PSI_ORIGINAL = 1.0     # Minimum charging time (minutes)
BETA_ORIGINAL = 10.0   # Maximum charging time per stop (minutes)
M_ORIGINAL = 10000.0   # Big-M constant

# Scaled integer values
CMAX = int(CMAX_ORIGINAL * SCALE)
CMIN = int(CMIN_ORIGINAL * SCALE)
ALPHA = int(ALPHA_ORIGINAL * SCALE)
MU = int(MU_ORIGINAL * SCALE)
SM = int(SM_ORIGINAL * SCALE)
PSI = int(PSI_ORIGINAL * SCALE)
BETA = int(BETA_ORIGINAL * SCALE)
M = int(M_ORIGINAL * SCALE)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_time_to_minutes(time_str: str) -> float:
    """
    Convert time string (HH:MM format) to minutes since 00:00.

    Args:
        time_str: Time in "HH:MM" format

    Returns:
        Minutes since midnight as float
    """
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except Exception as e:
        logger.error(f"Error parsing time '{time_str}': {e}")
        return 0.0


def scale_to_integer(value: float) -> int:
    """
    Scale a floating-point value to integer by multiplying by SCALE.

    Args:
        value: Original floating-point value

    Returns:
        Scaled integer value (rounded to nearest int)
    """
    return round(value * SCALE)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate Euclidean distance between two GPS coordinates.
    This is a simplification; for real-world applications, use Haversine formula.

    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate

    Returns:
        Distance in arbitrary units
    """
    return ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5


# ============================================================================
# MAIN CONVERSION FUNCTIONS
# ============================================================================

def process_bus_line(line_data: Dict[str, Any]) -> Dict[str, List]:
    """
    Process a single bus line from JSON and extract all buses.

    Args:
        line_data: Dictionary containing line information

    Returns:
        Dictionary with processed bus data
    """
    buses = line_data.get('buses', [])
    processed_buses = []

    for bus_idx, bus in enumerate(buses):
        path = bus.get('path', [])

        if not path:
            logger.warning(f"Bus {bus_idx} has empty path. Skipping.")
            continue

        # Extract station IDs
        station_ids = [stop['station_id'] for stop in path]

        # Extract and convert times to minutes
        times = [parse_time_to_minutes(stop['time']) for stop in path]

        # Calculate time deltas (travel time between consecutive stops)
        time_deltas = [0.0]  # First stop has 0 travel time
        for i in range(1, len(times)):
            delta = times[i] - times[i-1]
            time_deltas.append(delta)

        # Calculate distances (energy consumption)
        # If GPS coordinates are available, use them; otherwise approximate
        distances = [0.0]  # First stop has 0 distance
        for i in range(1, len(path)):
            # Check if GPS data exists
            if 'lat' in path[i] and 'lon' in path[i] and 'lat' in path[i-1] and 'lon' in path[i-1]:
                dist = calculate_distance(
                    path[i-1]['lat'], path[i-1]['lon'],
                    path[i]['lat'], path[i]['lon']
                )
                # Scale distance to energy consumption (realistic estimation)
                # Typical: 100m → 0.5-1 kWh depending on bus type
                energy = (dist * 0.01) * 10  # 100m ≈ 0.1 kWh base
            else:
                # Approximate energy based on time
                # Realistic consumption: 1.5-2 kWh per minute for electric bus
                time_minutes = time_deltas[i]  # Already in minutes
                energy = time_minutes * 0.20  # ~0.2 kWh per minute (realistic for bus operation)

            distances.append(energy)

        processed_buses.append({
            'station_ids': station_ids,
            'times': times,
            'time_deltas': time_deltas,
            'energy_consumption': distances
        })

    return processed_buses


def convert_json_to_dzn(json_file: Path, output_file: Path, variant_name: str = ""):
    """
    Convert a JSON bus schedule file to integer DZN format.

    Args:
        json_file: Path to input JSON file
        output_file: Path to output DZN file
        variant_name: Name of the variant (e.g., "20_0")
    """
    logger.info(f"Converting {json_file.name} to integer DZN format...")

    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Process all lines and collect buses
        all_buses = []
        for line_data in data:
            buses = process_bus_line(line_data)
            all_buses.extend(buses)

        if not all_buses:
            logger.error(f"No buses found in {json_file.name}")
            return

        # Collect all unique stations
        all_stations = set()
        for bus in all_buses:
            all_stations.update(bus['station_ids'])

        # Create station mapping (1-indexed for MiniZinc compatibility)
        # Stations are enumerated starting from 1, not 0
        station_to_idx = {st: idx + 1 for idx, st in enumerate(sorted(all_stations))}

        # Determine dimensions
        num_buses = len(all_buses)
        num_stations = len(all_stations)
        max_stops = max(len(bus['station_ids']) for bus in all_buses)

        # Prepare arrays with padding
        st_bi = []
        D = []
        T = []
        tau_bi = []
        num_stops = []

        for bus in all_buses:
            num_stops.append(len(bus['station_ids']))

            # Map stations to indices and pad
            stations = [station_to_idx[st] for st in bus['station_ids']]
            stations += [stations[-1]] * (max_stops - len(stations))  # Pad with last station
            st_bi.extend(stations)

            # Scale and pad energy consumption (D) - CONVERTED TO INTEGERS
            energy = [scale_to_integer(e) for e in bus['energy_consumption']]
            energy += [0] * (max_stops - len(energy))  # Pad with zeros
            D.extend(energy)

            # Scale and pad travel times (T) - CONVERTED TO INTEGERS
            times = [scale_to_integer(t) for t in bus['time_deltas']]
            times += [0] * (max_stops - len(times))  # Pad with zeros
            T.extend(times)

            # Scale and pad schedule times (tau_bi) - CONVERTED TO INTEGERS
            schedule = [scale_to_integer(t) for t in bus['times']]
            schedule += [scale_to_integer(bus['times'][-1])] * (max_stops - len(schedule))  # Pad with last time
            tau_bi.extend(schedule)

        # Generate DZN file with comprehensive comments
        base_name = json_file.stem.replace('buses_input', '')
        base_name = base_name.strip('_') if base_name else 'default'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("% " + "=" * 76 + "\n")
            f.write(f"% CLP Test Case: {base_name} (variant: {variant_name})\n")
            f.write("% " + "=" * 76 + "\n")
            f.write("% Source: JITS2022 Test Battery\n")
            f.write(f"% Original file: {json_file.name}\n")
            f.write("% Converted to INTEGER CLP format with SCALE=10\n")
            f.write("%\n")
            f.write("% CONVERSION DETAILS:\n")
            f.write("% - All floating-point values multiplied by 10 and rounded to integers\n")
            f.write("% - Example: 42.5 minutes → 425 (integer)\n")
            f.write("%           1.3 kWh → 13 (integer)\n")
            f.write("%\n")
            f.write("% IMPORTANT: To interpret results, divide integer values by 10:\n")
            f.write("%   - Time: integer_value / 10 = minutes\n")
            f.write("%   - Energy: integer_value / 10 = kWh\n")
            f.write("% " + "=" * 76 + "\n\n")

            # Problem dimensions
            f.write("% --- Problem Dimensions ---\n")
            f.write(f"num_buses = {num_buses};\n")
            f.write(f"num_stations = {num_stations};\n\n")

            # Energy parameters (all values scaled and commented)
            f.write("% --- Energy Parameters (CLP Model) ---\n")
            f.write("% All values are INTEGERS scaled by ×10 from original floating-point values\n")
            f.write(f"Cmax = {CMAX};  % Maximum battery capacity (original: {CMAX_ORIGINAL} kWh)\n")
            f.write(f"Cmin = {CMIN};   % Minimum reserve (original: {CMIN_ORIGINAL} kWh)\n")
            f.write(f"alpha = {ALPHA};  % Fast charging rate (original: {ALPHA_ORIGINAL} kWh per minute)\n\n")

            # Time and schedule parameters
            f.write("% --- Time and Schedule Parameters ---\n")
            f.write("% All values are INTEGERS scaled by ×10 from original floating-point values\n")
            f.write(f"mu = {MU};      % Maximum delay allowed (original: {MU_ORIGINAL} minutes)\n")
            f.write(f"SM = {SM};      % Safety margin (original: {SM_ORIGINAL} minutes)\n")
            f.write(f"psi = {PSI};     % Minimum charging time (original: {PSI_ORIGINAL} minutes)\n")
            f.write(f"beta = {BETA};   % Maximum charging time per stop (original: {BETA_ORIGINAL} minutes)\n")
            f.write(f"M = {M};   % Big-M constant (original: {M_ORIGINAL})\n\n")

            # Route structure
            f.write("% --- Route Structure ---\n")
            f.write(f"max_stops = {max_stops};\n")
            f.write(f"num_stops = {num_stops};\n\n")

            # Station sequence (st_bi)
            f.write("% --- Station Sequence (st_bi) ---\n")
            f.write("% Maps each bus stop to a physical station ID (1-indexed)\n")
            f.write(f"st_bi = array2d(1..{num_buses}, 1..{max_stops}, [\n")
            for i in range(num_buses):
                start_idx = i * max_stops
                end_idx = start_idx + max_stops
                bus_stations = st_bi[start_idx:end_idx]
                line = "  " + ",".join(map(str, bus_stations))
                f.write(line + ("," if i < num_buses - 1 else "") + f"  % Bus {i+1}\n")
            f.write("]);\n\n")

            # Energy consumption (D) - NOW INTEGERS
            f.write("% --- Energy Consumption (D) ---\n")
            f.write("% Energy consumed between stops (INTEGER values, divide by 10 for kWh)\n")
            f.write("% Original floating-point values have been scaled by ×10\n")
            f.write(f"D = array2d(1..{num_buses}, 1..{max_stops}, [\n")
            for i in range(num_buses):
                start_idx = i * max_stops
                end_idx = start_idx + max_stops
                bus_energy = D[start_idx:end_idx]
                line = "  " + ",".join(map(str, bus_energy))
                f.write(line + ("," if i < num_buses - 1 else "") + f"  % Bus {i+1}\n")
            f.write("]);\n\n")

            # Travel time (T) - NOW INTEGERS
            f.write("% --- Travel Time (T) ---\n")
            f.write("% Time between stops (INTEGER values, divide by 10 for minutes)\n")
            f.write("% Original floating-point values have been scaled by ×10\n")
            f.write(f"T = array2d(1..{num_buses}, 1..{max_stops}, [\n")
            for i in range(num_buses):
                start_idx = i * max_stops
                end_idx = start_idx + max_stops
                bus_times = T[start_idx:end_idx]
                line = "  " + ",".join(map(str, bus_times))
                f.write(line + ("," if i < num_buses - 1 else "") + f"  % Bus {i+1}\n")
            f.write("]);\n\n")

            # Schedule (tau_bi) - NOW INTEGERS
            f.write("% --- Original Timetable (tau_bi) ---\n")
            f.write("% Scheduled arrival times (INTEGER values, divide by 10 for minutes since 00:00)\n")
            f.write("% Original floating-point values have been scaled by ×10\n")
            f.write(f"tau_bi = array2d(1..{num_buses}, 1..{max_stops}, [\n")
            for i in range(num_buses):
                start_idx = i * max_stops
                end_idx = start_idx + max_stops
                bus_schedule = tau_bi[start_idx:end_idx]
                line = "  " + ",".join(map(str, bus_schedule))
                f.write(line + ("," if i < num_buses - 1 else "") + f"  % Bus {i+1}\n")
            f.write("]);\n")

        logger.info(f"✓ Successfully created {output_file.name}")
        logger.info(f"  - Buses: {num_buses}, Stations: {num_stations}, Max stops: {max_stops}")

    except Exception as e:
        logger.error(f"Error converting {json_file.name}: {e}", exc_info=True)


def batch_convert_directory(input_dir: Path, output_dir: Path):
    """
    Convert all JSON files in a directory to integer DZN format.

    Args:
        input_dir: Directory containing JSON files
        output_dir: Directory for output DZN files
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all JSON files
    json_files = sorted(input_dir.glob("*.json"))

    if not json_files:
        logger.warning(f"No JSON files found in {input_dir}")
        return

    logger.info(f"Found {len(json_files)} JSON files to convert")
    logger.info("=" * 80)

    success_count = 0
    for json_file in json_files:
        # Generate output filename
        base_name = json_file.stem.replace('buses_input', '')
        base_name = base_name.strip('_') if base_name else 'default'

        # Extract variant name (e.g., "20_0" from "buses_input_20_0.json")
        parts = json_file.stem.split('_')
        variant = '_'.join(parts[2:]) if len(parts) > 2 else ""

        output_file = output_dir / f"{input_dir.name}{base_name}.dzn"

        try:
            convert_json_to_dzn(json_file, output_file, variant)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to convert {json_file.name}: {e}")

    logger.info("=" * 80)
    logger.info(f"Conversion complete: {success_count}/{len(json_files)} files successful")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to run the converter."""
    if len(sys.argv) > 1:
        # Single file mode
        input_file = Path(sys.argv[1])
        output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(input_file.stem + "_int.dzn")

        if input_file.exists():
            convert_json_to_dzn(input_file, output_file)
        else:
            logger.error(f"File not found: {input_file}")
            sys.exit(1)
    else:
        # Batch mode - convert all directories
        project_root = Path(__file__).resolve().parents[2]
        jits_data_dir = project_root / "external" / "jits2022" / "Code" / "data"
        output_base = project_root / "experiments" / "instances" / "battery-own"

        if not jits_data_dir.exists():
            logger.error(f"JITS data directory not found: {jits_data_dir}")
            sys.exit(1)

        logger.info("=" * 80)
        logger.info("BATCH CONVERSION MODE: Processing all JITS2022 test cases")
        logger.info(f"Source: {jits_data_dir}")
        logger.info(f"Target: {output_base}")
        logger.info("=" * 80)

        # Find all subdirectories containing JSON files
        subdirs = [d for d in jits_data_dir.iterdir() if d.is_dir()]

        for subdir in sorted(subdirs):
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing directory: {subdir.name}")
            logger.info(f"{'='*80}")
            batch_convert_directory(subdir, output_base)

        logger.info("\n" + "=" * 80)
        logger.info("ALL CONVERSIONS COMPLETE")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()
