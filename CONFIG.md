# CLP-RCLP v2.1.0 Installation Guide

## Prerequisites

- **Python**: 3.8 or higher
- **MiniZinc**: 2.6 or higher
- **Operating System**: Windows, macOS, or Linux
- **Git**: For cloning the repository

## Step 1: Python Environment Setup

Create a virtual environment to isolate project dependencies:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Step 2: Install MiniZinc

Download MiniZinc 2.6+ from [https://www.minizinc.org/](https://www.minizinc.org/)

**Windows**: Run the installer and add MiniZinc to your PATH.
**macOS**: Use Homebrew: `brew install minizinc`
**Linux**: Follow distribution-specific instructions at [https://www.minizinc.org/doc-2.6.0/en/installation.html](https://www.minizinc.org/doc-2.6.0/en/installation.html)

Verify installation:
```bash
minizinc --version
```

## Step 3: Install Python Dependencies

With virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Key packages**:
- `PySimpleGUI>=4.60` - GUI framework for System Center and tools
- `minizinc>=0.26.0` - MiniZinc Python interface
- `pydantic>=2.0` - Configuration validation
- `requests>=2.28` - HTTP library for API calls

## Step 4: Optional - Install Solvers

The framework uses MiniZinc's bundled solvers (Chuffed, Gecode, COIN-BC, OR-Tools) by default. For advanced features:

### Install CPLEX

1. Download IBM CPLEX Studio from [IBM website](https://www.ibm.com/products/ilog-cplex-optimization-studio)
2. Install and configure Python binding:
   ```bash
   python setup.py install
   # or
   pip install cplex
   ```

### Install Gurobi

1. Download Gurobi from [https://www.gurobi.com/](https://www.gurobi.com/)
2. Install and activate license
3. Install Python package:
   ```bash
   pip install gurobipy
   ```

Refer to [docs/installation/](docs/installation/) for detailed solver setup instructions.

## Step 5: Launch the System Center

Start the main GUI interface:

```bash
python core/start.py
```

The System Center GUI opens with access to:
- **Data Converter** - Transform JSON data to MiniZinc format
- **Instance Generator** - Create synthetic test datasets
- **Test Runner** - Execute optimization with multiple solvers

## Project Structure

```
core/
  ├── models/              # MiniZinc models (CLP, RCLP)
  ├── converter/           # JSON to DZN conversion engine
  ├── generator/           # Instance generation system
  ├── runner/              # Optimization runner
  ├── orchestration/       # GUI orchestrator (System Center)
  └── shared/              # Common utilities and navigation

experiments/
  ├── instances/           # Test data (Battery-Decided, battery-own, battery-generated)
  └── results/             # Optimization results and diagnostics

scripts/
  ├── solvers/             # Solver availability checking and diagnostics
  ├── testing/             # Integration and regression tests
  ├── verification/        # Converter and model verification
  ├── runner/              # CPLEX runner entry point
  └── debug/               # Investigation and diagnostic utilities

docs/
  ├── installation/        # Installation guides for solvers and dependencies
  ├── guides/              # User guides and troubleshooting
  └── model/               # Mathematical formulation and theory
```

## Troubleshooting

### MiniZinc not found
Ensure MiniZinc is installed and in your system PATH:
```bash
# Verify
minizinc --version
```

### PySimpleGUI errors
Ensure you're using Python 3.8+:
```bash
python --version
```

### CPLEX/Gurobi not detected
Follow the solver-specific installation instructions in [docs/installation/](docs/installation/).

### Import errors
Ensure your virtual environment is activated and requirements are installed:
```bash
pip list | grep -E "PySimpleGUI|minizinc|pydantic"
```

## Documentation

- **Getting Started**: [docs/getting-started/](docs/getting-started/GETTING_STARTED.md)
- **User Guides**: [docs/guides/](docs/guides/)
- **Architecture**: [docs/architecture/](docs/architecture/)
- **Model Reference**: [docs/model/](docs/model/PROJECT_SUMMARY.md)

## Support

For issues or questions:
1. Check [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md)
2. Review GitHub issues: [github.com/rclp-optimization-framework/CLP-RCLP_TestLab](https://github.com/rclp-optimization-framework/CLP-RCLP_TestLab)
3. Contribute: See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - See [LICENSE](LICENSE) for details.
