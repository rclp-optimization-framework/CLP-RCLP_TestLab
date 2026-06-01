# Core Module Architecture Map

Complete architectural overview of the CLP-RCLP framework's core modules.

## Directory Structure

```
core/
├── __init__.py                          # Package initialization
├── start.py                             # Main entry point (launcher)
├── converter/                           # JITS2022 → MiniZinc format conversion
│   ├── config.py                        # Configuration for converter
│   ├── converter.py                     # Entry point
│   ├── core/
│   │   ├── converter_engine.py          # Core conversion algorithm
│   │   ├── data_loader.py               # JITS2022 data loading
│   │   ├── experiment_config.py         # Experiment configuration
│   │   └── file_manager.py              # File I/O operations
│   └── ui/                              # Tkinter GUI
│       ├── components.py                # Reusable UI components
│       ├── help_window.py               # Help dialog
│       ├── interface.py                 # Main window
│       ├── themes.py                    # Color schemes
│       └── tooltip.py                   # Tooltip widget
├── generator/                           # Instance generation from configurations
│   ├── config.py                        # Generator configuration
│   ├── generator.py                     # Entry point
│   ├── orchestrator.py                  # Generator orchestration
│   ├── test_generator.py                # Test generation logic
│   ├── core/
│   │   ├── instance_generator.py        # Instance creation
│   │   ├── instance_manager.py          # Instance lifecycle
│   │   ├── instance_validator.py        # Validation logic
│   │   └── minizinc_exporter.py         # .dzn file export
│   └── ui/                              # Tkinter GUI
│       ├── components.py                # UI components
│       ├── interface.py                 # Main window
│       ├── layouts.py                   # Layout builder
│       ├── themes.py                    # Themes
│       └── tooltip.py                   # Tooltips
├── orchestration/                       # System orchestrator (tool launcher)
│   ├── config.py                        # Orchestrator configuration
│   ├── orchestrator.py                  # Main orchestrator logic
│   ├── README.md                        # Orchestrator documentation
│   └── ui/                              # Tkinter GUI
│       ├── components.py                # UI components
│       ├── help_window.py               # Help dialog
│       ├── interface.py                 # Main window
│       ├── layouts.py                   # Layout builder
│       ├── themes.py                    # Themes
│       └── tooltip.py                   # Tooltips
├── runner/                              # Test execution engine
│   ├── config.py                        # Runner configuration
│   ├── runner.py                        # Entry point
│   ├── core/
│   │   ├── executor.py                  # MiniZinc subprocess wrapper
│   │   ├── result_handler.py            # Result file I/O
│   │   └── solvers.py                   # Solver management
│   └── ui/                              # Tkinter GUI
│       ├── components.py                # UI components
│       ├── interface.py                 # Main window (v2.2.0+: batch/subdir)
│       ├── layouts.py                   # Layout builder
│       ├── themes.py                    # Themes
│       └── tooltip.py                   # Tooltips
├── models/                              # MiniZinc model files
│   ├── clp_model.mzn                    # CLP integer model
│   ├── clp_model_float.mzn              # CLP floating-point model
│   ├── rclp_model.mzn                   # RCLP integer model
│   └── rclp_model_float.mzn             # RCLP floating-point model
└── shared/                              # Shared utilities
    ├── __init__.py                      # Package init
    ├── navigation.py                    # Inter-module navigation
    ├── path_resolver.py                 # Dynamic tool discovery
    ├── project_paths.py                 # Centralized path management
    └── theme_persistence.py             # Cross-session theme storage
```

## Module Descriptions

### `core.converter` - JITS2022 Format Conversion

**Purpose:** Transform JITS2022 benchmark data into MiniZinc .dzn format.

**Key Classes:**
- `ConverterEngine`: Main conversion algorithm, data transformation logic
- `DataLoader`: Loads JITS2022 XML/data files
- `ExperimentConfig`: Defines experiment parameters and boundaries
- `FileManager`: Handles file I/O and directory operations

**Integration:**
- Input: `external/jits2022/Code/data/` (JITS2022 benchmark)
- Output: `experiments/instances/battery-original/` (.dzn files)
- UI: Tkinter interface with progress tracking and configuration

**Key Files:**
- `core/converter/core/converter_engine.py`: Core algorithm
- `core/converter/ui/interface.py`: GUI

**v2.2.0 Status:** No changes in this module.

---

### `core.generator` - Instance Generation

**Purpose:** Generate diverse test instances from configuration templates.

