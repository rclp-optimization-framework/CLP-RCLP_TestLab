# CLP-RCLP Version History

## v2.1.0 - Path Refactoring and Java Compatibility (May 2026)

**Release Date**: May 14, 2026

### Major Features
- **Java-Compatible Conversion Mode**: New converter mode emitting integer energy units and seconds-based timing for semantic parity with JITS2022 baseline
- **Complete Path Reorganization**: Modern project structure (core/, experiments/, scripts/) replacing legacy (Models/, Data/, Tests/)
- **Data-Driven Model Bounds**: MiniZinc models now compute bounds from instance data, supporting arbitrary problem scales
- **Automated Model Selection**: Runner auto-detects DZN precision and selects appropriate model variant
- **Enhanced Documentation**: Professional CONFIG.md installation guide, comprehensive SUMMARY.md, updated version references

### Breaking Changes
- `original` (decimal) conversion mode removed; use `normalized` or `java`
- Tests directory (`Tests/`) deprecated; results now in `experiments/results/`
- Hardcoded model bounds replaced with data-dependent computation

### Major Fixes
- **RCLP Temporal Recursion**: Fixed sign bug in `rclp_model_float.mzn` (subtraction → addition)
- **Runner Output Organization**: Results moved from `Tests/Output/` to `experiments/results/runner/Run_N/Output/`
- **Model Precision Handling**: Auto-detect and select correct MiniZinc model based on DZN format

### New/Updated Files
- `requirements.txt` - Python dependencies for reproducible installation
- `CONFIG.md` - Professional step-by-step installation guide
- `SUMMARY.md` - Comprehensive v2.1.0 release summary
- `scripts/runner/README.md` - CPLEX runner documentation
- `scripts/debug/README.md` - Investigation utilities catalog

### Path Migration Map
| Legacy | Modern |
|--------|--------|
| Models/ | core/models/ |
| Converter/ | core/converter/ |
| Generator/ | core/generator/ |
| Runner/ | core/runner/ |
| Data/ | experiments/instances/ |
| Tests/ | experiments/results/ |
| Scripts/ | scripts/ |

### Technical Improvements
- Project root detection via `Path(__file__).resolve().parents[2]`
- Flexible timeout handling in executor (None or ≤0 for infinite)
- DZN precision detection in runner
- Wildcard instance globbing in batch runner
- CPLEX runner with warm-start artifact generation

