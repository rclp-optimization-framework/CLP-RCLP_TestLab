# Verification Scripts

Automated verification and testing scripts for the CLP-RCLP framework.

## Scripts

### verify_original_decimal_converter.py

**Purpose**: Verifies that the converter can emit the original decimal DZN format without rounding the source values.

**What it tests**:

- ✓ Station mapping remains stable
- ✓ Travel times match the source JSON schedules
- ✓ Energy values keep the original decimal distance precision
- ✓ The generated DZN includes the original decimal format marker

**Usage**:

```bash
# From project root
python scripts/verification/verify_original_decimal_converter.py external/jits2022/Code/data/cork-1-line
```

**Exit Codes**:

- `0`: Original decimal mode verified successfully ✓
- `1`: Verification failed ✗

**Notes**:

- The script generates temporary DZN files and cleans them up automatically
- It is intended for the new original decimal conversion mode exposed in the converter UI

### verify_window_transitions.py

**Purpose**: Verifies window transition functionality between Orchestrator and Tool windows.

**What it tests**:

- ✓ ToolPathResolver can locate all tool scripts (Converter, Generator, Runner)
- ✓ Navigation paths are correctly configured
- ✓ Back button functionality works across all tools
- ✓ Orchestrator theme switching support is enabled

**Usage**:

```bash
# From project root
python scripts/verification/verify_window_transitions.py

# With explicit project root
python scripts/verification/verify_window_transitions.py --project-root /path/to/CLP-RCLP_Minizinc_Lab_Enviroment
```

**Exit Codes**:

- `0`: All transitions verified successfully ✓
- `1`: One or more transitions failed ✗
- `2`: Configuration error (missing tools, etc.)

**Example Output**:

```
============================================================================
CLP-RCLP WINDOW TRANSITION VERIFICATION REPORT
============================================================================

[1] ToolPathResolver Verification
--------------------------------------------------------------------------
✓ ToolPathResolver imported successfully
  converter: ✓ FOUND (/path/to/core/converter/converter.py)
  generator: ✓ FOUND (/path/to/core/generator/generator.py)
  runner: ✓ FOUND (/path/to/core/runner/runner.py)

[2] Navigation Path Verification
--------------------------------------------------------------------------
Orchestrator path: ✓ FOUND (/path/to/core/orchestration/orchestrator.py)
Navigation module: ✓ FOUND (/path/to/core/shared/navigation.py)
Path resolver: ✓ FOUND (/path/to/core/shared/path_resolver.py)

[3] Orchestrator Theme Support Verification
--------------------------------------------------------------------------
Theme components: _toggle_theme✓, ThemeManager✓, FlatButton✓, theme_dict✓

============================================================================
SUMMARY
============================================================================
Overall Status: ✓ PASS
  Tool Resolution: ✓
  Navigation Paths: ✓
  Theme Support: ✓

Details:
  Available Tools: 3/3
  Navigation Checks: 3/3
============================================================================
```

## How It Works

### Phase 1: ToolPathResolver Verification

The script imports `ToolPathResolver` and tests its ability to locate all three tool scripts:

- Converter (`core/converter/converter.py`)
- Generator (`core/generator/generator.py`)
- Runner (`core/runner/runner.py`)

This ensures the dynamic path resolution system works correctly regardless of directory structure or naming conventions.

### Phase 2: Navigation Path Verification

Verifies that critical navigation components exist:

- Orchestrator entry point (`core/orchestration/orchestrator.py`)
- Navigation utility module (`core/shared/navigation.py`)
- Path resolver module (`core/shared/path_resolver.py`)

### Phase 3: Orchestrator Theme Support

Checks that the Orchestrator interface includes all required theme-switching components:

- `_toggle_theme()` method
- `ThemeManager` integration
- `FlatButton` component for theme toggle
- `theme_dict` theme dictionary

## Troubleshooting

### "ToolPathResolver imported successfully" but tools not found

**Problem**: The path resolver can't locate tool scripts.

**Solutions**:

1. Verify directory structure:

   ```
   core/
   ├── converter/
   │   └── converter.py
   ├── generator/
   │   └── generator.py
   ├── runner/
   │   └── runner.py
   ├── orchestration/
   │   └── orchestrator.py
   └── shared/
       ├── path_resolver.py
       └── navigation.py
   ```

2. Check that tool scripts aren't in unexpected locations
3. Ensure file names match exactly (case-sensitive on Unix systems)

### "Navigation module: ✗ NOT FOUND"

The `navigation.py` file may be missing. Ensure it exists at `core/shared/navigation.py` and contains the updated path resolution code.

### "Theme Support: ✗"

The Orchestrator interface may not have theme switching properly integrated. Check `core/orchestration/ui/interface.py` for:

- Proper `ThemeManager` import
- `_toggle_theme()` method implementation
- Theme toggle button in header

## Running via GUI

You can also test transitions manually:

1. **Launch Orchestrator**:

   ```bash
   python core/orchestration/orchestrator.py
   ```

2. **Launch any tool** from the Orchestrator interface using the "Launch" buttons

3. **Test back navigation** by clicking the back button (`<`) in the tool header

4. **Test theme switching** in both Orchestrator and Tool windows using the theme toggle button (☀ Light / 🌙 Dark)

## Integration with CI/CD

This script can be integrated into your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Verify Window Transitions
  run: python scripts/verification/verify_window_transitions.py
```

## Notes

- The script automatically detects the project root
- It respects the current working directory but can work from any location
- All paths are cross-platform compatible (Windows, macOS, Linux)
- Detailed logging is provided for debugging

## Author

AVISPA Research Team
April 2026
