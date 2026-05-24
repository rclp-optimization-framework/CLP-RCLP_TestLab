"""
Result Handler - Save test results in JSON and TXT formats

Manages output file generation and formatting for successful and failed executions.
Organizes results by solver and stores diagnostics for failed runs.

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ResultHandler:
    """Handle result file generation and storage with test-name and solver organization."""

    def __init__(self, output_dir: str, test_name: str = ""):
        """
        Initialize result handler.

        Args:
            output_dir: Base directory to save results
            test_name: Name of the test instance (optional, for organizing by test)
        """
        self.output_dir = Path(output_dir)
        self.test_name = test_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_results(self, filename: str, result: Dict, solver: str) -> Tuple[bool, str, str]:
        """
        Save successful results in JSON and TXT formats, organized by test name and solver.

        Args:
            filename: Base filename (without extension)
            result: Result dictionary (from executor)
            solver: Solver name used for execution

        Returns:
            (success: bool, json_path: str, txt_path: str)
        """
        try:
            # Build directory path: output_dir/test_name/solver (if test_name provided)
            if self.test_name:
                result_dir = self.output_dir / self.test_name / solver
            else:
                result_dir = self.output_dir / solver

            result_dir.mkdir(parents=True, exist_ok=True)

            # Save JSON
            json_path = result_dir / f"{filename}_result.json"
            self._save_json(json_path, result, solver)

            # Save TXT
            txt_path = result_dir / f"{filename}_result.txt"
            self._save_txt(txt_path, result, solver)

            logger.info(f"Results saved: {json_path}, {txt_path}")
            return True, str(json_path), str(txt_path)

        except Exception as e:
            logger.error(f"Save error: {str(e)}")
            return False, "", ""

    def save_diagnostic(self, filename: str, result: Dict, solver: str,
                       status: str = "error") -> Tuple[bool, str, str]:
        """
        Save diagnostic information for failed or unsatisfiable runs.

        Args:
            filename: Base filename (without extension)
            result: Result dictionary with error information
            solver: Solver name used for execution
            status: 'error', 'unsatisfiable', or 'timeout'

        Returns:
            (success: bool, json_path: str, txt_path: str)
        """
        try:
            # Create diagnostics directory structure: Tests/Diagnostics/{solver}/
            diag_dir = Path("Tests/Diagnostics") / solver
            diag_dir.mkdir(parents=True, exist_ok=True)

            # Save JSON diagnostic
            json_path = diag_dir / f"{filename}_diagnostic.json"
            self._save_diagnostic_json(json_path, result, solver, status)

            # Save TXT diagnostic
            txt_path = diag_dir / f"{filename}_diagnostic.txt"
            self._save_diagnostic_txt(txt_path, result, solver, status)

            logger.info(f"Diagnostics saved: {json_path}, {txt_path}")
            return True, str(json_path), str(txt_path)

        except Exception as e:
            logger.error(f"Diagnostic save error: {str(e)}")
            return False, "", ""

    def _save_json(self, path: Path, result: Dict, solver: str) -> None:
        """Save result as JSON with solver and execution time."""
        deviation_minutes = self._time_deviation_minutes(result)
        json_data = {
            "solver": solver,
            "execution_time_seconds": round(result.get('execution_time', 0), 3),
            "num_buses": result.get('num_buses', 0),
            "num_stations": result.get('num_stations', 0),
            "charged_stations": result.get('charged_stations', 0),
            "charging_locations": result.get('charging_locations', []),
            "time_deviation_minutes": deviation_minutes,
            "timestamp": datetime.now().isoformat()
        }

        with open(path, 'w') as f:
            json.dump(json_data, f, indent=2)

    def _save_txt(self, path: Path, result: Dict, solver: str) -> None:
        """Save result as human-readable TXT format with solver and time info."""
        num_buses = result.get('num_buses', 0)
        num_stations = result.get('num_stations', 0)
        charged = result.get('charged_stations', 0)
        locations = result.get('charging_locations', [])
        deviation = self._time_deviation_minutes(result)
        exec_time = result.get('execution_time', 0)

        # Format charging locations as binary array
        locations_str = "[" + ",".join(str(x) for x in locations) + "]"

        lines = [
            "=" * 70,
            "CLP-RCLP Test Execution Result",
            "=" * 70,
            "",
            f"Solver:                 {solver}",
            f"Execution Time:         {exec_time:.3f} seconds",
            f"Timestamp:              {datetime.now().isoformat()}",
            "",
            f"Number of Buses:        {num_buses}",
            f"Number of Stations:     {num_stations}",
            f"Charged Stations:       {charged}",
            f"Charging Locations:     {locations_str}",
            f"Time Deviation:         {deviation} minutes",
            "",
            "=" * 70
        ]

        with open(path, 'w') as f:
            f.write("\n".join(lines))

    @staticmethod
    def _time_deviation_minutes(result: Dict) -> float:
        """Normalize time deviation to minutes based on the model precision."""
        deviation = float(result.get('time_deviation', 0) or 0)
        precision = str(result.get('model_precision', '')).lower()

        if precision == 'integer':
            return deviation / 10

        return deviation

    def _save_diagnostic_json(self, path: Path, result: Dict, solver: str, status: str) -> None:
        """Save diagnostic information as JSON."""
        diag_data = {
            "solver": solver,
            "status": status,  # 'error', 'unsatisfiable', 'timeout'
            "execution_time_seconds": result.get('execution_time', None),
            "error_message": result.get('error_message', ''),
            "minizinc_stderr": result.get('minizinc_stderr', ''),
            "test_instance": result.get('test_instance', ''),
            "model": result.get('model', ''),
            "timestamp": datetime.now().isoformat()
        }

        with open(path, 'w') as f:
            json.dump(diag_data, f, indent=2)

    def _save_diagnostic_txt(self, path: Path, result: Dict, solver: str, status: str) -> None:
        """Save diagnostic information in human-readable format."""
        exec_time = result.get('execution_time', None)
        exec_time_str = f"{exec_time:.3f} seconds" if exec_time else "N/A"

        lines = [
            "=" * 70,
            "CLP-RCLP Test Execution Diagnostic Report",
            "=" * 70,
            "",
            f"Status:                 {status.upper()}",
            f"Solver:                 {solver}",
            f"Execution Time:         {exec_time_str}",
            f"Timestamp:              {datetime.now().isoformat()}",
            "",
            f"Test Instance:          {result.get('test_instance', 'N/A')}",
            f"Model:                  {result.get('model', 'N/A')}",
            "",
            "-" * 70,
            "Error Information:",
            "-" * 70,
            "",
            result.get('error_message', 'No error message available'),
            "",
            "-" * 70,
            "MiniZinc Output:",
            "-" * 70,
            "",
            result.get('minizinc_stderr', 'No stderr available'),
            "",
            "=" * 70
        ]

        with open(path, 'w') as f:
            f.write("\n".join(lines))
