# Scripts Directory

Collection of utility scripts for data processing, generation, testing, verification, solver checks, and warm-start experiments in the CLP-RCLP optimization framework.

## Directory Structure

The top-level `scripts/` folder now groups reusable helpers into thematic subfolders:

- `data-processing/` - Data conversion and validation helpers.
- `generation/` - Instance generation and variant builders.
- `setup/` - Environment setup and validation.
- `solvers/` - Solver discovery and smoke tests.
- `testing/` - Test suites and regression checks.
- `ui-testing/` - UI validation scripts.
- `utilities/` - Small diagnostics and one-off helpers.
- `verification/` - Model and conversion verification.
- `warm_start/` - Warm-start model, reference instances, and runner.

Root-level scripts are kept for direct execution and ad hoc diagnostics:

- `run_with_cplex.py` - Main CPLEX runner with optional warm-start artifact generation.
- `check_java_equivalence.py` - Java alignment checks.
- `compare_dzn.py`, `compare_integer_float.py` - Comparison utilities.
- `generate_instances.py`, `generate_battery_last.py`, `gen_dzn.py` - Generation helpers.
- Debug and inspection helpers under names starting with `debug_` or `inspect`.
- `test_converter_java_mode.py`, `tmp_regen_battery_java.py`, `task_script.py`, `analyze_t.py`, `explore_integer_search_variants.py` - Special-purpose scripts used during development.

## Recommended Entry Points

```bash
# Launch the application UI
cd core
python start.py

# Validate the environment
python scripts/setup/setup_and_validate.py

# Check solver availability
python scripts/solvers/check_solvers.py

# Run the main regression suite
bash scripts/testing/test_generator.sh

# Run the warm-start sample
python scripts/warm_start/run_warmstart.py --instance scripts/warm_start/instances/cork-1-line_Battery-Decided20_0.dzn --out scripts/warm_start/tmp/out_20_0.txt --time 10
```

## Folder Guides

### `data-processing/`

Convert and validate data formats.

- `convert_json_to_integer_dzn.py` - JSON to DZN conversion.
- `validate_integer_dzn.py` - DZN file validation.

### `generation/`

Create test instances and variants.

- `create_cork_variants.py` - Extract Cork single-cycle variants.
- `generate_synthetic_data.py` - Generate random instances.

### `setup/`

Configure and validate the environment.

- `setup_and_validate.py` - Validate system requirements.

### `solvers/`

Manage and test solver installation.

- `check_solvers.py` - List available solvers.
- `diagnose_solvers.py` - Diagnose solver issues.
- `test_gurobi.py` - Smoke test for Gurobi.
- `test_multiple_solvers.py` - Test multiple solvers.

### `testing/`

Execute regression and integration tests.

- `test_generator.sh` - Main test suite.
- `test_clp_preliminary.sh` - Preliminary tests.
- `test_converter.py` - Converter unit tests.
- `test_converter_integration.py` - Integration tests.
- `run_battery_project_tests.py` - Battery project tests.
- `test_initial_small_case.py` - Small-case validation.

### `ui-testing/`

Validate the UI and its core flows.

- `test_runner_ui.py` - Runner interface checks.
- `test_generator_ui.py` - Generator interface checks.

### `utilities/`

Small diagnostics and utility scripts.

- `diagnose_cork.sh` - Cork instance analysis helper.

### `verification/`

Verify converter and model correctness.

- `test_converter_against_jits2022.py` - Converter accuracy checks.
- `verify_converter_fidelity.py` - Conversion fidelity checks.
- `verify_dzn_correctness.py` - DZN output validation.
- `analyze_distance_scaling.py` - Scaling diagnostics.

### `warm_start/`

Warm-start model resources.

- `clp_model_warmstart.mzn` - Standalone warm-start MiniZinc model.
- `instances/` - Reference instances for warm-start runs.
- `run_warmstart.py` - Lightweight runner for direct warm-start experiments.

## Use Cases

### New User Setup

