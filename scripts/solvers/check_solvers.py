#!/usr/bin/env python3
"""
Solver Availability Checker

Verify which solvers are available in the system and provide installation guidance.
Useful for diagnosing solver configuration issues.

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
Usage: python scripts/solvers/check_solvers.py
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Tuple
import io
import os

# Configure output encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class SolverChecker:
    """Check solver availability and version information."""

    # Solvers to check and their version commands
    SOLVERS = {
        "chuffed": ["minizinc", "--solver", "chuffed", "--version"],
        "gecode": ["minizinc", "--solver", "gecode", "--version"],
        "coin-bc": ["minizinc", "--solver", "coin-bc", "--version"],
        "cp-sat": ["minizinc", "--solver", "cp-sat", "--version"],
        "cplex": ["minizinc", "--solver", "cplex", "--version"],
        "gurobi": ["minizinc", "--solver", "gurobi", "--version"],
    }

    @staticmethod
    def check_solver(solver_name: str) -> Tuple[bool, str]:
        """
        Check if a solver is available.

        Returns:
            (available: bool, version_info: str)
        """
        try:
            cmd = SolverChecker.SOLVERS.get(solver_name, [])
            if not cmd:
                return False, "Unknown solver"

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                version_info = result.stdout.strip() or result.stderr.strip()
                return True, version_info
            else:
                return False, result.stderr.strip() or "Solver not available"

        except subprocess.TimeoutExpired:
            return False, "Timeout checking solver"
        except FileNotFoundError:
            return False, "MiniZinc not found in PATH"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def check_all_solvers() -> Dict[str, Dict]:
        """Check all available solvers and return status."""
        results = {}

        for solver_name in SolverChecker.SOLVERS.keys():
            available, info = SolverChecker.check_solver(solver_name)
            results[solver_name] = {
                "available": available,
                "info": info
            }

        return results

    @staticmethod
    def print_report(results: Dict[str, Dict]) -> None:
        """Print formatted solver availability report."""
        print("\n" + "=" * 70)
        print("SOLVER AVAILABILITY REPORT")
        print("=" * 70 + "\n")

        available_count = sum(1 for r in results.values() if r["available"])
        total_count = len(results)

        print(f"Summary: {available_count}/{total_count} solvers available\n")

        # Print available solvers
        print("-" * 70)
        print("[OK] AVAILABLE SOLVERS")
        print("-" * 70)
        for solver, info in results.items():
            if info["available"]:
                print(f"\n  {solver.upper()}")
                print(f"    Status: Ready")
                print(f"    Info: {info['info'][:60]}")

        # Print unavailable solvers
        print("\n" + "-" * 70)
        print("[NOT FOUND] UNAVAILABLE SOLVERS")
        print("-" * 70)
        for solver, info in results.items():
            if not info["available"]:
                print(f"\n  {solver.upper()}")
                print(f"    Status: Not found")
                print(f"    Details: {info['info']}")

        print("\n" + "=" * 70 + "\n")

    @staticmethod
    def save_json_report(results: Dict[str, Dict], output_path: str) -> None:
        """Save report as JSON."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Report saved: {output_path}")


if __name__ == "__main__":
    checker = SolverChecker()
    results = checker.check_all_solvers()

    # Print report
    checker.print_report(results)

    # Save JSON report
    report_path = Path(__file__).resolve().parents[2] / "experiments" / "results" / "solver_check_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    checker.save_json_report(results, str(report_path))
