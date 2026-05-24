#!/usr/bin/env python3
"""
Gurobi Configuration and Testing

Troubleshoot Gurobi solver setup and test execution.
Gurobi requires proper DLL configuration which this script helps diagnose.

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
Usage: python scripts/solvers/test_gurobi.py [instance_path] [model]
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import time
import os
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class GurobiTester:
    """Test and diagnose Gurobi solver configuration."""

    def __init__(self, instance_path: str, model: str = "CLP"):
        """Initialize tester."""
        self.instance_path = Path(instance_path)
        self.model = model
        self.project_root = self._find_project_root()
        self.model_file = self._get_model_file()

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

    def check_gurobi_installation(self) -> Dict:
        """Check Gurobi installation status."""
        print("\n[Checking Gurobi Installation]")
        print("-" * 70)

        result = {
            "minizinc_available": False,
            "dll_path": None,
            "env_variable": None,
            "home_directory": None
        }

        # Check if Gurobi solver is listed in MiniZinc
        try:
            out = subprocess.run(
                ["minizinc", "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if "gurobi" in out.stdout.lower():
                result["minizinc_available"] = True
                print("  [OK] MiniZinc recognizes Gurobi solver")
            else:
                print("  [WARN] Gurobi not listed in MiniZinc solvers")

        except Exception as e:
            print(f"  [ERROR] Could not check MiniZinc: {e}")

        # Check environment variables
        if "GUROBI_HOME" in os.environ:
            result["home_directory"] = os.environ["GUROBI_HOME"]
            print(f"  [OK] GUROBI_HOME set: {result['home_directory']}")
        else:
            print("  [WARN] GUROBI_HOME not set")

        # Try to find DLL
        dll_paths = [
            Path("C:/gurobi/win64/bin/gurobi.dll"),
            Path("C:/Program Files/Gurobi/win64/bin/gurobi.dll"),
            Path("C:/Program Files (x86)/Gurobi/win64/bin/gurobi.dll"),
        ]

        if "GUROBI_HOME" in os.environ:
            dll_paths.insert(0, Path(os.environ["GUROBI_HOME"]) / "bin" / "gurobi.dll")

        for dll_path in dll_paths:
            if dll_path.exists():
                result["dll_path"] = str(dll_path)
                print(f"  [OK] Found DLL: {dll_path}")
                break

        if not result["dll_path"]:
            print("  [WARN] Could not find gurobi.dll in standard locations")

        return result

    def test_without_dll_specification(self, timeout: int = 5) -> Dict:
        """Test Gurobi without --gurobi-dll parameter."""
        print("\n[Test 1: Direct execution (without DLL specification)]")
        print("-" * 70)

        try:
            cmd = [
                "minizinc",
                "--solver", "gurobi",
                "--time-limit", str(timeout * 1000),
                str(self.model_file),
                str(self.instance_path)
            ]

            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
            exec_time = time.time() - start_time

            if result.returncode == 0:
                print(f"  [OK] Execution successful in {exec_time:.3f}s")
                return {"success": True, "time": exec_time}
            else:
                error = result.stderr.strip()
                print(f"  [FAIL] Error: {error[:100]}")
                return {"success": False, "error": error, "time": exec_time}

        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Exceeded {timeout}s")
            return {"success": False, "error": "Timeout", "time": timeout}
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return {"success": False, "error": str(e), "time": 0}

    def test_with_dll_specification(self, dll_path: str, timeout: int = 5) -> Dict:
        """Test Gurobi with explicit DLL path."""
        print(f"\n[Test 2: With DLL specification]")
        print(f"DLL Path: {dll_path}")
        print("-" * 70)

        try:
            # Try Windows path conversion
            if dll_path.startswith("/c/"):
                dll_path_windows = dll_path.replace("/c/", "C:/")
            else:
                dll_path_windows = dll_path

            cmd = [
                "minizinc",
                "--solver", "gurobi",
                "--gurobi-dll", dll_path_windows,
                "--time-limit", str(timeout * 1000),
                str(self.model_file),
                str(self.instance_path)
            ]

            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
            exec_time = time.time() - start_time

            if result.returncode == 0:
                print(f"  [OK] Execution successful in {exec_time:.3f}s")
                return {"success": True, "time": exec_time}
            else:
                error = result.stderr.strip()
                # Check for license error
                if "No Gurobi license found" in error:
                    print(f"  [LICENSE] Gurobi found but no valid license")
                    print(f"           Error: {error[:100]}")
                    return {"success": False, "error": "No license", "time": exec_time, "license_required": True}
                else:
                    print(f"  [FAIL] Error: {error[:100]}")
                    return {"success": False, "error": error, "time": exec_time}

        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Exceeded {timeout}s")
            return {"success": False, "error": "Timeout", "time": timeout}
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return {"success": False, "error": str(e), "time": 0}

    def generate_report(self) -> Dict:
        """Generate comprehensive Gurobi status report."""
        print("\n" + "=" * 70)
        print("GUROBI SOLVER DIAGNOSIS REPORT")
        print("=" * 70)
        print(f"Instance: {self.instance_path.name}")
        print(f"Model: {self.model}")

        # Check installation
        install_info = self.check_gurobi_installation()

        # Test without DLL
        test1_result = self.test_without_dll_specification()

        # Test with DLL if found
        test2_result = None
        if install_info["dll_path"]:
            test2_result = self.test_with_dll_specification(install_info["dll_path"])
        else:
            # Try with GUROBI_HOME
            if install_info["home_directory"]:
                dll_candidate = Path(install_info["home_directory"]) / "bin" / "gurobi130.dll"
                if dll_candidate.exists():
                    print(f"\n[Found DLL at GUROBI_HOME: {dll_candidate}]")
                    test2_result = self.test_with_dll_specification(str(dll_candidate))

        # Generate summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        if test1_result["success"]:
            print("[OK] Gurobi is working correctly!")
            status = "working"
        elif test2_result and test2_result.get("license_required"):
            print("[GUROBI FOUND] Gurobi installation found but no valid license")
            print(f"    Binary: Found at {install_info.get('home_directory', 'GUROBI_HOME')}")
            print("    Status: License required for full operation")
            status = "needs_license"
        elif test2_result and test2_result["success"]:
            print("[OK] Gurobi works with explicit DLL path")
            print(f"    Use: --gurobi-dll {install_info['dll_path']}")
            status = "working_with_dll"
        elif install_info["dll_path"] or install_info["home_directory"]:
            print("[GUROBI CONFIGURED] Gurobi binary found but not working")
            print(f"    Home: {install_info.get('home_directory', 'Not set')}")
            print("    Status: Needs license configuration")
            status = "needs_license"
        else:
            print("[NOT INSTALLED] Gurobi not found on system")
            status = "not_installed"

        print("=" * 70)

        report = {
            "status": status,
            "installation_info": install_info,
            "test_direct": test1_result,
            "test_with_dll": test2_result,
            "recommendation": self._get_recommendation(status)
        }

        return report

    def _get_recommendation(self, status: str) -> str:
        """Get recommendation based on status."""
        recommendations = {
            "working": "Gurobi is working. No action needed.",
            "working_with_dll": "Gurobi works when DLL path is specified. Consider environment variable setup.",
            "needs_license": "Gurobi binary found. Install valid Gurobi license: https://www.gurobi.com/",
            "needs_config": "Install Gurobi or set GUROBI_HOME environment variable.",
            "not_installed": "Gurobi not found. Download from https://www.gurobi.com/"
        }
        return recommendations.get(status, "Unknown status")

    def save_report(self, report: Dict, output_path: Optional[str] = None) -> str:
        """Save report as JSON."""
        if not output_path:
            output_dir = self.project_root / "experiments" / "results" / "diagnostics"
        else:
            output_dir = Path(output_path)

        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "gurobi_test_report.json"

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return str(output_file)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/solvers/test_gurobi.py <instance_path> [model]")
        print("Example: python scripts/solvers/test_gurobi.py experiments/instances/battery-own/noncity_5buses-8stations.dzn CLP")
        sys.exit(1)

    instance_path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "CLP"

    try:
        tester = GurobiTester(instance_path, model)
        report = tester.generate_report()
        output_file = tester.save_report(report)
        print(f"\nReport saved: {output_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
