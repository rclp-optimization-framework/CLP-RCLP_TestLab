# CLP-RCLP v2.1.0 Release Summary

**Release Date**: May 14, 2026  
**Version**: 2.1.0 (from 2.0.0)  
**Repository**: [rclp-optimization-framework/CLP-RCLP_TestLab](https://github.com/rclp-optimization-framework/CLP-RCLP_TestLab)

## Release Overview

Version 2.1.0 consolidates comprehensive refactoring of the CLP-RCLP framework, resolving critical semantic misalignments between the original Java baseline and Python/MiniZinc implementation. This release includes:

- **Java-compatible converter mode** for semantic parity with JITS2022 baseline
- **Complete path reorganization** (legacy structure → modern core/experiments/scripts layout)
- **Critical model bug fixes** in RCLP temporal recursion
- **Robust data validation** and automated precision detection
- **Professional documentation** with installation guides and troubleshooting

## Key Changes

### 1. Java-Compatible Conversion Mode

**Problem**: Energy units and timing conventions diverged between Java baseline and Python implementation, preventing direct comparison.

**Solution**: Implemented new `java` conversion mode in converter:
- Converts energy to Java-compatible integer units (distance_km × 1000)
- Emits time values in seconds (not minutes)
- Calculates parameters aligned with JITS2022 conventions
- Provides UI option for mode selection

**Files Modified**:
- `core/converter/core/converter_engine.py` - Java mode implementation
- `core/converter/ui/interface.py` - UI option for Java/normalized modes

**Impact**: Direct verification against Java baseline now possible on identical semantics.

### 2. Repository Path Reorganization

**Migration**: All legacy paths consolidated to modern structure:

| Legacy | New |
|--------|-----|
| `Models/` | `core/models/` |
| `Converter/` | `core/converter/` |
| `Generator/` | `core/generator/` |
| `Runner/` | `core/runner/` |
| `Data/` | `experiments/instances/` |
| `Tests/` | `experiments/results/` |
| `Scripts/` | `scripts/` |

**Files Affected**: 50+ Python scripts, 8 shell scripts, 15+ documentation files

**Impact**: 
- Consistent, maintainable project layout
- Clear separation: core logic vs experiments vs utilities
- Improved discoverability and navigation

### 3. RCLP Float Model Sign Correction

**Bug**: Time recursion constraint used subtraction instead of addition:
```minizinc
# BEFORE (incorrect)
t[b,i] >= t[b,i-1] + ct[b,i-1] - T[b,i]

# AFTER (correct)
t[b,i] >= t[b,i-1] + ct[b,i-1] + T[b,i]
```

**File**: `core/models/rclp_model_float.mzn`

**Impact**: RCLP model now correctly enforces travel time constraints; enables future robustness studies.

### 4. Data-Driven Model Bounds

**Change**: Models now use data-dependent bound computation instead of hardcoded limits:

```minizinc
int: tau_max = max([tau_bi[b,i] | b in B, i in 1..num_stops[b]]);
int: t_upper_bound = tau_max + M + beta + SM + mu;

array[B,1..max_stops] of var 0..t_upper_bound: tbi;
```

**Files Modified**:
- `core/models/clp_model.mzn`
- `core/models/clp_model_float.mzn`

**Impact**: Models accept diverse parameter ranges without errors; supports arbitrary problem scales.

### 5. Runner Enhancements

**Features Added**:
- **Automatic precision detection**: Identifies float vs integer DZN format
- **Model auto-selection**: Uses `clp_model_float.mzn` for floats, `clp_model.mzn` for integers
- **Flexible timeout handling**: Supports infinite execution (timeout ≤ 0 or None)
- **Solver CLI parameter**: `--solver` argument (default: `cplex`)
- **Wildcard instance support**: Glob patterns in `--data-dir`

**File**: `scripts/testing/run_battery_project_tests.py`

**Impact**: Transparent model selection; simplified execution for diverse input formats.

### 6. Results Directory Reorganization

**Migration**:
- Runner outputs: `Tests/Output/` → `experiments/results/runner/Run_N/Output/`
- Diagnostics: `Tests/Diagnostics/` → `experiments/results/diagnostics/{battery-type}/{instance}/`
- Error files: Stored as `error.txt` in diagnostic directories

**File**: `core/runner/runner.py`

**Impact**: Cleaner results organization; `Tests/` folder can be deleted from repositories.

## Installation & Setup

See [CONFIG.md](CONFIG.md) for complete step-by-step installation guide.

**Quick Start**:
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch System Center GUI
python core/start.py
```

**Key Dependencies**:
- Python 3.8+
- MiniZinc 2.6+
- PySimpleGUI 4.60+
- pydantic 2.0+

See `requirements.txt` for complete dependency list.

## Project Structure

```
core/
  ├── models/              # MiniZinc models (CLP, RCLP, float variants)
  ├── converter/           # JSON → DZN conversion engine
  ├── generator/           # Instance generation system
  ├── runner/              # Solver execution (CPLEX/Gurobi/etc.)
  ├── orchestration/       # GUI orchestrator (System Center)
  └── shared/              # Navigation, path resolution, theme utilities

experiments/
  ├── instances/           # Test data (Battery-Decided, battery-own, battery-generated)
  └── results/             # Optimization results and diagnostics

scripts/
  ├── solvers/             # Solver availability checking and benchmarking
  ├── testing/             # Integration and regression tests
  ├── verification/        # Converter and model verification
  ├── runner/              # CPLEX execution entry point
  └── debug/               # Investigation and diagnostic utilities

docs/
  ├── installation/        # Solver setup guides (CPLEX, Gurobi, MiniZinc)
  ├── guides/              # User guides and troubleshooting
  ├── architecture/        # Technical architecture documentation
  └── model/               # Mathematical formulation and theory
```

## Testing & Verification

**Regression Tests** (all passing):
- `scripts/testing/test_converter.py` - Converter functional tests
- `scripts/testing/test_converter_integration.py` - Integration tests with JITS2022 data
- `scripts/testing/test_generator.sh` - Generator validation
- `scripts/verification/verify_window_transitions.py` - UI verification
- `scripts/solvers/check_solvers.py` - Solver availability verification

**Example Verification**:
```bash
# Check available solvers
python scripts/solvers/check_solvers.py

# Test converter against JITS2022 baseline
python scripts/verification/test_converter_against_jits2022.py

# Run converter tests
python scripts/testing/test_converter.py
```

## Compatibility

- ✓ **Python**: 3.8, 3.9, 3.10, 3.11
- ✓ **Operating Systems**: Windows, macOS, Linux
- ✓ **MiniZinc**: 2.6+ (tested with 2.7.0)
- ✓ **Solvers**: Chuffed, Gecode, COIN-BC, OR-Tools, CPLEX, Gurobi
- ✓ **Data Formats**: JSON (input), DZN (MiniZinc), CSV (results)

## Known Limitations

1. **RCLP Solver Status**: Robust variant returns `UNKNOWN` on tested instances within 180s. Requires separate robustness parameter tuning and extended solve time.
2. **Commercial Solvers**: CPLEX and Gurobi require separate installation and license management.
3. **Instance Scaling**: Generation limited to patterns for bus fleet sizing; future versions will support arbitrary scale factors.

## Migration Guide (2.0.0 → 2.1.0)

If upgrading from v2.0.0:

1. **Update paths in custom scripts**:
   - `Models/` → `core/models/`
   - `Data/` → `experiments/instances/`
   - `Tests/` → `experiments/results/`
   - `Scripts/` → `scripts/`

2. **Update converter usage**:
   - Normalized mode (default): Uses float energy units
   - Java mode: Integer units matching JITS2022
   - Original mode removed; migrate to normalized or java

3. **Update runner paths**:
   - Results now in `experiments/results/runner/Run_N/Output/`
   - Diagnostics in `experiments/results/diagnostics/`

4. **Reinstall dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## Documentation

- **Getting Started**: [docs/getting-started/GETTING_STARTED.md](docs/getting-started/GETTING_STARTED.md)
- **Installation**: [CONFIG.md](CONFIG.md) & [docs/installation/README.md](docs/installation/README.md)
- **User Guides**: [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md)
- **Architecture**: [docs/architecture/ARCHITECTURE_PATH_RESOLUTION.md](docs/architecture/ARCHITECTURE_PATH_RESOLUTION.md)
- **Model Reference**: [docs/model/PROJECT_SUMMARY.md](docs/model/PROJECT_SUMMARY.md)

## Version History

| Version | Date | Focus |
|---------|------|-------|
| 2.1.0 | May 14, 2026 | Path refactoring, Java compatibility, model fixes |
| 2.0.0 | Apr 20, 2026 | System Center GUI, orchestration, unified versioning |
| 1.5.0 | Apr 16, 2026 | Converter UI improvements, theme enhancements |
| 1.4.0 | Apr 15, 2026 | Multi-solver support, result organization |
| 1.3.0 | Apr 7, 2026 | Modular theme system, UI improvements |

## Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/rclp-optimization-framework/CLP-RCLP_TestLab/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rclp-optimization-framework/CLP-RCLP_TestLab/discussions)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - See [LICENSE](LICENSE) for full text.

---

**Repository**: https://github.com/rclp-optimization-framework/CLP-RCLP_TestLab  
**Branch**: feature/converter-format (merge to main pending)  
**Maintainers**: AVISPA Research Group
