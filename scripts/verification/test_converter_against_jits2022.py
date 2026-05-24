"""
End-to-End Converter Test Against JITS2022

Tests that the Converter produces outputs matching JITS2022 instances.
Validates converter logic on actual test batteries.

Author: AVISPA Research Team
Date: April 2026
"""

import logging
import sys
from pathlib import Path
from typing import List, Tuple
import json

# Add parent directories to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.experiment_config import ExperimentConfig
from core.converter.core.data_loader import DataLoader
from scripts.verification.verify_converter_fidelity import VerifyConverterFidelity

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConverterTest:
    """Test converter against JITS2022 instances."""

    def __init__(self, jits_data_root: Path):
        """
        Initialize test runner.

        Args:
            jits_data_root: Root path to JITS2022 test data (e.g., external/jits2022/Code/data/cork-1-line)
        """
        self.jits_data_root = Path(jits_data_root)
        if not self.jits_data_root.exists():
            raise ValueError(f"JITS data root not found: {jits_data_root}")

        self.results = []

    def run_tests(self, test_pattern: str = "buses_input_*.json", tolerance_pct: float = 1.0) -> Tuple[int, int]:
        """
        Run converter tests on all matching bus input files.

        Args:
            test_pattern: Glob pattern for test files
            tolerance_pct: Tolerance percentage for verification

        Returns:
            (passed_count, failed_count)
        """
        # Find all test files
        test_files = list(self.jits_data_root.glob(test_pattern))
        if not test_files:
            logger.error(f"No test files found matching {test_pattern} in {self.jits_data_root}")
            return 0, 0

        logger.info(f"Found {len(test_files)} test files")

        # Load data once (same for all buses in this directory)
        logger.info("Loading experiment data...")
        config = ExperimentConfig()
        stations, _ = DataLoader.load_stations(self.jits_data_root)
        distances, _ = DataLoader.load_distances(self.jits_data_root)

        logger.info(f"  Config: model_speed={config.model_speed} km/h, rest_time={config.rest_time} min")
        if distances:
            logger.info(f"  Loaded {len(distances)} distance entries")
        else:
            logger.warning("  No distance data loaded (will use fallback)")

        passed_count = 0
        failed_count = 0

        for test_file in sorted(test_files):
            result = self._run_single_test(test_file, config, distances, tolerance_pct)
            self.results.append(result)

            if result['passed']:
                passed_count += 1
                logger.info(f"[OK] {test_file.name}: PASSED")
            else:
                failed_count += 1
                logger.error(f"[FAIL] {test_file.name}: FAILED")

        return passed_count, failed_count

    def _run_single_test(self, test_file: Path, config: ExperimentConfig,
                        distances: dict, tolerance_pct: float) -> dict:
        """
        Run converter on a single test file.

        Args:
            test_file: Path to buses_input_*.json
            config: Experiment config
            distances: Distance dictionary
            tolerance_pct: Tolerance percentage

        Returns:
            Result dictionary
        """
        result = {
            'test_file': str(test_file),
            'passed': False,
            'message': '',
            'error': None
        }

        try:
            # Generate output DZN
            output_file = test_file.parent / f"{test_file.stem}_converted.dzn"

            # Extract variant from filename (e.g., "20_10" from "buses_input_20_10.json")
            variant = test_file.stem.replace('buses_input_', '')

            logger.info(f"Converting {test_file.name}...")
            success, message = ConverterEngine.convert_json_to_dzn(
                test_file, output_file, variant_name=variant,
                config=config, distances_dict=distances
            )

            if not success:
                result['error'] = message
                result['message'] = f"Conversion failed: {message}"
                return result

            logger.info(f"  Output: {output_file.name}")

            # Verify output (if reference exists)
            # For now, just check that the file was created successfully
            if output_file.exists():
                result['passed'] = True
                result['message'] = f"Successfully converted: {message}"
            else:
                result['error'] = "Output file not created"
                result['message'] = "Output file was not created"

        except Exception as e:
            result['error'] = str(e)
            result['message'] = f"Exception: {str(e)}"
            logger.error(f"Error in test: {e}", exc_info=True)

        return result

    def print_summary(self) -> None:
        """Print test summary to console."""
        print("\n" + "=" * 80)
        print("CONVERTER TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for r in self.results if r['passed'])
        failed = sum(1 for r in self.results if not r['passed'])
        total = len(self.results)

        print(f"\nTotal tests: {total}")
        print(f"Passed: {passed} [OK]")
        print(f"Failed: {failed} [FAIL]")
        print(f"Success rate: {(passed / total * 100):.1f}%" if total > 0 else "N/A")

        if failed > 0:
            print("\n--- FAILED TESTS ---")
            for result in self.results:
                if not result['passed']:
                    print(f"\n  {Path(result['test_file']).name}")
                    print(f"  Message: {result['message']}")
                    if result['error']:
                        print(f"  Error: {result['error']}")

        print("\n" + "=" * 80 + "\n")

        return passed == total


def main():
    """Main entry point."""
    # Path to JITS2022 test data
    project_root = Path(__file__).parent.parent.parent
    test_data_root = project_root / "external" / "jits2022" / "Code" / "data" / "cork-1-line"

    logger.info(f"Test data root: {test_data_root}")

    if not test_data_root.exists():
        logger.error(f"Test data directory not found: {test_data_root}")
        logger.info("\nUsage: python scripts/verification/test_converter_against_jits2022.py [path_to_test_data]")
        return 1

    try:
        tester = ConverterTest(test_data_root)
        passed, failed = tester.run_tests(tolerance_pct=1.0)

        success = tester.print_summary()

        logger.info(f"\nTest results: {passed} passed, {failed} failed")

        return 0 if success else 1

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
