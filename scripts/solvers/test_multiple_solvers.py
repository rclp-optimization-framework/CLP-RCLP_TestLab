#!/usr/bin/env python3
"""
Batch Solver Testing Script

Execute a test instance with multiple solvers and compare results.
Useful for performance benchmarking and solver validation.

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
Usage: python scripts/solvers/test_multiple_solvers.py <instance_path> [model] [solvers...]
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional


class MultipleSolverTester:
    """Execute tests across multiple solvers."""

    SOLVERS = ["chuffed", "gecode", "coin-bc", "cp-sat", "cplex", "gurobi"]
    MODELS = ["CLP", "RCLP"]

    def __init__(self, instance_path: str, model: str = "CLP", solvers: Optional[List[str]] = None):
        """
        Initialize tester.

        Args:
            instance_path: Path to .dzn instance file
            model: Model to use (CLP or RCLP)
            solvers: List of solvers to test (default: all available)
        """
        self.instance_path = Path(instance_path)
        self.model = model
        self.solvers = solvers or self.SOLVERS

        if not self.instance_path.exists():
            raise FileNotFoundError(f"Instance not found: {instance_path}")

        # Find project root and models
        self.project_root = self._find_project_root()
        self.model_file = self._get_model_file()

        if not self.model_file.exists():
            raise FileNotFoundError(f"Model not found: {self.model_file}")

    def _find_project_root(self) -> Path:
        """Find project root directory."""
        current = Path(__file__).parent
        while current.name != "CLP-RCLP Minizinc" and current.parent != current:
            current = current.parent
        return current if current.name == "CLP-RCLP Minizinc" else Path(__file__).parent.parent.parent

    def _get_model_file(self) -> Path:
        """Get model file path."""
        model_name = "clp_model.mzn" if self.model == "CLP" else "rclp_model.mzn"
        return self.project_root / "core" / "models" / model_name

    def test_solver(self, solver: str, timeout: int = 300) -> Dict:
        """
        Test a single solver.

        Returns:
            Dictionary with results
        """
        result = {
            "solver": solver,
            "success": False,
            "execution_time": None,
            "output": "",
            "error": ""
        }

        try:
            cmd = [
                "minizinc",
                "--solver", solver,
                "--time-limit", str(timeout * 1000),
                str(self.model_file),
                str(self.instance_path)
            ]

            start_time = time.time()

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )

            result["execution_time"] = time.time() - start_time

            if process.returncode == 0:
                result["success"] = True
                result["output"] = process.stdout[:500]  # First 500 chars
            else:
                result["error"] = process.stderr[:500]

        except subprocess.TimeoutExpired:
            result["execution_time"] = timeout
            result["error"] = "Execution timed out"
        except Exception as e:
            result["error"] = str(e)

        return result

    def run_all_tests(self) -> List[Dict]:
        """Run tests on all solvers."""
        print(f"\nTesting instance: {self.instance_path.name}")
        print(f"Model: {self.model}")
        print(f"Solvers: {', '.join(self.solvers)}\n")

        results = []

        for solver in self.solvers:
            print(f"Testing {solver}...", end=" ", flush=True)
            result = self.test_solver(solver)
            results.append(result)

            status = "[OK]" if result["success"] else "[FAIL]"
            time_str = f"{result['execution_time']:.3f}s" if result["execution_time"] else "N/A"
            print(f"{status} ({time_str})")

        return results

    def print_report(self, results: List[Dict]) -> None:
        """Print formatted results."""
        print("\n" + "=" * 80)
        print("MULTI-SOLVER TEST RESULTS")
        print("=" * 80)
        print(f"Instance: {self.instance_path.name}")
        print(f"Model: {self.model}")
        print("-" * 80)

        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        print(f"\nSuccessful: {len(successful)}/{len(results)} solvers\n")

        if successful:
            print("SUCCESSFUL SOLVERS (sorted by execution time):")
            print("-" * 80)
            for result in sorted(successful, key=lambda r: r["execution_time"] or float('inf')):
                print(f"  {result['solver']:15} - {result['execution_time']:.3f}s")

        if failed:
            print("\nFAILED SOLVERS:")
            print("-" * 80)
            for result in failed:
                error_msg = result["error"][:60] if result["error"] else "Unknown error"
                print(f"  {result['solver']:15} - {error_msg}")

        print("\n" + "=" * 80 + "\n")

    def save_results(self, output_dir: Optional[str] = None) -> str:
        """Save results to JSON file."""
        if not output_dir:
            output_dir = str(self.project_root / "experiments" / "results" / "solver_tests")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        instance_name = self.instance_path.stem
        output_file = Path(output_dir) / f"{instance_name}_multi_solver_results.json"

        # Get results
        results = self.run_all_tests()

        # Prepare data
        data = {
            "instance": str(self.instance_path),
            "model": self.model,
            "results": results,
            "summary": {
                "total_solvers": len(results),
                "successful": len([r for r in results if r["success"]]),
                "failed": len([r for r in results if not r["success"]])
            }
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Results saved: {output_file}")
        return str(output_file)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/solvers/test_multiple_solvers.py <instance_path> [model] [solvers...]")
        print(r"Example: python scripts/solvers/test_multiple_solvers.py experiments/instances/battery-own/noncity_5buses-8stations.dzn CLP chuffed gecode")
        sys.exit(1)

    instance_path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "CLP"
    solvers = sys.argv[3:] if len(sys.argv) > 3 else None

    try:
        tester = MultipleSolverTester(instance_path, model, solvers)
        results = tester.run_all_tests()
        tester.print_report(results)
        tester.save_results()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