**Key Classes:**
- `InstanceGenerator`: Creates instances from templates
- `InstanceManager`: Manages instance lifecycle and metadata
- `InstanceValidator`: Validates generated instances against constraints
- `MiniZincExporter`: Exports instances as .dzn files

**Integration:**
- Input: Configuration parameters (bus count, station count, constraints)
- Output: `experiments/instances/battery-generated/` (.dzn files)
- UI: Configuration UI with generation progress

**Key Files:**
- `core/generator/core/instance_generator.py`: Generation logic
- `core/generator/ui/interface.py`: GUI

**v2.2.0 Status:** No changes in this module.

---

### `core.runner` - Test Execution Engine

**Purpose:** Execute MiniZinc models with multiple solvers and manage results.

**Key Classes:**
- `MiniZincExecutor`: Subprocess wrapper, execution control (v2.2.0: Popen-based)
- `ResultHandler`: Result file I/O, storage organization (v2.2.0: model-aware)
- `SolverManager`: Solver registration, configuration
- `RunnerInterface`: Main UI (v2.2.0: batch execution, subdirectory nav)

**Integration:**
- Input: Test instances (.dzn), model files (.mzn)
- Output: `experiments/results/output/` (results) and `Diagnostics/` (errors)
- Solvers: Chuffed, Gecode, COIN-BC, OR-Tools, CPLEX, Gurobi

**Key Files:**
- `core/runner/core/executor.py`: Execution engine (v2.2.0 enhanced)
- `core/runner/core/result_handler.py`: Result management (v2.2.0 enhanced)
- `core/runner/ui/interface.py`: GUI (v2.2.0 major enhancements)

**v2.2.0 Enhancements:**
- Proper subprocess termination (stop button fix)
- Model-aware result storage (float/integer)
- Batch execution (single/all/continue modes)
- Subdirectory battery navigation
- Charged station indices

---

### `core.orchestration` - System Orchestrator

**Purpose:** Provide unified entry point, launch other tools, manage transitions.

**Key Classes:**
- `Orchestrator`: Main orchestration logic, tool launching
- `OrchestratorInterface`: GUI for tool selection and launching

**Integration:**
- Input: User selections (which tool to launch)
- Output: Launches tool subprocesses (converter, generator, runner)
- State: Tracks which tools are running

**Key Files:**
- `core/orchestration/orchestrator.py`: Orchestrator logic
- `core/orchestration/ui/interface.py`: GUI

**v2.2.0 Status:** No changes in this module.

---

### `core.models` - MiniZinc Model Files

**Purpose:** Store the mathematical models used for optimization.

**Files:**
- `clp_model.mzn`: CLP with integer variables (scaling factor = 10)
- `clp_model_float.mzn`: CLP with floating-point variables
- `rclp_model.mzn`: RCLP with integer variables (scaling factor = 10)
- `rclp_model_float.mzn`: RCLP with floating-point variables

**Integration:**
- Used by: `runner.executor` for model resolution
- Path resolution: `ProjectPaths.clp_model_path(precision)`
- Precision affects: Time deviation normalization in results

**v2.2.0 Impact:** Model-aware storage now distinguishes between model precisions (float vs integer).

---

### `core.shared` - Shared Utilities

**Purpose:** Provide cross-module utilities and configuration.

#### `path_resolver.py`

**Class:** `ToolPathResolver`

**Purpose:** Dynamically locate tool scripts (converter, generator, runner) regardless of directory structure.

**Key Methods:**
- `get_tool_path(tool_name)`: Returns path to tool script
- `validate_tools()`: Checks all tools are available

**Handles:** Case-insensitive directory names, legacy structures, nested modules.

---

#### `project_paths.py`

**Class:** `ProjectPaths` (static utility)

**Purpose:** Centralized path management for all project directories.

**Key Methods:**
- `get_project_root()`: Auto-detects project root
- `instances_dir()`: Test instances directory
- `results_dir()`: Results output directory
- `clp_model_path(precision)`: Get CLP model file
- `rclp_model_path(precision)`: Get RCLP model file

**Auto-detection:** Searches upward for directory containing `core/` and `experiments/`.

**v2.2.0 Impact:** Used throughout runner for model resolution and result directory construction.

---

#### `navigation.py`

**Functions:**
- `return_to_orchestrator(window)`: Close current tool, launch orchestrator

**Purpose:** Enable seamless navigation between tools.

---