### Scripts Updated/Created
- **Updated**: 50+ Python scripts, 8 shell scripts
- **Created**: scripts/runner/run_with_cplex.py, scripts/debug/* utilities
- **Validated**: All paths, imports, and execution behavior

### Documentation
- Updated: README.md, CHANGELOG.md, version badges
- Created: CONFIG.md, requirements.txt
- Created: SUMMARY.md (comprehensive release summary)
- Updated: All version references (2.0.0 → 2.1.0)
- Updated: Path examples in all README.md files

### Known Limitations
- RCLP robust variant returns UNKNOWN on tested instances (needs robustness tuning)
- Commercial solvers require separate installation and licensing
- Instance generation limited to predefined patterns

### Commits
- **refactor**: Complete path reorganization across 50+ files
- **feat**: Java conversion mode, auto model selection, flexible timeout
- **fix**: RCLP sign bug, runner output paths, model bounds
- **docs**: Installation guide, version consolidation, migration guide

---

## v2.0.0 - Multi-Tool Framework (April 2026)

**Release Date**: April 20, 2026

### Major Features
- **System Center**: New unified GUI for all tools with dark/light theming
- **Instance Generator**: Complete redesign with Cork variant support
- **Multi-Solver Support**: Integrated Chuffed, Gecode, COIN-BC, OR-Tools, CPLEX, Gurobi
- **Professional Architecture**: Modular core framework with separation of concerns
- **Enhanced Documentation**: Comprehensive guides, installation instructions, troubleshooting

### Breaking Changes
- Project directory structure reorganized (Converter → core/converter, etc.)
- Entry points moved to core/ directory (start.py, start.sh)
- Configuration format updated in runner and generator

### New Modules
- `core/orchestration/` - System Center GUI and orchestration
- `core/shared/` - Common utilities and navigation
- `core/models/` - Unified MiniZinc model directory

### Technical Improvements
- Coherent energy/time scaling strategy
- Corrected Big-M constant calculation
- Improved error handling and validation
- Better import path handling with fallbacks
- Professional Tkinter UI with theme support

### Fixed Issues
- Model-Converter scale misalignment (v1.4.0 → v2.0.0)
- Tau_bi time variable overflow errors
- Import path issues in multi-module system
- Window sizing for improved UX

### Documentation
- New: GETTING_STARTED.md (user onboarding)
- New: PROJECT_OVERVIEW.md (architecture and features)
- New: VERSION_HISTORY.md (this file)
- Updated: All installation guides in English
- Removed: Obsolete development reports
- Simplified: docs/ structure for clarity

### Commits
- **feat**: Multiple feature commits including GUI, multi-solver, generator
- **fix**: Scaling strategy, import paths, model domains
- **refactor**: Complete project structure reorganization
- **docs**: Comprehensive documentation updates

---

## v1.4.0 - Multi-Solver Architecture (April 2026)

**Release Date**: April 15, 2026

### Features
- Integrated 6 solvers (Chuffed, Gecode, COIN-BC, OR-Tools, CPLEX, Gurobi)
- Solver management and abstraction layer
- Result aggregation across solvers
- HTML report generation
- Parallel solver execution

### Technical Details
- Solver detection and validation
- Timeout handling per solver
- Resource management (memory, CPU)
- Result normalization and comparison

### Known Issues
- Scale mismatch between model (SCALE_ENERGY=50) and converter (SCALE_ENERGY=1000)
- Tau_bi values exceeding variable bounds in some instances

### Documentation
- ARCHITECTURE_v1_4_0.md - Technical architecture
- Solver installation guides (CPLEX, Gurobi, MiniZinc)
- Multi-solver troubleshooting guide

---

## v1.3.0 - Converter Refinement (March 2026)

**Release Date**: March 26, 2026

### Features
- Improved JSON to DZN converter with validation
- Cork instance variant generation
- Battery project data standardization
- Energy parameter scaling

### Improvements
- Better error messages
- Input validation framework
- Test coverage expansion
- Performance optimization

### Fixes
- st_bi indexing corrections
- Data validation enhancements
- Path handling improvements

---

## v1.2.0 - Initial Multi-Tool Release (March 2026)

**Release Date**: March 20, 2026

### Features
- Data Converter tool (JSON → DZN)
- Instance Generator tool
- Test Runner tool
- Command-line interfaces for all tools
- Basic configuration system

### Modules
- Converter: JSON to MiniZinc format conversion
- Generator: Synthetic instance generation
- Runner: Optimization execution and result collection
- Models: MiniZinc CLP and RCLP formulations

### Technical Details
- Python 3.8+ compatibility
- MiniZinc 2.6+ integration
- Configuration-based parameter management
- Result output to files and console

### Documentation
- Tool usage guides
- Mathematical model documentation (MathModel.tex)
- Installation instructions
- Basic troubleshooting

---

## v1.1.0 - Single-Tool Release (March 2026)

**Release Date**: March 10, 2026

### Features
- Initial Data Converter implementation
- MiniZinc model integration
- Basic instance data support
- Command-line execution

### Limitations
- Single tool only
- Limited solver support
- Minimal error handling
- Basic documentation

---

## v1.0.0 - Alpha Release (February 2026)

**Release Date**: February 28, 2026

### Initial Features
- Basic project structure
- Converter framework foundation
- MiniZinc model templates
- Minimal documentation

### Status
- Alpha/prototype phase
- Limited testing
- Core functionality present but unrefined

---

## Version Comparison

| Feature | v1.0 | v1.2 | v1.4 | v2.0 |
|---------|------|------|------|------|
| Converter | ✓ | ✓ | ✓ | ✓ |
| Generator | ✗ | ✓ | ✓ | ✓ |
| Runner | ✗ | ✓ | ✓ | ✓ |
| Multi-Solver | ✗ | ✗ | ✓ | ✓ |
| GUI (System Center) | ✗ | ✗ | ✗ | ✓ |
| Theme Support | ✗ | ✗ | ✗ | ✓ |
| Cork Variants | ✗ | ✗ | ✓ | ✓ |
| Professional Docs | ✗ | Partial | ✓ | ✓ |

## Breaking Changes by Version

### v1.2.0 → v1.3.0
- Configuration format updates
- Parameter naming conventions

### v1.3.0 → v1.4.0
- Solver integration layer (minor)
- Result output format changes

### v1.4.0 → v2.0.0 (Major)
- **Directory structure**: Complete reorganization
- **Import paths**: All relative paths updated
- **Entry points**: Moved to core/ directory
- **Configuration**: Format and location changes
- **API changes**: Minor updates to runner and generator interfaces
- **UI migration**: Command-line → GUI + command-line

## Migration Guide (v1.4.0 → v2.0.0)

### Path Updates
```
Old: python Converter/converter.py
New: python core/converter/converter.py
     or: cd core && python converter/converter.py

Old: python Generator/generator.py
New: python core/generator/generator.py
     or: cd core && python generator/generator.py

Old: python Runner/runner.py
New: python core/runner/runner.py
     or: cd core && python runner/runner.py
```

### GUI Access
```
New: python core/start.py
     or: cd core && python start.py
     or: cd core && bash start.sh
```

### Data Directories
```
Old: Data/battery-project
New: experiments/instances/battery-project

Old: Tests/Diagnostics
New: experiments/results/Diagnostics
```

### Configuration
Check individual tool config files:
- `core/converter/config.py`
- `core/generator/config.py`
- `core/runner/config.py`

## Future Roadmap

### v2.1 (Planned)
- Real-time performance dashboard
- Advanced visualization of solutions
- Instance classification using ML
- API for programmatic access

### v2.2 (Planned)
- Distributed solving across machines
- Cloud integration support
- Database backend for large-scale experiments
- Advanced filtering and searching of results

### v3.0 (Long-term)
- Graphical instance editor
- Custom constraint support
- Plugin architecture for solvers
- Web-based interface

## Support & Deprecation

**Current Version**: v2.0.0 (Active)
- Full support
- Regular updates
- Active maintenance

**Previous Versions**: v1.4.0 and earlier
- Limited support
- Security updates only
- Upgrade recommended

**Deprecated**: Versions before v1.2.0
- No longer supported
- Archive purposes only

## Feedback & Contributions

For feedback on versions, requested features, or bugs:
1. GitHub Issues: Report bugs and request features
2. GitHub Discussions: General feedback and ideas
3. Pull Requests: Contribute improvements

See main README.md for detailed contribution guidelines.
