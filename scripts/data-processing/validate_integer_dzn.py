#!/usr/bin/env python3
"""
================================================================================
DZN File Validator for Integer Electric Bus Charging Station Data
================================================================================

This script validates converted DZN files to ensure:
1. All values are integers (no floating-point)
2. Scaling is consistent
3. Data relationships are maintained
4. No invalid or out-of-range values

Author: EV-CLP Battery Project
Date: 2026-03-25
================================================================================
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import logging

# ============================================================================
# CONFIGURATION
# ============================================================================

SCALE = 10

# Expected integer parameters
EXPECTED_PARAMS = {
    'Cmax': 1000,
    'Cmin': 200,
    'alpha': 100,
    'mu': 50,
    'SM': 10,
    'psi': 10,
    'beta': 100,
    'M': 100000
}

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
# VALIDATION FUNCTIONS
# ============================================================================

def extract_parameter(content: str, param_name: str) -> any:
    """Extract a parameter value from DZN content."""
    pattern = rf'{param_name}\s*=\s*([^;]+);'
    match = re.search(pattern, content)
    if match:
        value_str = match.group(1).strip()
        try:
            return int(value_str)
        except ValueError:
            return value_str
    return None


def extract_array(content: str, array_name: str) -> List[float]:
    """
    Extract array values from DZN content.
    Returns list of values (may contain decimals if not converted properly).
    """
    pattern = rf'{array_name}\s*=\s*array2d\([^,]+,\s*[^,]+,\s*\[(.*?)\]\s*\);'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        array_content = match.group(1)
        # Remove comments
        array_content = re.sub(r'%.*$', '', array_content, flags=re.MULTILINE)
        # Extract numbers (both int and float)
        numbers = re.findall(r'-?\d+\.?\d*', array_content)
        return [float(n) for n in numbers]
    return []


def validate_no_floats(content: str, filename: str) -> Tuple[bool, List[str]]:
    """
    Validate that there are no floating-point numbers in numeric assignments.

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Check parameter assignments for floats
    param_pattern = r'(Cmax|Cmin|alpha|mu|SM|psi|beta|M)\s*=\s*(\d+\.\d+);'
    float_params = re.findall(param_pattern, content)

    for param, value in float_params:
        errors.append(f"Parameter '{param}' has float value: {value} (should be integer)")

    # Check arrays for floating-point values
    array_pattern = r'(D|T|tau_bi|st_bi)\s*=\s*array2d\([^;]+\);'
    matches = re.finditer(array_pattern, content, re.DOTALL)

    for match in matches:
        array_name = match.group(1)
        array_section = match.group(0)

        # Extract all numbers from this array
        numbers = re.findall(r'\b\d+\.\d+\b', array_section)

        if numbers:
            errors.append(f"Array '{array_name}' contains {len(numbers)} floating-point values")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_parameters(content: str, filename: str) -> Tuple[bool, List[str]]:
    """
    Validate that parameter values match expected scaled integers.

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    for param, expected_value in EXPECTED_PARAMS.items():
        actual_value = extract_parameter(content, param)

        if actual_value is None:
            errors.append(f"Parameter '{param}' not found")
        elif actual_value != expected_value:
            errors.append(f"Parameter '{param}' = {actual_value}, expected {expected_value}")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_array_consistency(content: str, filename: str) -> Tuple[bool, List[str]]:
    """
    Validate consistency between arrays and dimensions.

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Extract dimensions
    num_buses = extract_parameter(content, 'num_buses')
    num_stations = extract_parameter(content, 'num_stations')
    max_stops = extract_parameter(content, 'max_stops')

    if not all([num_buses, num_stations, max_stops]):
        errors.append("Missing dimension parameters")
        return False, errors

    # Extract arrays
    st_bi = extract_array(content, 'st_bi')
    D = extract_array(content, 'D')
    T = extract_array(content, 'T')
    tau_bi = extract_array(content, 'tau_bi')

    expected_size = num_buses * max_stops

    # Check array sizes
    if len(st_bi) != expected_size:
        errors.append(f"st_bi has {len(st_bi)} elements, expected {expected_size}")

    if len(D) != expected_size:
        errors.append(f"D has {len(D)} elements, expected {expected_size}")

    if len(T) != expected_size:
        errors.append(f"T has {len(T)} elements, expected {expected_size}")

    if len(tau_bi) != expected_size:
        errors.append(f"tau_bi has {len(tau_bi)} elements, expected {expected_size}")

    # Check that all station IDs are within range [0, num_stations-1]
    invalid_stations = [s for s in st_bi if s < 0 or s >= num_stations]
    if invalid_stations:
        errors.append(f"Found {len(invalid_stations)} invalid station IDs (outside range [0, {num_stations-1}])")

    # Check for negative values in D (energy consumption)
    negative_d = [d for d in D if d < 0]
    if negative_d:
        errors.append(f"Found {len(negative_d)} negative energy consumption values in D")

    # Check for negative values in T (time)
    negative_t = [t for t in T if t < 0]
    if negative_t:
        errors.append(f"Found {len(negative_t)} negative time values in T")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_dzn_file(file_path: Path) -> Dict[str, any]:
    """
    Comprehensive validation of a single DZN file.

    Returns:
        Dictionary with validation results
    """
    logger.info(f"Validating {file_path.name}...")

    result = {
        'file': file_path.name,
        'valid': True,
        'errors': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Run all validation checks
        checks = [
            ("No floating-point values", validate_no_floats),
            ("Parameter values", validate_parameters),
            ("Array consistency", validate_array_consistency)
        ]

        for check_name, check_func in checks:
            is_valid, errors = check_func(content, file_path.name)

            if not is_valid:
                result['valid'] = False
                result['errors'].append({
                    'check': check_name,
                    'issues': errors
                })

        if result['valid']:
            logger.info(f"  ✓ {file_path.name}: Valid")
        else:
            logger.warning(f"  ✗ {file_path.name}: {len(result['errors'])} validation issues found")

    except Exception as e:
        result['valid'] = False
        result['errors'].append({
            'check': 'File reading',
            'issues': [str(e)]
        })
        logger.error(f"  ✗ {file_path.name}: Error reading file - {e}")

    return result


def validate_directory(directory: Path) -> Dict[str, any]:
    """
    Validate all DZN files in a directory.

    Returns:
        Summary dictionary with validation results
    """
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return {'valid_files': 0, 'invalid_files': 0, 'total': 0}

    dzn_files = sorted(directory.glob("*.dzn"))

    if not dzn_files:
        logger.warning(f"No DZN files found in {directory}")
        return {'valid_files': 0, 'invalid_files': 0, 'total': 0}

    logger.info(f"Validating {len(dzn_files)} DZN files in {directory.name}...")
    logger.info("=" * 80)

    valid_count = 0
    invalid_count = 0
    all_results = []

    for dzn_file in dzn_files:
        result = validate_dzn_file(dzn_file)
        all_results.append(result)

        if result['valid']:
            valid_count += 1
        else:
            invalid_count += 1

    logger.info("=" * 80)
    logger.info(f"Validation complete: {valid_count} valid, {invalid_count} invalid (total: {len(dzn_files)})")

    # Print detailed errors for invalid files
    if invalid_count > 0:
        logger.info("\n" + "=" * 80)
        logger.info("DETAILED VALIDATION ERRORS:")
        logger.info("=" * 80)

        for result in all_results:
            if not result['valid']:
                logger.info(f"\nFile: {result['file']}")
                for error in result['errors']:
                    logger.info(f"  Check: {error['check']}")
                    for issue in error['issues']:
                        logger.info(f"    - {issue}")

    return {
        'valid_files': valid_count,
        'invalid_files': invalid_count,
        'total': len(dzn_files),
        'results': all_results
    }


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to run the validator."""
    if len(sys.argv) > 1:
        # Single file mode
        file_path = Path(sys.argv[1])

        if file_path.exists():
            result = validate_dzn_file(file_path)

            if result['valid']:
                logger.info(f"\n✓ {file_path.name} is VALID")
                sys.exit(0)
            else:
                logger.error(f"\n✗ {file_path.name} is INVALID")
                for error in result['errors']:
                    logger.error(f"  {error['check']}:")
                    for issue in error['issues']:
                        logger.error(f"    - {issue}")
                sys.exit(1)
        else:
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
    else:
        # Directory mode - validate Battery Project Integer
        project_root = Path(__file__).resolve().parents[2]
        target_dir = project_root / "experiments" / "instances" / "battery-own"

        if not target_dir.exists():
            logger.error(f"Directory not found: {target_dir}")
            logger.info("Run convert_json_to_integer_dzn.py first to generate files")
            sys.exit(1)

        logger.info("=" * 80)
        logger.info("DZN INTEGER VALIDATION")
        logger.info(f"Target: {target_dir}")
        logger.info("=" * 80 + "\n")

        summary = validate_directory(target_dir)

        logger.info("\n" + "=" * 80)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total files: {summary['total']}")
        logger.info(f"Valid files: {summary['valid_files']}")
        logger.info(f"Invalid files: {summary['invalid_files']}")

        if summary['invalid_files'] == 0:
            logger.info("\n✓ ALL FILES ARE VALID!")
            sys.exit(0)
        else:
            logger.error(f"\n✗ {summary['invalid_files']} FILES HAVE VALIDATION ERRORS")
            sys.exit(1)


if __name__ == "__main__":
    main()
