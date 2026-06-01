"""
MiniZinc Executor - Run CLP/RCLP tests with multiple solvers

Handles MiniZinc execution with proper timeout management, output parsing,
and support for multiple solvers (chuffed, gecode, coin-bc, cp-sat, cplex, gurobi).

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging
import time
import signal
import threading

from core.shared.project_paths import ProjectPaths
from .solvers import SolverType, SolverManager

logger = logging.getLogger(__name__)

DEFAULT_CPLEX_OPTIONS = {}


class MiniZincExecutor:
    """Execute MiniZinc models with multiple solver support."""

    def __init__(self, model_path: str, timeout_seconds: Optional[int] = 300, stop_event: Optional[threading.Event] = None):
        """
        Initialize executor.

        Args:
            model_path: Path to .mzn model file
            timeout_seconds: Execution timeout in seconds, or None/<=0 for no timeout
            stop_event: Threading event to signal stop request from UI
        """
        self.model_path = Path(model_path)
        self.timeout_seconds = timeout_seconds
        self.process: Optional[subprocess.Popen] = None
        self.stop_event = stop_event

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

    def execute(self, dzn_file, solver: SolverType = SolverType.CHUFFED, solver_options: Optional[Dict] = None) -> Tuple[bool, Optional[Dict], Optional[float]]:
        """
        Execute MiniZinc with given instance and solver using Popen for process control.

        Args:
            dzn_file: Path to .dzn instance file
            solver: Solver to use (default: chuffed)
            solver_options: Optional solver-specific configuration

        Returns:
            (success: bool, result: dict or None, execution_time: float or None)
            Result contains: num_buses, num_stations, charged_stations,
                           charging_locations, time_deviation, solver, execution_time
        """
        if isinstance(dzn_file, (list, tuple)):
            dzn_paths = [Path(p) for p in dzn_file]
        else:
            dzn_paths = [Path(dzn_file)]

        for p in dzn_paths:
            if not p.exists():
                logger.error(f"Instance file not found: {p}")
                return False, None, None

        try:
            solver_name = SolverManager.get_minizinc_solver_name(solver)
            cmd = ["minizinc", "--solver", solver_name]

            if self.timeout_seconds and self.timeout_seconds > 0:
                cmd += ["--time-limit", str(self.timeout_seconds * 1000)]

            if solver == SolverType.CPLEX:
                effective_options = dict(solver_options or {})
                if 'solver_time_limit' in effective_options and effective_options['solver_time_limit'] is not None:
                    cmd += ["--solver-time-limit", str(int(effective_options['solver_time_limit']))]

            cmd += [str(self.model_path)] + [str(p) for p in dzn_paths]
            logger.debug(f"Running: {' '.join(cmd)}")

            start_time = time.time()
            timeout_sec = self.timeout_seconds + 10 if self.timeout_seconds and self.timeout_seconds > 0 else None

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Poll with stop_event checking instead of blocking communicate()
            stdout_lines = []
            stderr_lines = []
            deadline = time.time() + timeout_sec if timeout_sec else None
            poll_interval = 0.1  # Check stop_event every 100ms

            while True:
                # Check for stop request
                if self.stop_event and self.stop_event.is_set():
                    logger.info("Stop event detected, terminating process")
                    self.terminate()
                    return False, None, None

                # Check if process finished
                returncode = self.process.poll()
                if returncode is not None:
                    break

                # Check timeout
                if deadline and time.time() > deadline:
                    self.process.kill()
                    logger.warning(f"MiniZinc execution timed out with {solver_name}")
                    return False, None, self.timeout_seconds

                time.sleep(poll_interval)

            # Process finished, read remaining output
            execution_time = time.time() - start_time
            stdout, stderr = self.process.communicate()  # Non-blocking at this point

            if returncode == 0:
                success, parsed_result = self._parse_solution(stdout, dzn_paths[0], solver)
                if success and parsed_result:
                    parsed_result['execution_time'] = execution_time
                    parsed_result['solver'] = SolverManager.get_display_name(solver)
                return success, parsed_result, execution_time
            else:
                logger.warning(f"MiniZinc failed with {solver_name}: {stderr[:200] if stderr else 'Unknown error'}")
                return False, None, execution_time

        except Exception as e:
            logger.error(f"Execution error: {str(e)}")
            if self.process and self.process.poll() is None:
                self.process.kill()
            return False, None, None

    def terminate(self) -> None:
        """
        Terminate the currently running MiniZinc process gracefully.

        First attempts SIGTERM, then SIGKILL after 2 seconds if needed.
        """
        if self.process is None or self.process.poll() is not None:
            return

        try:
            logger.info("Terminating MiniZinc process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
                logger.info("Process terminated gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("Process did not respond to SIGTERM, killing forcefully...")
                self.process.kill()
                self.process.wait()
                logger.info("Process killed")
        except Exception as e:
            logger.error(f"Error terminating process: {str(e)}")

    def _parse_solution(self, output: str, dzn_path: Path, solver: SolverType) -> Tuple[bool, Optional[Dict]]:
        """
        Parse MiniZinc output to extract solution.

        Args:
            output: MiniZinc stdout
            dzn_path: Path to instance file (for metadata extraction)
            solver: Solver used for this execution

        Returns:
            (success: bool, result: dict or None)
        """
        try:
            # Check if satisfiable - look for common "UNSAT"/"UNSATISFIABLE" markers
            # MiniZinc/solvers may print variants such as "=====UNSATISFIABLE=====",
            # "% UNSATISFIABLE", or plain "UNSATISFIABLE". Match common patterns.
            if re.search(r"UNSATISFIABLE", output, re.IGNORECASE) or re.search(r"={2,}\s*UNSAT", output, re.IGNORECASE) or "% UNSATISFIABLE" in output:
                logger.info(f"Instance is UNSATISFIABLE with {SolverManager.get_display_name(solver)}")
                return False, {
                    "status": "unsatisfiable",
                    "model_path": str(self.model_path),
                    "model_precision": "floating" if "float" in self.model_path.stem.lower() else "integer",
                }

            # Extract key values from solution
            lines = output.strip().split("\n")
            result = self._extract_values(lines, dzn_path)

            if result is None:
                logger.warning(f"Could not parse solution values for {SolverManager.get_display_name(solver)}")
                return False, None

            result["model_path"] = str(self.model_path)
            result["model_precision"] = "floating" if "float" in self.model_path.stem.lower() else "integer"

            logger.info(f"Solution found with {SolverManager.get_display_name(solver)}: {result.get('charged_stations', 0)} stations charged")
            return True, result

        except Exception as e:
            logger.error(f"Parse error: {str(e)}")
            return False, None

    def _extract_values(self, lines: list, dzn_path: Path) -> Optional[Dict]:
        """
        Extract solution values from MiniZinc output.

        Returns extracted values or None if parse fails.
        """
        result = {}

        try:
            with open(dzn_path, 'r', encoding='utf-8') as f:
                content = f.read()
                buses_match = re.search(r'num_buses\s*=\s*(\d+)', content)
                stations_match = re.search(r'num_stations\s*=\s*(\d+)', content)

                if buses_match and stations_match:
                    result['num_buses'] = int(buses_match.group(1))
                    result['num_stations'] = int(stations_match.group(1))
                else:
                    return None
        except Exception:
            return None

        solution_text = "\n".join(lines)

        estaciones_match = re.search(r'Estaciones instaladas:\s*\[(.*?)\]', solution_text, re.DOTALL)
        if estaciones_match:
            locations_str = estaciones_match.group(1)
            try:
                charging_locs = [int(x.strip()) for x in locations_str.split(',') if x.strip()]
                result['charging_locations'] = charging_locs
                result['charged_stations'] = sum(charging_locs)
                result['charged_index'] = [i for i, val in enumerate(charging_locs) if val == 1]
            except ValueError:
                logger.warning(f"Failed to parse charging locations: {locations_str}")
                return None
        else:
            logger.warning("Could not find 'Estaciones instaladas' in output")
            return None

        desviacion_match = re.search(r'Desviacion total:\s*(-?\d+(?:\.\d+)?)', solution_text)
        if desviacion_match:
            result['time_deviation'] = float(desviacion_match.group(1))
        else:
            logger.warning("Could not find 'Desviacion total' in output")
            result['time_deviation'] = 0

        return result