```bash
python scripts/setup/setup_and_validate.py
python scripts/solvers/check_solvers.py
cd core && python start.py
```

### Generate Test Data

```bash
cd core && python start.py
# Then use the Instance Generator tool

python scripts/generation/generate_synthetic_data.py --buses 10 --stops 5 --output test_instance
```

### Run Optimization Tests

```bash
bash scripts/testing/test_generator.sh
python scripts/testing/test_converter.py
```

### Convert Data Format

```bash
python scripts/data-processing/convert_json_to_integer_dzn.py data.json
```

### Warm-Start Experiment

```bash
python scripts/warm_start/run_warmstart.py --instance scripts/warm_start/instances/cork-1-line_Battery-Decided20_0.dzn --out scripts/warm_start/tmp/out_20_0.txt --time 10
```

## Notes

The warm-start flow is opt-in. The base model remains clean, and warm-start artifacts are written only under `scripts/warm_start/generated/` when `scripts/runner/run_with_cplex.py --warm-start-json ...` is used.

## Data Paths (v2.0.0)

All paths reference the reorganized repository structure:

```
../experiments/instances/           # Test instances (old: ../Data/)
../experiments/results/             # Results (old: ../Tests/)
../core/models/                     # Models (old: ../Models/)
```

## Documentation

- [data-processing/README.md](data-processing/README.md)
- [generation/README.md](generation/README.md)
- [runner/README.md](runner/README.md)
- [setup/README.md](setup/README.md)
- [solvers/README.md](solvers/README.md)
- [testing/README.md](testing/README.md)
- [ui-testing/README.md](ui-testing/README.md)
- [utilities/README.md](utilities/README.md)
- [verification/README.md](verification/README.md)
- [warm_start/README.md](warm_start/README.md)
- [debug/README.md](debug/README.md)

## Data Paths (v2.0.0)

All paths reference the new structure:

```
../experiments/instances/           # Test instances (old: ../Data/)
├── battery-project-integer/
├── battery-project-variant/
├── battery-generated/
└── battery-own/

../experiments/results/             # Results (old: ../Tests/)
└── Diagnostics/

../core/models/                     # Models (old: ../Models/)
├── clp_model.mzn
├── rclp_model.mzn
└── archive/
```

## System Requirements

- **Python**: 3.8+
- **MiniZinc**: 2.6+
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 2GB for solvers and test data

## Dependencies

All scripts use only Python standard library and MiniZinc CLI.

Optional Python packages:
- `pytest` (for testing)
- `numpy` (for some analysis scripts)

## Running Tests

### Full Test Suite (Recommended)

```bash
cd scripts
bash testing/test_generator.sh
```

### Individual Tests

```bash
# Data processing
python data-processing/validate_integer_dzn.py ../experiments/instances/*.dzn

# Generation
python generation/generate_synthetic_data.py --test

# Conversion
python testing/test_converter.py

# Solver verification
python solvers/test_multiple_solvers.py
```

## Maintenance

- **Paths**: All scripts use relative paths from `scripts/` directory
- **Python Version**: 3.8+ required
- **Encoding**: UTF-8
- **Cross-platform**: Windows, Linux, macOS compatible

## Contributing

To add new scripts:

1. Choose appropriate category directory
2. Create script file following naming convention
3. Add documentation to category README.md
4. Update relative paths if needed
5. Test with multiple solvers if applicable

## Documentation

For detailed information:

- [data-processing/README.md](data-processing/README.md) - Data tools
- [generation/README.md](generation/README.md) - Generation tools
- [setup/README.md](setup/README.md) - Setup procedures
- [solvers/README.md](solvers/README.md) - Solver management
- [testing/README.md](testing/README.md) - Test procedures
- [ui-testing/README.md](ui-testing/README.md) - UI testing
- [utilities/README.md](utilities/README.md) - Diagnostics

---

**Version**: 2.1.0  
**Last Updated**: April 20, 2026  
**Structure**: clp-rclp-framework pattern
