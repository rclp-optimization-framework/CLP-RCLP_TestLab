"""
Data Loader Module

Loads instance data files (stations, distances, bus routes) from JITS2022 format.
Replicates the data reading logic from JITS2022 InstanceMTD.java.

Author: AVISPA Research Team
Date: April 2026
"""

import json
import logging
import csv
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and manage instance data from JITS2022 format files."""

    @staticmethod
    def load_stations(input_folder: Path) -> Tuple[Dict[int, str], int]:
        """
        Load station data from stations_input.csv.

        Replicates JITS2022 InstanceMTD.readStations() (lines 736-752).

        Args:
            input_folder: Path to input data folder

        Returns:
            (station_names: Dict[int, str], num_stations: int)
            Maps station ID to station name, and returns station count
        """
        station_names = {}
        stations_file = input_folder / "stations_input.csv"

        if not stations_file.exists():
            logger.warning(f"stations_input.csv not found in {input_folder}. Using default station mapping.")
            return station_names, 0

        try:
            with open(stations_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        station_id = int(row[1])
                        station_name = row[0]
                        station_names[station_id] = station_name

            logger.info(f"Loaded {len(station_names)} stations from {stations_file.name}")
            return station_names, len(station_names)

        except Exception as e:
            logger.error(f"Error loading stations from {stations_file}: {e}")
            return station_names, 0

    @staticmethod
    def load_distances(input_folder: Path, preserve_precision: bool = False) -> Tuple[Dict[Tuple[int, int], float], int]:
        """
        Load distance matrix from distances_input.csv.

        Replicates JITS2022 InstanceMTD.readDistances() (lines 754-776).

        CSV Format: from_id,to_id,distance (distance in kilometers)
        Returns: distances in meters (CSV km values multiplied by 1000)

        Args:
            input_folder: Path to input data folder

        Returns:
            (distances: Dict[(from, to), distance_in_meters], num_stations: int)
            Returns distance matrix as dictionary and station count
        """
        distances = {}
        distances_file = input_folder / "distances_input.csv"
        max_station_id = 0

        if not distances_file.exists():
            logger.warning(f"distances_input.csv not found in {input_folder}. Distances will need to be calculated.")
            return distances, 0

        try:
            with open(distances_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 3:
                        try:
                            from_id = int(row[0])
                            to_id = int(row[1])
                            if preserve_precision:
                                distance_value = Decimal(row[2].strip())
                            else:
                                distance_km = float(row[2])
                                distance_value = int(distance_km * 1000)  # Convert km to meters

                            # Store in both directions (symmetric)
                            distances[(from_id, to_id)] = distance_value
                            distances[(to_id, from_id)] = distance_value

                            max_station_id = max(max_station_id, from_id, to_id)
                        except ValueError as ve:
                            logger.warning(f"Skipping invalid distance row: {row}. Error: {ve}")

            num_stations = max_station_id + 1
            logger.info(f"Loaded {len(distances)} distance entries (covering {num_stations} stations) from {distances_file.name}")
            return distances, num_stations

        except Exception as e:
            logger.error(f"Error loading distances from {distances_file}: {e}")
            return distances, 0

    @staticmethod
    def load_bus_routes(input_folder: Path, model_speed: int, rest_time: int) -> Tuple[List[Dict], bool]:
        """
        Load bus routes from buses_input_{modelSpeed}_{restTime}.json.

        Replicates JITS2022 InstanceMTD.readBuses() (lines 778-909).

        Args:
            input_folder: Path to input data folder
            model_speed: Minimum model speed (km/h) - used in filename pattern
            rest_time: Rest time duration (min) - used in filename pattern

        Returns:
            (buses: List[Dict], file_found: bool)
            Each bus dict contains: station_ids, times, rest_flags
        """
        buses_filename = f"buses_input_{model_speed}_{rest_time}.json"
        buses_file = input_folder / buses_filename

        if not buses_file.exists():
            logger.error(f"{buses_filename} not found in {input_folder}")
            return [], False

        try:
            with open(buses_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            buses = []
            bus_id = 0

            # data is a list of line objects
            for line_obj in data:
                if 'buses' not in line_obj:
                    continue

                for bus_obj in line_obj['buses']:
                    if 'path' not in bus_obj or not bus_obj['path']:
                        logger.warning(f"Bus {bus_id} has empty path. Skipping.")
                        continue

                    path = bus_obj['path']
                    station_ids = []
                    times = []
                    rest_flags = []

                    for i, stop in enumerate(path):
                        station_id = stop.get('station_id')
                        time_str = stop.get('time', '00:00')
                        has_rest = stop.get('rest', False)

                        if station_id is not None:
                            station_ids.append(int(station_id))
                            times.append(time_str)
                            rest_flags.append(bool(has_rest))

                    if station_ids:
                        buses.append({
                            'bus_id': bus_id,
                            'station_ids': station_ids,
                            'times': times,
                            'rest_flags': rest_flags,
                        })
                        bus_id += 1

            logger.info(f"Loaded {len(buses)} buses from {buses_file.name}")
            return buses, True

        except Exception as e:
            logger.error(f"Error loading buses from {buses_file}: {e}")
            return [], False

    @staticmethod
    def parse_time_to_minutes(time_str: str) -> int:
        """
        Convert time string (HH:MM format) to minutes since 00:00.

        Replicates JITS2022 InstanceMTD time parsing.

        Args:
            time_str: Time in "HH:MM" format

        Returns:
            Minutes since midnight as integer
        """
        try:
            parts = time_str.split(':')
            if len(parts) >= 2:
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours * 60 + minutes
            return 0
        except (ValueError, IndexError):
            logger.warning(f"Could not parse time: {time_str}")
            return 0

    @staticmethod
    def kmh_to_m_per_sec(kmh: float) -> float:
        """
        Convert km/h to m/s.

        Replicates JITS2022 ToolsMTD.kmHourToMtSeconds().

        Args:
            kmh: Speed in kilometers per hour

        Returns:
            Speed in meters per second
        """
        return (kmh * 1000) / 3600

    @staticmethod
    def m_per_sec_to_seconds(distance_m: float, speed_m_per_sec: float) -> int:
        """
        Calculate travel time in seconds from distance (m) and speed (m/s).

        Args:
            distance_m: Distance in meters
            speed_m_per_sec: Speed in meters per second

        Returns:
            Travel time in seconds
        """
        if speed_m_per_sec <= 0:
            return 0
        return int(round(distance_m / speed_m_per_sec))

    @staticmethod
    def build_distance_matrix(distances_dict: Dict[Tuple[int, int], float],
                            station_count: int) -> List[List[int]]:
        """
        Build n×n distance matrix from dictionary.

        Args:
            distances_dict: Distance dict from load_distances()
            station_count: Number of stations

        Returns:
            n×n matrix where D[i][j] = distance in meters
        """
        D = [[0] * station_count for _ in range(station_count)]

        for (from_id, to_id), distance_m in distances_dict.items():
            if from_id < station_count and to_id < station_count:
                D[from_id][to_id] = int(distance_m)

        return D
