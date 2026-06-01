# v2.2.0 Changelog - Runner Pro

**Release Date:** May 31, 2026

## Overview

Version 2.2.0 introduces significant enhancements to the test runner, focusing on execution control, result organization, batch processing, and comprehensive documentation. These improvements address key limitations in v2.1.0 while maintaining backward compatibility.

## Major Features

### 1. Fixed Stop Button with Subprocess Termination

**Issue:** The stop button in v2.1.0 was non-functional. While the UI flag was set, the underlying MiniZinc subprocess continued running indefinitely.

**Solution:** Implemented proper subprocess management with thread-safe termination:
- Migrated from `subprocess.run()` to `subprocess.Popen()` for direct process control
- Added `threading.Event()` for clean shutdown coordination
- Implemented graceful termination: SIGTERM → 2-second wait → SIGKILL if needed
- Added executor reference tracking in UI thread

**Impact:** Users can now reliably stop long-running executions within 2 seconds of pressing the stop button.

### 2. Model-Aware Result Storage

**Issue:** Results were stored as `battery/instance/solver/`, not reflecting whether integer or floating-point models were used.

**Solution:** Reorganized result storage structure:
- New format: `battery/model_type/instance/solver/`
- Model type values: `float` or `integer`
- Automatic subdirectory creation when needed
- Backward compatible: old results remain accessible

**Example:**
```
experiments/results/output/
├── Battery-Decided/
│   ├── float/
│   │   └── cork-1-line_Battery-Decided20_0/
│   │       └── CPLEX/
│   │           ├── cork-1-line_Battery-Decided20_0_result.json
│   │           └── cork-1-line_Battery-Decided20_0_result.txt
│   └── integer/
│       └── cork-1-line_Battery-Decided20_0/
```

**Impact:** Clear organization enables comparative analysis between model precisions.

### 3. Charged Station Indices in Results

**Issue:** Results showed charged stations as a binary array `[0,1,0,0,1]` but not their actual indices `[1,4]`.

**Solution:** Added `charged_index` field to all results:

**JSON Format:**
```json
{
  "charged_stations": 2,
  "charging_locations": [0, 1, 0, 0, 1],
  "charged_index": [1, 4]
}
```

**TXT Format:**
```
Charged Stations:       2
Charging Locations:     [0,1,0,0,1]
Charged Index:          [1,4]
```

**Impact:** Eliminates manual index calculation; improves result interpretability.

### 4. Subdirectory Battery Navigation

**Issue:** Batteries with nested structures (e.g., Battery-Decided with cork-1-line/, cork-2-line/ subdirectories) were not discoverable.

**Solution:** Added UI controls for battery subdirectory navigation:
- New "Subdirectory" dropdown automatically populated from battery structure
- Shows "Root" for battery root instances or detected subdirectories
- Instance list automatically updates based on selected subdirectory
- Results mirror subdirectory hierarchy: `battery/model_type/subdir/instance/solver/`

**Impact:** Enables execution from deeply nested battery structures without flattening.

### 5. Batch Execution with Resume Capability

**Issue:** Only single-instance execution was supported. Running 100 instances required 100 manual clicks.

**Solution:** Implemented comprehensive batch execution:

**Execution Modes:**
- **Single**: Run one instance (original behavior)
- **All**: Run all instances in selected battery/subdirectory sequentially
- **Continue**: Resume from specific instance after interruption

**Features:**
- Real-time progress logging: `[5/20] Executing instance_name...`
- Results saved one-by-one as executions complete
- Automatic error diagnostics on failure
- Batch stops gracefully on first failure, allowing resume
- Full state tracking for partial batch recovery

**Batch Execution Flow:**
```
Idle
  ↓
Running All/Continue
  ↓
  For each instance:
    → Execute → Success → Save → Continue
    → Execute → UNSAT → Save Diagnostic → Continue
    → Execute → Failed → Save Diagnostic → Stop
  ↓
Batch Complete/Stopped
  ↓
Idle
```

**Impact:** Reduces manual test execution from hours to minutes.

### 6. Core Module Documentation

**Scope:** Audited and documented all modules in `core/` with professional English docstrings.

**Modules Enhanced:**
- `core/__init__.py`: High-level package overview
- `core/shared/theme_persistence.py`: Cross-session theme management
- `core/shared/navigation.py`: Already well-documented
- `core/shared/path_resolver.py`: Already well-documented
- `core/shared/project_paths.py`: Already well-documented
- All runner, generator, converter, orchestration modules reviewed

**Standards Applied:**
- Module-level docstrings with purpose and key classes
- Class docstrings explaining responsibility and architecture
- Function/method docstrings with Args, Returns, and Notes sections
- Type hints throughout
- Integration point documentation

**Impact:** Improved code maintainability and onboarding for new developers.

## Technical Details

### Subprocess Termination Architecture

The stop button fix uses a multi-layer approach:

1. **Thread-level signal**: `threading.Event()` set by UI
2. **Process-level control**: `subprocess.Popen()` reference stored in executor
3. **Escalating termination**: SIGTERM → wait 2s → SIGKILL
4. **State cleanup**: Flags and executor references cleared

### Result Storage Migration

No action required for end users. New executions automatically use the new structure. Existing results remain readable.

### Batch Execution State Machine

Implemented as a sequential for-loop with:
- Per-iteration stop event check
- Per-instance exception handling
- Cumulative result accumulation
- Final summary reporting

## Breaking Changes

**None.** Version 2.2.0 is fully backward compatible with v2.1.0:
- Old result directory structures still readable
- Single-mode execution unchanged
- All solver selections preserved
- UI themes maintained

## Dependencies

- **Python**: 3.8+ (unchanged)
- **MiniZinc**: Current version (unchanged)
- **Tkinter**: Standard library (unchanged)

## Files Modified

1. `core/runner/core/executor.py`: Popen + terminate()
2. `core/runner/core/result_handler.py`: Model-aware storage
3. `core/runner/ui/interface.py`: Stop button, batch UI, subdirectory nav
4. `core/shared/theme_persistence.py`: Documentation
5. `core/__init__.py`: Documentation

## Files Created

1. `docs/v2.2.0/CHANGELOG.md`
2. `docs/v2.2.0/IMPLEMENTATION.md`
3. `docs/v2.2.0/CORE_MAP.md`
4. `docs/v2.2.0/MIGRATION_GUIDE.md`

## Testing Coverage

All new features verified:
- ✓ Stop button terminates subprocess within 2 seconds
- ✓ Results stored in float/integer subdirectories
- ✓ Charged index calculated correctly
- ✓ Subdirectory batteries navigate properly
- ✓ Batch execution completes all instances
- ✓ Continue-from resumes at correct index
- ✓ No regressions in single-mode execution

## Known Limitations

1. **Batch execution**: Currently sequential (not parallel). Future versions may add parallel execution with thread pools.
2. **Subdirectories**: Supports 1 level of nesting (Battery/Subdir/instances). Deeper structures not tested.
3. **Resume capability**: Uses instance index, not instance name. Renamed instances require manual index adjustment.

## Future Roadmap

- **v2.3.0**: Parallel batch execution
- **v2.4.0**: Advanced filtering (by solver, model type, result status)
- **v2.5.0**: Web dashboard for result visualization

## Upgrade Instructions

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed instructions on using new features.

## Contributors

- Andrey Quiceno (AVISPA Team)
- Juan Francesco García (AVISPA Team)

## License

See LICENSE file at project root.
