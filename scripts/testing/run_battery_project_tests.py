#!/usr/bin/env python3
"""
================================================================================
Battery Project Integer - Comprehensive Test Runner
================================================================================

Professional test execution system that:
- Runs all test cases from Battery Project Integer
- Manages execution runs in separate result directories
- Handles interruptions gracefully
- Generates comprehensive reports
- Supports resume functionality

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
import argparse
import signal

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_FILE = "clp_model.mzn"
DEFAULT_SOLVER = "cplex"
DEFAULT_TIME_LIMIT_MS = 300000  # 5 minutes per test
RESULTS_BASE_DIR = "experiments/results/runner"
DIAGNOSTICS_BASE_DIR = "experiments/results/diagnostics"

# ============================================================================
# LOGGING SETUP
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = ColoredFormatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# ============================================================================
# GLOBAL STATE FOR SIGNAL HANDLING
# ============================================================================

_interrupted = False


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global _interrupted
    logger.warning("\n⚠ Interrupt received. Finishing current test and saving results...")
    _interrupted = True


signal.signal(signal.SIGINT, signal_handler)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_next_run_number(base_dir: Path) -> int:
    """Get the next available run number."""
    if not base_dir.exists():
        return 1

    existing_runs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith('Run_')]

    if not existing_runs:
        return 1

    numbers = []
    for run_dir in existing_runs:
        try:
            num = int(run_dir.name.split('_')[1])
            numbers.append(num)
        except (IndexError, ValueError):
            continue

    return max(numbers) + 1 if numbers else 1


def create_run_directory(base_dir: Path, run_number: int) -> Path:
    """Create a new run directory."""
    run_dir = base_dir / f"Run_{run_number}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


# ============================================================================
# TEST EXECUTION FUNCTIONS
# ============================================================================

def run_test_case(model_file: Path, data_file: Path, time_limit_ms: int, solver: str) -> dict:
    """
    Execute a single test case with MiniZinc.

    Args:
        model_file: Path to .mzn model
        data_file: Path to .dzn data
        time_limit_ms: Time limit in milliseconds

    Returns:
        Dictionary with test results
    """
    cmd = [
        "minizinc",
        "--solver", solver,
        "--time-limit", str(time_limit_ms),
        "-s",  # Statistics
        "--json-stream",  # JSON output for easier parsing
        str(model_file),
        str(data_file)
    ]

    start_time = datetime.now()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=(time_limit_ms / 1000) + 15  # 15s buffer
        )

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'elapsed_time': elapsed,
            'returncode': result.returncode,
            'timed_out': False
        }

    except subprocess.TimeoutExpired:
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        return {
            'success': False,
            'stdout': "",
            'stderr': "Timeout exceeded",
            'elapsed_time': elapsed,
            'returncode': -1,
            'timed_out': True
        }

    except Exception as e:
        return {
            'success': False,
            'stdout': "",
            'stderr': f"Execution error: {str(e)}",
            'elapsed_time': 0,
            'returncode': -2,
            'timed_out': False
        }


def parse_json_stream_output(output: str) -> dict:
    """Parse MiniZinc JSON stream output."""
    solution_info = {
        'solution_found': False,
        'optimal': False,
        'num_stations': None,
        'deviation': None,
        'solve_time': None,
        'nodes': None
    }

    try:
        lines = output.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue

            try:
                data = json.loads(line)

                if data.get('type') == 'solution':
                    solution_info['solution_found'] = True
                    output_data = data.get('output', {})

                    # Try to extract from output (model output format)
                    if 'dzn' in output_data:
                        dzn_text = output_data['dzn']
                        # Parse DZN output
                        # This is simplified - adapt to your model's output format

                elif data.get('type') == 'status':
                    status = data.get('status', '')
                    if status in ['OPTIMAL_SOLUTION', 'ALL_SOLUTIONS']:
                        solution_info['optimal'] = True

                elif data.get('type') == 'statistics':
                    stats = data.get('statistics', {})
                    solution_info['solve_time'] = stats.get('solveTime')
                    solution_info['nodes'] = stats.get('nodes')

            except json.JSONDecodeError:
                # If not JSON, might be regular output
                if "Total estaciones:" in line:
                    try:
                        solution_info['num_stations'] = int(line.split(':')[-1].strip())
                        solution_info['solution_found'] = True
                    except:
                        pass

                if "Desviacion total:" in line:
                    try:
                        solution_info['deviation'] = int(line.split(':')[-1].strip())
                    except:
                        pass

                if "==========" in line:
                    solution_info['optimal'] = True

    except Exception as e:
        logger.debug(f"Error parsing output: {e}")

    return solution_info


def save_test_result(result: dict, output_file: Path):
    """Save test result to file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"Test Case: {result['case_name']}\n")
        f.write(f"Timestamp: {result['timestamp']}\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Status: {'SUCCESS' if result['success'] else 'FAILED'}\n")
        f.write(f"Elapsed Time: {result['elapsed_time']:.2f}s\n")
        f.write(f"Timed Out: {'Yes' if result['timed_out'] else 'No'}\n")
        f.write(f"Return Code: {result['returncode']}\n\n")

        if result['solution_found']:
            f.write("SOLUTION FOUND:\n")
            f.write(f"  Optimal: {'Yes' if result['optimal'] else 'No'}\n")
            if result['num_stations'] is not None:
                f.write(f"  Stations Installed: {result['num_stations']}\n")
            if result['deviation'] is not None:
                f.write(f"  Total Deviation: {result['deviation']}\n")
            if result['solve_time'] is not None:
                f.write(f"  Solve Time: {result['solve_time']:.2f}s\n")
            if result['nodes'] is not None:
                f.write(f"  Nodes Explored: {result['nodes']}\n")
        else:
            f.write("NO SOLUTION FOUND\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("STANDARD OUTPUT:\n")
        f.write("=" * 80 + "\n")
        f.write(result['stdout'])

        if result['stderr']:
            f.write("\n" + "=" * 80 + "\n")
            f.write("STANDARD ERROR:\n")
            f.write("=" * 80 + "\n")
            f.write(result['stderr'])


def generate_summary_report(results: list, summary_file: Path, run_info: dict):
    """Generate comprehensive summary report."""
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("BATTERY PROJECT INTEGER - TEST EXECUTION SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Run Number: {run_info['run_number']}\n")
        f.write(f"Start Time: {run_info['start_time']}\n")
        f.write(f"End Time: {run_info['end_time']}\n")
        f.write(f"Duration: {run_info['duration']:.2f}s\n")
        f.write(f"Interrupted: {'Yes' if run_info['interrupted'] else 'No'}\n\n")

        # Statistics
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        failed = total - successful
        solutions_found = sum(1 for r in results if r['solution_found'])
        optimal_solutions = sum(1 for r in results if r['optimal'])
        timeouts = sum(1 for r in results if r['timed_out'])

        f.write("=" * 80 + "\n")
        f.write("STATISTICS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total Tests: {total}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Solutions Found: {solutions_found}\n")
        f.write(f"Optimal Solutions: {optimal_solutions}\n")
        f.write(f"Timeouts: {timeouts}\n\n")

        # Detailed results
        f.write("=" * 80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 80 + "\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"{i}. {result['case_name']}\n")
            f.write(f"   Status: {'✓ SUCCESS' if result['success'] else '✗ FAILED'}\n")
            f.write(f"   Time: {result['elapsed_time']:.2f}s")

            if result['timed_out']:
                f.write(" (TIMEOUT)")

            f.write("\n")

            if result['solution_found']:
                f.write(f"   Solution: {'OPTIMAL' if result['optimal'] else 'FEASIBLE'}\n")
                if result['num_stations'] is not None:
                    f.write(f"   Stations: {result['num_stations']}\n")
            else:
                f.write("   Solution: NONE\n")

            f.write("\n")


# ============================================================================
# MODEL SELECTION
# ============================================================================

def detect_dzn_precision(dzn_file: Path) -> str:
    """
    Detect if a DZN file contains float or integer data.
    
    Returns:
        'float' if data contains decimal values, 'int' otherwise
    """
    try:
        with open(dzn_file, 'r', encoding='utf-8') as f:
            content = f.read(2000)  # Check first 2KB
            
            # Look for float patterns: decimal points in numeric values
            # But not in comments
            lines = [l for l in content.split('\n') if not l.strip().startswith('%')]
            text = ' '.join(lines)
            
            # Check for float indicators
            import re
            # Pattern: number with decimal point (e.g., 100.0, 0.123)
            float_pattern = r'=\s*[\d\.]+-?[\d\.]+(?:\.|e)[\d\.]+'
            if re.search(float_pattern, text) or '.0' in text or '0.0' in text:
                return 'float'
            
            return 'int'
    except Exception as e:
        logger.warning(f"Could not determine precision for {dzn_file}: {e}. Assuming int.")
        return 'int'


def select_model_file(project_root: Path, data_dir: Path, dzn_file: Path = None) -> tuple:
    """
    Select appropriate model file based on data precision.
    
    Returns:
        (model_file: Path, precision: str)
    """
    # Auto-detect precision from first DZN file if available
    if dzn_file:
        precision = detect_dzn_precision(dzn_file)
    else:
        # Check first DZN in data directory
        first_dzn = next((project_root / data_dir).rglob('*.dzn'), None) if data_dir else None
        precision = detect_dzn_precision(first_dzn) if first_dzn else 'int'
    
    model_name = "clp_model_float.mzn" if precision == 'float' else "clp_model.mzn"
    model_file = project_root / "core" / "models" / model_name
    
    return model_file, precision


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Run Battery Project Integer tests')
    parser.add_argument('--data-dir', type=str, default='experiments/instances/battery-converted',
                        help='Path to data directory (default: experiments/instances/battery-converted)')
    parser.add_argument('--time-limit', type=int, default=DEFAULT_TIME_LIMIT_MS,
                        help=f'Time limit per test in milliseconds (default: {DEFAULT_TIME_LIMIT_MS})')
    parser.add_argument('--pattern', type=str, default='*.dzn',
                        help='File pattern to match (default: *.dzn)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of tests to run')
    parser.add_argument('--solver', type=str, default=DEFAULT_SOLVER,
                        help=f'MiniZinc solver id (default: {DEFAULT_SOLVER})')

    args = parser.parse_args()

    # Setup paths
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / args.data_dir
    results_base = project_root / RESULTS_BASE_DIR

    # Validate data directory first
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        logger.error("Run convert_json_to_integer_dzn.py first!")
        sys.exit(1)

    # Get test cases
    test_files = sorted(data_dir.rglob(args.pattern))

    if not test_files:
        logger.error(f"No test files found matching pattern: {args.pattern}")
        sys.exit(1)

    # Auto-detect and select appropriate model
    model_file, precision = select_model_file(project_root, data_dir, test_files[0])

    if not model_file.exists():
        logger.error(f"Model file not found: {model_file}")
        sys.exit(1)

    if args.limit:
        test_files = test_files[:args.limit]

    # Create run directory
    run_number = get_next_run_number(results_base)
    run_dir = create_run_directory(results_base, run_number)

    # Setup logging to file
    log_file = run_dir / "execution.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(file_handler)

    # Print header
    logger.info("=" * 80)
    logger.info("BATTERY PROJECT INTEGER - COMPREHENSIVE TEST EXECUTION")
    logger.info("=" * 80)
    logger.info(f"Run Number: {run_number}")
    logger.info(f"Results Directory: {run_dir}")
    logger.info(f"Data Directory: {args.data_dir}")
    logger.info(f"Data Precision: {precision.upper()}")
    logger.info(f"Model: {model_file.name}")
    logger.info(f"Solver: {args.solver}")
    logger.info(f"Time Limit: {args.time_limit / 1000}s per test")
    logger.info(f"Total Tests: {len(test_files)}")
    logger.info("=" * 80)
    logger.info("")

    # Run tests
    start_time = datetime.now()
    results = []

    for idx, test_file in enumerate(test_files, 1):
        if _interrupted:
            logger.warning("Execution interrupted by user. Stopping...")
            break

        case_name = test_file.stem

        logger.info(f"[{idx}/{len(test_files)}] Testing: {case_name}")
        logger.info("-" * 80)

        test_result = run_test_case(model_file, test_file, args.time_limit, args.solver)

        # Parse solution info
        if test_result['success']:
            solution_info = parse_json_stream_output(test_result['stdout'])
        else:
            solution_info = {
                'solution_found': False,
                'optimal': False,
                'num_stations': None,
                'deviation': None,
                'solve_time': None,
                'nodes': None
            }

        # Compile result
        result = {
            'case_name': case_name,
            'timestamp': datetime.now().isoformat(),
            'success': test_result['success'],
            'elapsed_time': test_result['elapsed_time'],
            'timed_out': test_result['timed_out'],
            'returncode': test_result['returncode'],
            'stdout': test_result['stdout'],
            'stderr': test_result['stderr'],
            **solution_info
        }

        results.append(result)

        # Save individual result under run Output directory
        output_dir = run_dir / "Output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{case_name}.txt"
        save_test_result(result, output_file)

        # Save diagnostics for failed/unknown cases organized by battery type
        try:
            # Derive battery type from data directory structure: first component under data_dir
            rel = test_file.relative_to(data_dir)
            battery_type = rel.parts[0] if len(rel.parts) > 1 else rel.stem
        except Exception:
            battery_type = "unknown"

        if (not result['success']) or result['timed_out'] or (not result['solution_found']):
            diag_dir = project_root / DIAGNOSTICS_BASE_DIR / battery_type / case_name
            diag_dir.mkdir(parents=True, exist_ok=True)
            # Save diagnostic details
            diag_file = diag_dir / "error.txt"
            save_test_result(result, diag_file)

        # Log result
        if result['success']:
            status_icon = "✓"
            status_color = "\033[32m"  # Green
        else:
            status_icon = "✗"
            status_color = "\033[31m"  # Red

        logger.info(f"{status_color}{status_icon} {case_name}: {result['elapsed_time']:.2f}s\033[0m")

        if result['solution_found']:
            logger.info(f"  Solution: {'OPTIMAL' if result['optimal'] else 'FEASIBLE'}")
            if result['num_stations'] is not None:
                logger.info(f"  Stations: {result['num_stations']}")
        elif result['timed_out']:
            logger.warning(f"  TIMEOUT")
        else:
            logger.warning(f"  NO SOLUTION")

        logger.info("")

    end_time = datetime.now()

    # Generate summary
    run_info = {
        'run_number': run_number,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration': (end_time - start_time).total_seconds(),
        'interrupted': _interrupted
    }

    summary_file = run_dir / "SUMMARY.txt"
    generate_summary_report(results, summary_file, run_info)

    # Print summary
    logger.info("=" * 80)
    logger.info("EXECUTION COMPLETED")
    logger.info("=" * 80)
    logger.info(f"Total Tests: {len(results)}")
    logger.info(f"Successful: {sum(1 for r in results if r['success'])}")
    logger.info(f"Failed: {sum(1 for r in results if not r['success'])}")
    logger.info(f"Solutions Found: {sum(1 for r in results if r['solution_found'])}")
    logger.info(f"Duration: {run_info['duration']:.2f}s")
    logger.info("")
    logger.info(f"Results saved to: {run_dir}")
    logger.info(f"Summary: {summary_file}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
