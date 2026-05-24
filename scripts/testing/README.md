# Testing Scripts

Scripts for validation, testing, and verification of the complete CLP-RCLP system.

## Contents

### `test_generator.sh` (MAIN)
Comprehensive testing script for the instance generation system.

**Usage**:
```bash
bash scripts/testing/test_generator.sh
```

**Tests Included**:
1. Verify Cork variants exist
2. Verify generator script availability
3. Verify MiniZinc installation
4. Validate Cork variant with CLP model
5. Verify generated directory structure
6. Validate existing generated instance
7. Verify complete documentation

**Output**: Detailed report with color and statistics

### `test_clp_preliminary.sh`
Preliminary tests to validate basic CLP model functionality.

**Usage**:
```bash
bash scripts/testing/test_clp_preliminary.sh
```

### `run_battery_project_tests.py`
Test suite for Battery project instances.

**Usage**:
```bash
python scripts/testing/run_battery_project_tests.py [options]
```

### `test_initial_small_case.py`
Initial small case tests to verify basic functionality.

**Usage**:
```bash
python scripts/testing/test_initial_small_case.py
```

## Test Workflow

```
test_generator.sh (MAIN)
├── Validate Cork variants
├── Validate installation (MiniZinc)
├── Solve instances
└── Final report

Then:
├── scripts/testing/run_battery_project_tests.py (complete validation)
└── scripts/testing/test_clp_preliminary.sh (diagnostics)
```

## Dependencies
- bash (for .sh scripts)
- Python 3.8+ (for .py scripts)
- MiniZinc 2.5+ (for validation)
- minizinc Python module (for some scripts)

## Expected Results
- **SUCCESS**: 100% test pass rate, all instances SATISFIABLE
- **INFO**: Expected warnings for Cork (complex instances)
- **TIMEOUT**: Acceptable for very large instances (>20 buses)

## Related Documentation
- Main test guide: `../../docs/overview/README.md`
- Model info: `../../core/models/`