#### `theme_persistence.py`

**Class:** `ThemePersistence` (static utility)

**Purpose:** Store and restore theme (dark/light mode) across sessions.

**Key Methods:**
- `get_theme()`: Returns saved theme or "dark" default
- `set_theme(theme)`: Save theme preference

**Storage:** `.theme_config.json` at project root.

---

## Data Flow Diagrams

### Converter Pipeline

```
JITS2022 Data
    ↓
DataLoader
    ↓
ConverterEngine (transformation algorithm)
    ↓
ExperimentConfig (parameters)
    ↓
FileManager (write .dzn)
    ↓
battery-original/instance.dzn
```

### Generator Pipeline

```
Config (instance parameters)
    ↓
InstanceGenerator (create)
    ↓
InstanceValidator (verify)
    ↓
MiniZincExporter (serialize)
    ↓
battery-generated/instance.dzn
```

### Runner Pipeline (v2.2.0)

```
UI Selection (battery, instance, model, solver, mode)
    ↓
Battery/Subdirectory Discovery
    ↓
Instance List Population
    ↓
Execution Mode Dispatch
    ├─ Single: Execute one instance
    ├─ All: Execute all, save one-by-one
    └─ Continue: Resume from index
    ↓
MiniZincExecutor (Popen-based, v2.2.0)
    ↓
ResultHandler (model-aware storage, v2.2.0)
    ├─ Success: Save results
    ├─ UNSAT: Save diagnostic
    └─ Error: Save diagnostic + break
    ↓
results/output/{battery}/{model_type}/{subdir}/{instance}/{solver}/
results/diagnostics/{model_type}/{solver}/
```

## Dependency Graph

```
orchestration/
    ↓ launches
converter/, generator/, runner/
    ↓ use
runner/core/executor.py
    ↓ uses
    └─ runner/core/solvers.py
    └─ shared/project_paths.py
runner/core/result_handler.py
    ↓ uses
    └─ shared/project_paths.py
shared/theme_persistence.py [independent]
shared/navigation.py
    ↓ launches
    └─ orchestration/
```

## Key Architectural Patterns

### 1. Module Isolation

Each major module (converter, generator, runner, orchestration) is self-contained:
- Own `core/` subdirectory for business logic
- Own `ui/` subdirectory for GUI
- Own `config.py` for configuration
- Minimal cross-module dependencies

### 2. Separation of Concerns

- **UI Layer** (`ui/interface.py`): User interactions, display
- **Core Layer** (`core/*.py`): Algorithms, business logic
- **Shared Layer** (`shared/`): Common utilities

### 3. Path Centralization

All path operations go through `ProjectPaths`. This ensures:
- Single source of truth for directory layout
- Cross-platform compatibility (Windows/Mac/Linux)
- Easy reconfiguration if directory structure changes

### 4. Theme Persistence

Theme preference (dark/light) is persistent across all tools via `ThemePersistence`.

### 5. Dynamic Discovery

`ToolPathResolver` and `path_resolver.py` provide dynamic tool discovery, enabling:
- Flexible directory structures
- Legacy naming support
- Easy testing with temporary structures

## Configuration Management

Each module has `config.py`:
- `core/converter/config.py`: Converter settings
- `core/generator/config.py`: Generator settings
- `core/runner/config.py`: Runner settings
- `core/orchestration/config.py`: Orchestrator settings

Centralized configuration enables:
- Easy testing with different parameters
- Consistent defaults across module launches
- Environment-specific overrides

## Testing Considerations

### Unit Test Targets

- `executor.py`: Subprocess management, termination
- `result_handler.py`: Result file writing, directory creation
- `path_resolver.py`: Tool discovery edge cases
- `project_paths.py`: Path construction correctness

### Integration Test Targets

- End-to-end converter: JITS2022 → .dzn
- End-to-end generator: Config → .dzn
- End-to-end runner: Instance → Results
- Cross-module navigation: Orchestrator → Tools → Orchestrator

### Performance Test Targets

- Batch execution with 100+ instances
- Result writing throughput
- Memory usage during batch processing

## Future Expansion Points

1. **Plugin System**: Allow custom solvers via plugin interface
2. **Remote Execution**: SSH/API-based execution on remote clusters
3. **Result Database**: PostgreSQL backend for result storage instead of JSON
4. **Web Dashboard**: HTML/JavaScript frontend for result visualization
5. **Parallel Execution**: ThreadPool/ProcessPool for concurrent instances
