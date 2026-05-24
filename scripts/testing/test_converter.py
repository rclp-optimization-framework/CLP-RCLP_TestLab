#!/usr/bin/env python3
"""
Converter Verification Script

Tests JSON to DZN conversion functionality with a sample from JITS2022.
Validates conversion output and reports success/failure.

Usage:
    python scripts/testing/test_converter.py

Author: AVISPA Research Team
Date: April 2026
"""

import sys
import json
import logging
from pathlib import Path
from typing import Tuple

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.jits_analyzer import JITSAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Find project root directory."""
    return Path(__file__).resolve().parents[2]


def test_converter() -> Tuple[bool, str]:
    """
    Test converter with a sample JSON file.

    Returns:
        (success: bool, message: str)
    """
    try:
        project_root = get_project_root()

        logger.info("=" * 80)
        logger.info("CONVERTER VERIFICATION TEST")
        logger.info("=" * 80)

        # Find a test JSON file
        jits_path = project_root / "external" / "jits2022" / "Code" / "data"
        if not jits_path.exists():
            return False, f"JITS path not found: {jits_path}"

        # Get first directory with JSON files
        directories = JITSAnalyzer.get_test_directories(jits_path)
        if not directories:
            return False, "No JITS test directories found"

        test_dir = jits_path / directories[0]
        json_files = JITSAnalyzer.get_json_files(test_dir, "buses_input_*.json")

        if not json_files:
            return False, f"No JSON files found in {test_dir.name}"

        # Test with first JSON file
        test_json = json_files[0]
        logger.info(f"Testing with: {test_dir.name}/{test_json.name}")

        # Validate JSON structure
        is_valid, error_msg = JITSAnalyzer.validate_json_file(test_json)
        if not is_valid:
            return False, f"JSON validation failed: {error_msg}"

        logger.info(f"✓ JSON validation passed")

        # Extract metadata
        metadata = JITSAnalyzer.get_json_metadata(test_json)
        logger.info(f"✓ Metadata extracted:")
        logger.info(f"  - Buses: {metadata.get('num_buses')}")
        logger.info(f"  - Stations: {metadata.get('num_stations')}")
        logger.info(f"  - Lines: {metadata.get('num_lines')}")

        # Test conversion
        output_dir = project_root / "experiments" / "results" / "Temp_Converter_Test"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{test_json.stem}_test.dzn"

        logger.info(f"Converting to DZN...")
        success, message = ConverterEngine.convert_json_to_dzn(test_json, output_file)

        if not success:
            return False, f"Conversion failed: {message}"

        logger.info(f"✓ Conversion successful: {message}")

        # Validate output file
        if not output_file.exists():
            return False, "Output DZN file was not created"

        # Check file size
        file_size = output_file.stat().st_size
        if file_size < 1000:
            return False, f"Output file too small: {file_size} bytes"

        logger.info(f"✓ Output file created: {file_size} bytes")

        # Validate DZN structure
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_sections = ['num_buses', 'num_stations', 'st_bi', 'D', 'T', 'tau_bi']
        missing_sections = [s for s in required_sections if s not in content]

        if missing_sections:
            return False, f"DZN missing required sections: {missing_sections}"

        logger.info(f"✓ DZN structure validation passed")
        logger.info(f"  - All required sections present")

        # Cleanup
        output_file.unlink()
        output_dir.rmdir()

        logger.info("=" * 80)
        logger.info("ALL TESTS PASSED ✓")
        logger.info("=" * 80)

        return True, "Converter verification successful"

    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        return False, f"Exception: {str(e)}"


def main():
    """Run converter verification."""
    success, message = test_converter()

    if success:
        logger.info(message)
        sys.exit(0)
    else:
        logger.error(message)
        sys.exit(1)


if __name__ == "__main__":
    main()
