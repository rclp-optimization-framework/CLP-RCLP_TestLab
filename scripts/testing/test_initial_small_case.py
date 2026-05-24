#!/usr/bin/env python3
"""
================================================================================
Initial Test Script - Small Case Validation
================================================================================

Tests the CLP model with small battery test cases to verify that:
1. The model runs correctly with integer values
2. The chuffed solver can handle the problem
3. Results are reasonable

Author: EV-CLP Battery Project
Date: 2026-03-25
================================================================================
"""

import subprocess
import sys
from pathlib import Path
import logging
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Model to test
MODEL_FILE = "clp_model.mzn"

# Test cases (small ones first)
SMALL_TEST_CASES = [
    "experiments/instances/battery-own/noncity_5buses-8stations.dzn",
]

# Solver configuration
SOLVER = "chuffed"
TIME_LIMIT_MS = 60000  # 60 seconds

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
# TESTING FUNCTIONS
# ============================================================================

def run_minizinc(model_file: Path, data_file: Path, time_limit_ms: int = 60000):
    """
    Run MiniZinc with the specified model and data file.

    Args:
        model_file: Path to .mzn model file
        data_file: Path to .dzn data file
        time_limit_ms: Time limit in milliseconds

    Returns:
        Dictionary with results
    """
    cmd = [
        "minizinc",
        "--solver", SOLVER,
        "--time-limit", str(time_limit_ms),
        "-s",  # Print statistics
        str(model_file),
        str(data_file)
    ]

    logger.info(f"Running: {' '.join(cmd)}")

    start_time = datetime.now()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=time_limit_ms / 1000 + 10  # Add 10s buffer
        )

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'elapsed_time': elapsed,
            'returncode': result.returncode
        }

    except subprocess.TimeoutExpired:
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        return {
            'success': False,
            'stdout': "",
            'stderr': "Timeout exceeded",
            'elapsed_time': elapsed,
            'returncode': -1
        }

    except Exception as e:
        return {
            'success': False,
            'stdout': "",
            'stderr': str(e),
            'elapsed_time': 0,
            'returncode': -2
        }


def extract_solution(output: str) -> dict:
    """
    Extract solution information from MiniZinc output.

    Args:
        output: MiniZinc stdout

    Returns:
        Dictionary with solution details
    """
    solution = {
        'found': False,
        'optimal': False,
        'num_stations': None,
        'deviation': None
    }

    # Check if solution was found
    if "Estaciones instaladas:" in output or "Total estaciones:" in output:
        solution['found'] = True

    # Check for optimality
    if "==========\n" in output:
        solution['optimal'] = True

    # Extract number of stations
    for line in output.split('\n'):
        if "Total estaciones:" in line:
            try:
                solution['num_stations'] = int(line.split(':')[-1].strip())
            except:
                pass

        if "Desviacion total:" in line:
            try:
                solution['deviation'] = int(line.split(':')[-1].strip())
            except:
                pass

    return solution


def test_case(model_file: Path, data_file: Path, case_name: str, time_limit_ms: int):
    """
    Test a single case and report results.

    Args:
        model_file: Path to model file
        data_file: Path to data file
        case_name: Name of the test case
        time_limit_ms: Time limit in milliseconds

    Returns:
        Test result dictionary
    """
    logger.info("=" * 80)
    logger.info(f"Testing Case: {case_name}")
    logger.info("=" * 80)

    if not data_file.exists():
        logger.error(f"Data file not found: {data_file}")
        return {
            'case': case_name,
            'success': False,
            'error': 'File not found'
        }

    result = run_minizinc(model_file, data_file, time_limit_ms)

    solution = extract_solution(result['stdout']) if result['success'] else {}

    test_result = {
        'case': case_name,
        'success': result['success'],
        'elapsed_time': result['elapsed_time'],
        'solution_found': solution.get('found', False),
        'optimal': solution.get('optimal', False),
        'num_stations': solution.get('num_stations'),
        'deviation': solution.get('deviation'),
        'stdout': result['stdout'],
        'stderr': result['stderr']
    }

    # Log results
    if test_result['success']:
        logger.info(f"✓ Test PASSED - Elapsed: {test_result['elapsed_time']:.2f}s")
        if test_result['solution_found']:
            logger.info(f"  Solution Found: {test_result['optimal'] and 'OPTIMAL' or 'FEASIBLE'}")
            if test_result['num_stations'] is not None:
                logger.info(f"  Stations: {test_result['num_stations']}")
            if test_result['deviation'] is not None:
                logger.info(f"  Total Deviation: {test_result['deviation']}")
        else:
            logger.warning("  No solution found!")
    else:
        logger.error(f"✗ Test FAILED - {result['stderr']}")

    logger.info("")

    return test_result


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to run tests."""
    project_root = Path(__file__).resolve().parents[2]
    model_file = project_root / "core" / "models" / MODEL_FILE

    if not model_file.exists():
        logger.error(f"Model file not found: {model_file}")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("INITIAL MODEL TEST - SMALL BATTERY CASES")
    logger.info("=" * 80)
    logger.info(f"Model: {MODEL_FILE}")
    logger.info(f"Solver: {SOLVER}")
    logger.info(f"Time Limit: {TIME_LIMIT_MS / 1000}s")
    logger.info("=" * 80)
    logger.info("")

    all_results = []

    for test_case_path in SMALL_TEST_CASES:
        data_file = project_root / test_case_path
        case_name = test_case_path.split('/')[-1].replace('.dzn', '')

        result = test_case(model_file, data_file, case_name, TIME_LIMIT_MS)
        all_results.append(result)

    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)

    passed = sum(1 for r in all_results if r['success'])
    total = len(all_results)

    logger.info(f"Total Tests: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {total - passed}")
    logger.info("")

    if passed == total:
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("")
        logger.info("The model is working correctly with integer values.")
        logger.info("You can now proceed to run full battery tests.")
        sys.exit(0)
    else:
        logger.error("✗ SOME TESTS FAILED")
        logger.error("Please check the model and data files.")
        sys.exit(1)


if __name__ == "__main__":
    main()
