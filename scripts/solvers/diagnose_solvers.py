#!/usr/bin/env python3
"""
Comprehensive Solver Diagnostics Script

Detailed diagnosis of solver functionality and performance issues.
Tests each solver with actual model execution and provides detailed error reports.

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
Usage: python scripts/solvers/diagnose_solvers.py [instance_path] [model]
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import io
import os

# Configure output encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class SolverDiagnostics:
    """Comprehensive solver diagnostics and testing."""

    SOLVERS = ["chuffed", "gecode", "coin-bc", "cp-sat", "cplex", "gurobi"]

    def __init__(self, instance_path: str, model: str = "CLP"):
        """Initialize diagnostics."""
        self.instance_path = Path(instance_path)
        self.model = model
        self.project_root = self._find_project_root()
        self.model_file = self._get_model_file()
        self.results = {}

    def _find_project_root(self) -> Path:
        """Find project root."""
        current = Path(__file__).parent
        while current.name != "CLP-RCLP Minizinc" and current.parent != current:
            current = current.parent
        return current if current.name == "CLP-RCLP Minizinc" else Path(__file__).parent.parent.parent

    def _get_model_file(self) -> Path:
        """Get model file path."""
        model_name = "clp_model.mzn" if self.model == "CLP" else "rclp_model.mzn"
        return self.project_root / "core" / "models" / model_name

    def diagnose_solver(self, solver: str, timeout: int = 10) -> Dict:
        """Comprehensive diagnosis of a single solver."""
        print(f"\n[Diagnosing {solver}]", flush=True)

        diagnosis = {
            "solver": solver,
            "version_check": self._check_version(solver),
            "execution_test": self._test_execution(solver, timeout),
            "status": "unknown"
        }

        # Determine overall status
        if not diagnosis["version_check"]["available"]:
            diagnosis["status"] = "not_installed"
        elif diagnosis["execution_test"]["success"]:
            diagnosis["status"] = "working"
        else:
            diagnosis["status"] = "installed_but_failing"

        return diagnosis

    def _check_version(self, solver: str) -> Dict:
        """Check solver version."""
        try:
            result = subprocess.run(
                ["minizinc", "--solver", solver, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return {
                    "available": True,
                    "version": result.stdout.strip()[:100]
                }
            else:
                return {
                    "available": False,
                    "error": result.stderr.strip()[:200]
                }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)[:200]
            }

    def _test_execution(self, solver: str, timeout: int) -> Dict:
        """Test solver with actual model execution."""
        try:
            if not self.instance_path.exists():
                return {
                    "success": False,
                    "error": "Instance file not found",
                    "time": 0
                }

            cmd = [
                "minizinc",
                "--solver", solver,
                "--time-limit", str(timeout * 1000),
                str(self.model_file),
                str(self.instance_path)
            ]

            start_time = time.time()

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )

            exec_time = time.time() - start_time

            if result.returncode == 0:
                # Check for actual solution
                if "Estaciones instaladas" in result.stdout or "Solução" in result.stdout:
                    return {
                        "success": True,
                        "time": exec_time,
                        "output": result.stdout[:200]
                    }
                else:
                    return {
                        "success": False,
                        "error": "No solution in output",
                        "time": exec_time,
                        "output": result.stdout[:200]
                    }
            else:
                return {
                    "success": False,
                    "error": result.stderr[:300],
                    "time": exec_time
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timeout",
                "time": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)[:300],
                "time": 0
            }

    def run_all_diagnostics(self) -> Dict:
        """Run diagnostics on all solvers."""
        print("\n" + "=" * 70)
        print("SOLVER DIAGNOSTICS")
        print("=" * 70)
        print(f"Instance: {self.instance_path.name}")
        print(f"Model: {self.model}")
        print(f"Testing started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        results = {}
        for solver in self.SOLVERS:
            results[solver] = self.diagnose_solver(solver)

        self.results = results
        return results

    def print_summary(self) -> None:
        """Print formatted summary."""
        if not self.results:
            return

        print("\n" + "=" * 70)
        print("DIAGNOSTICS SUMMARY")
        print("=" * 70 + "\n")

        working = [s for s, r in self.results.items() if r["status"] == "working"]
        failing = [s for s, r in self.results.items() if r["status"] == "installed_but_failing"]
        missing = [s for s, r in self.results.items() if r["status"] == "not_installed"]

        print(f"Working: {len(working)}/{len(self.SOLVERS)}")
        print(f"Installed but Failing: {len(failing)}")
        print(f"Not Installed: {len(missing)}\n")

        # Working solvers
        if working:
            print("[WORKING SOLVERS]")
            for solver in working:
                result = self.results[solver]
                exec_time = result["execution_test"]["time"]
                print(f"  {solver:15} - {exec_time:.3f}s")

        # Failing solvers
        if failing:
            print("\n[INSTALLED BUT FAILING]")
            for solver in failing:
                result = self.results[solver]
                error = result["execution_test"]["error"][:60]
                print(f"  {solver:15} - {error}")

        # Missing solvers
        if missing:
            print("\n[NOT INSTALLED]")
            for solver in missing:
                result = self.results[solver]
                version_error = result["version_check"].get("error", "Unknown")[:60]
                print(f"  {solver:15} - {version_error}")

        print("\n" + "=" * 70 + "\n")

    def print_detailed_report(self) -> None:
        """Print detailed report for each solver."""
        if not self.results:
            return

        print("\n" + "=" * 70)
        print("DETAILED SOLVER REPORT")
        print("=" * 70 + "\n")

        for solver, result in self.results.items():
            print(f"[{solver.upper()}]")
            print(f"  Status: {result['status'].upper()}")

            # Version info
            version = result["version_check"]
            if version["available"]:
                print(f"  Version: {version['version']}")
            else:
                print(f"  Version Error: {version.get('error', 'Unknown')}")

            # Execution test
            exec_test = result["execution_test"]
            print(f"  Execution: {'SUCCESS' if exec_test['success'] else 'FAILED'}")
            print(f"  Time: {exec_test['time']:.3f}s")

            if not exec_test["success"]:
                print(f"  Error: {exec_test.get('error', 'Unknown')}")

            print()

    def save_json_report(self, output_path: Optional[str] = None) -> str:
        """Save detailed report as JSON."""
        if not output_path:
            output_dir = self.project_root / "experiments" / "results" / "diagnostics"
        else:
            output_dir = Path(output_path)

        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"solver_diagnostics_{timestamp}.json"

        report = {
            "instance": str(self.instance_path),
            "model": self.model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.results
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        return str(output_file)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/solvers/diagnose_solvers.py <instance_path> [model]")
        print("Example: python scripts/solvers/diagnose_solvers.py experiments/instances/battery-own/noncity_5buses-8stations.dzn CLP")
        sys.exit(1)

    instance_path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "CLP"

    try:
        diag = SolverDiagnostics(instance_path, model)
        diag.run_all_diagnostics()
        diag.print_summary()
        diag.print_detailed_report()

        json_report = diag.save_json_report()
        print(f"Detailed report saved: {json_report}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
