# CLP-RCLP TestLab Environment

[![Version](https://img.shields.io/badge/version-2.1.0-brightgreen?style=flat-square)](.)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](.)
[![Python](https://img.shields.io/badge/python-3.8+-yellow?style=flat-square)](.)
[![MiniZinc](https://img.shields.io/badge/minizinc-2.6+-ff69b4?style=flat-square)](.)

## Overview

Professional lab environment for research and optimization of the **Charging Location Problem (CLP)** and its robust extension **(RCLP)** for electric bus fleets using constraint programming.

This framework provides a complete toolkit for:

- **System Center**: Unified GUI for accessing all tools (v2.1.0)
- **Mathematical Models**: CLP and RCLP formulations in MiniZinc
- **Instance Generation**: Create synthetic and realistic test datasets
- **Data Conversion**: Transform JSON to constraint programming format
- **Optimization Testing**: Execute and compare multiple solvers
- **Multi-Solver Support**: Chuffed, Gecode, COIN-BC, OR-Tools, CPLEX, Gurobi
- **Complete Documentation**: Comprehensive guides and technical references

## Key Features

### 🎯 System Center GUI (v2.1.0)

- Unified interface to all tools
- Dark/Light theme with persistent preferences
- Professional design with 2x2 grid layout
- One-click tool launching
- Direct access to documentation and GitHub
- Resizable window with responsive layout

### 🔧 Three Core Tools

1. **Data Converter** - JSON to MiniZinc (DZN) format, with normalized and Java-compatible output modes
2. **Instance Generator** - Create test instances with parameters
3. **Test Runner** - Execute optimization and compare solvers

### 📊 Mathematical Models

- **CLP**: Optimal charging station location
- **RCLP**: Robust variant with failure resilience
- MiniZinc format for multiple solvers

### 🎲 Instance Generation

- Working Pattern Replication
- 5 Route Patterns (Sequential, Reverse, Alternate, Diagonal)
- Smart parameter generation
- Guaranteed satisfiable instances

### ⚡ Multi-Solver Optimization

- 6+ constraint solvers (open-source and commercial)
- Parallel solver execution
- Result aggregation and comparison
- Performance metrics and analysis

### 📚 Complete Documentation

- Getting started guide
- User guides for each tool
- API reference documentation
- Mathematical formulation (LaTeX)
- Troubleshooting guide
- Installation instructions

## Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# MiniZinc 2.6 or higher
minizinc --version

# Download MiniZinc from https://www.minizinc.org/
```

### Installation

```bash
# Clone repository
git clone https://github.com/AndreyQuicenoC/CLP-RCLP_Minizinc_Lab_Enviroment.git
cd "CLP-RCLP_Minizinc_Lab_Enviroment"

# Install MiniZinc (if not already installed)
# See docs/getting-started/GETTING_STARTED.md for detailed instructions
```

### Launch System Center

```bash
# Recommended: Use System Center GUI
python core/start.py

# Or from core directory:
cd core
python start.py
# Or on Unix/Linux:
bash start.sh
```

### Direct Tool Access

```bash
cd core

# Generate instances
python generator/generator.py

# Convert data to DZN format
python converter/converter.py

# Run optimization tests
python runner/runner.py
```

## Project Structure

```
CLP-RCLP_Minizinc_Lab_Enviroment/
│
├── core/                          # Application modules
│   ├── start.py                  # System Center entry point
│   ├── start.sh                  # Bash launcher
│   ├── orchestration/            # System Center GUI
│   ├── converter/                # JSON to DZN conversion
│   ├── generator/                # Instance generation
│   ├── runner/                   # Optimization execution
│   ├── models/                   # MiniZinc models
│   ├── shared/                   # Common utilities
│   └── README.md                 # Core module documentation
│
├── experiments/                   # Experimental data
│   ├── instances/                # Test datasets
│   │   ├── battery-project-integer/
│   │   ├── battery-project-variant/
│   │   ├── battery-generated/
│   │   └── battery-own/
│   └── results/                  # Solver results and diagnostics
│       ├── runner/               # Runner outputs: Run_N/Output/
│       └── diagnostics/          # Diagnostics organized by battery-type/instance
│
├── scripts/                       # Utility scripts
│   ├── data-processing/          # Data utilities
│   ├── generation/               # Instance generation
│   ├── setup/                    # Environment setup
│   ├── solvers/                  # Solver management
│   ├── testing/                  # Test suites
│   ├── ui-testing/               # UI testing
│   ├── utilities/                # Diagnostic tools
│   ├── verification/             # Validation tools
│   └── README.md                 # Scripts documentation
│
├── docs/                          # Documentation
│   ├── getting-started/          # Installation and quick start
│   ├── overview/                 # Project information
│   ├── reference/                # Complete reference
│   ├── guides/                   # User guides
│   ├── installation/             # Solver installation
│   ├── model/                    # Mathematical documentation
│   └── README.md                 # Documentation index
│
├── external/                      # External dependencies
│   └── jits2022/                 # JITS2022 reference data
│
├── README.md                      # This file
├── LICENSE                        # MIT License
├── CHANGELOG.md                   # Change history
├── CONTRIBUTING.md                # Contribution guidelines
└── .gitignore                     # Git configuration
```

## Technology Stack

- **Language**: Python 3.8+
- **Constraint Programming**: MiniZinc 2.6+
- **UI Framework**: Tkinter (Python built-in)
- **Solvers**:
  - Open-source: Chuffed, Gecode, COIN-BC, OR-Tools
  - Commercial: CPLEX, Gurobi
- **Testing**: pytest, shell scripts
- **Version Control**: Git

## Documentation

Complete documentation is available in the `docs/` directory:

- **[Getting Started](docs/getting-started/GETTING_STARTED.md)** - Installation and first steps
- **[Project Overview](docs/overview/PROJECT_OVERVIEW.md)** - Features and architecture
- **[Usage Guide](docs/reference/USAGE_GUIDE.md)** - How to use each tool
- **[Version History](docs/reference/VERSION_HISTORY.md)** - Release notes and roadmap
- **[Mathematical Model](docs/model/MathModel.tex)** - Complete formulation
- **[Troubleshooting](docs/guides/TROUBLESHOOTING.md)** - Common problems and solutions
- **[Installation Guides](docs/installation/)** - Solver setup instructions

## System Requirements

### Minimum

- RAM: 8GB
- Disk: 2GB for solvers and instances
- Python 3.8+
- MiniZinc 2.6+

### Recommended

- RAM: 16GB
- Multi-core CPU for parallel solving
- SSD for faster I/O

## Features by Version

### v2.1.0 (Current - May 2026)

- System Center GUI with theme support
- Multi-solver integration
- Professional documentation
- Complete project restructuring
- Theme persistence across sessions

### v1.4.0

- Multi-solver architecture
- Result aggregation
- HTML report generation

### v1.3.0

- Enhanced converter with validation
- Cork variant generation
- Parameter scaling improvements

### v1.2.0

- Initial multi-tool release
- Converter, Generator, Runner tools
- Basic documentation

## Getting Help

### Documentation

- [docs/getting-started/GETTING_STARTED.md](docs/getting-started/GETTING_STARTED.md) - Installation help
- [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md) - Common problems
- [docs/reference/USAGE_GUIDE.md](docs/reference/USAGE_GUIDE.md) - Tool usage

### Issues & Feedback

- GitHub Issues: Report bugs and request features
- GitHub Discussions: General questions and ideas

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Create development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if any)
pip install -r requirements.txt  # If project has this file

# Run tests
python -m pytest scripts/testing/
```

## Citation

If using this framework in research, please cite:

```bibtex
@software{clprclp2026,
  title={CLP-RCLP: Charging Logistics Optimization Framework},
  author={Quiceno, Andrey and García, Juan Francesco},
  year={2026},
  url={https://github.com/AndreyQuicenoC/CLP-RCLP_Minizinc_Lab_Enviroment}
}
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Author

**AVISPA Research Team**

- Andrey Quiceno (Lead Developer)
- Juan Francesco García (UI/Framework)

## Acknowledgments

- MiniZinc for the constraint programming framework
- Multi-solver community (Chuffed, Gecode, OR-Tools, etc.)
- Research collaborators and testers

---

**Version**: 2.1.0  
**Last Updated**: April 20, 2026  
**Status**: Production Ready
