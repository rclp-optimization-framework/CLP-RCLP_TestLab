#!/usr/bin/env python3
"""
Master setup and validation script for the Integer Battery Testing System.
Runs all initialization steps in the correct order.
"""

import subprocess
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and report results."""
    logger.info("=" * 80)
    logger.info(f"STEP: {description}")
    logger.info("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, str(script_name)],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.info(f"✓ {description} - SUCCESS")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            logger.error(f"✗ {description} - FAILED")
            if result.stderr:
                print(result.stderr)
            return False

    except Exception as e:
        logger.error(f"✗ {description} - ERROR: {e}")
        return False


def main():
    """Main setup function."""
    scripts_dir = Path(__file__).parent

    logger.info("\n" + "=" * 80)
    logger.info("INTEGER BATTERY TEST SYSTEM - INITIALIZATION")
    logger.info("=" * 80 + "\n")

    steps = [
        ("validate_integer_dzn.py", "Validate existing integer DZN files"),
        ("generate_synthetic_data.py", "Generate synthetic test data"),
        ("test_initial_small_case.py", "Run initial small test cases"),
    ]

    results = []

    for script, description in steps:
        script_path = scripts_dir / script
        if not script_path.exists():
            logger.error(f"Script not found: {script}")
            results.append(False)
            continue

        success = run_script(script_path, description)
        results.append(success)

        if not success:
            logger.warning(f"Step failed, but continuing...")

        print()  # Empty line between steps

    # Final summary
    logger.info("=" * 80)
    logger.info("INITIALIZATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total steps: {len(results)}")
    logger.info(f"Successful: {sum(results)}")
    logger.info(f"Failed: {len(results) - sum(results)}")
    logger.info("")

    if all(results):
        logger.info("✓ ALL SYSTEMS READY!")
        logger.info("")
        logger.info("You can now run the full test battery:")
        logger.info("  bash scripts/testing/test_generator.sh")
        return 0
    else:
        logger.error("✗ SOME STEPS FAILED")
        logger.error("Please check the errors above and fix them before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
