#!/usr/bin/env python3
"""
Compare MiniZinc runner results against the Java reference matrix for cork-1-line.

Runs the floating CLP model on the Battery-Decided variants 20_0, 20_5, and
20_10 using the CPLEX backend and prints the selected station.
"""

from pathlib import Path
import sys
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.runner.core.executor import MiniZincExecutor
from core.runner.core.solvers import SolverType


EXPECTED = {
    "20_0": 19,
    "20_5": 19,
    "20_10": 19,
}


def selected_station(locations: list[int]) -> Optional[int]:
    if not locations:
        return None
    try:
        return locations.index(1)
    except ValueError:
        return None


def run_case(model_path: Path, instance_path: Path) -> dict:
    executor = MiniZincExecutor(str(model_path), timeout_seconds=None)
    success, result, elapsed = executor.execute(str(instance_path), SolverType.CPLEX)
    return {
        "success": success,
        "result": result,
        "elapsed": elapsed,
    }


def main() -> int:
    root = ROOT
    models = {
        "floating": root / "core" / "models" / "clp_model_float.mzn",
    }
    instances = {
        key: root / "experiments" / "instances" / "Battery-Decided" / f"cork-1-line_Battery-Decided{key}.dzn"
        for key in EXPECTED
    }

    exit_code = 0
    for precision_name, model_path in models.items():
        print(f"\n=== {precision_name.upper()} MODEL ===")
        for key, instance_path in instances.items():
            print(f"Running {key}: {instance_path.name}")
            if not model_path.exists():
                print(f"  missing model: {model_path}")
                exit_code = 1
                continue
            if not instance_path.exists():
                print(f"  missing instance: {instance_path}")
                exit_code = 1
                continue

            outcome = run_case(model_path, instance_path)
            result = outcome["result"] or {}
            locations = result.get("charging_locations", [])
            station = selected_station(locations)
            expected = EXPECTED[key]
            ok = station == expected and outcome["success"]
            print(f"  success: {outcome['success']}")
            print(f"  elapsed: {outcome['elapsed']:.3f}s" if outcome["elapsed"] is not None else "  elapsed: N/A")
            print(f"  selected_station: {station}")
            print(f"  expected_station: {expected}")
            print(f"  charging_locations: {locations}")
            print(f"  match: {'YES' if ok else 'NO'}")
            if not ok:
                exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())