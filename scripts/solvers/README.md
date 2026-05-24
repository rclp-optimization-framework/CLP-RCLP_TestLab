# Solver Management Scripts

Professional scripts for managing and testing multiple solvers in the CLP-RCLP environment.

## Available Scripts

### 1. check_solvers.py
Verify which solvers are available on your system.
```bash
python scripts/solvers/check_solvers.py
```
Output: Console report + JSON report in `experiments/results/solver_check_report.json`

### 2. diagnose_solvers.py
Comprehensive solver diagnosis with actual model execution testing.
```bash
python scripts/solvers/diagnose_solvers.py experiments/instances/battery-own/noncity_5buses-8stations.dzn [model]
```
Output: Detailed JSON reports in `experiments/results/diagnostics/`

### 3. test_multiple_solvers.py
Execute instance with multiple solvers and compare performance.
```bash
python scripts/solvers/test_multiple_solvers.py experiments/instances/battery-own/noncity_5buses-8stations.dzn [model] [solvers...]
```
Output: JSON results in `experiments/results/solver_tests/`

### 4. test_gurobi.py
Specific Gurobi solver diagnosis and license checking.
```bash
python scripts/solvers/test_gurobi.py experiments/instances/battery-own/noncity_5buses-8stations.dzn [model]
```
Output: Gurobi status report in `experiments/results/diagnostics/`

## Supported Solvers

### Working Solvers (v1.4.0)

1. **Chuffed** (Default)
   - Fast constraint solver
   - Recommended for CLP/RCLP
   - Performance: 0.99s on test instance

2. **Gecode**
   - General-purpose constraint programming
   - Good optimization capabilities
   - Performance: 0.40s on test instance

3. **COIN-BC**
   - Linear/mixed-integer programming
   - Efficient branch-and-cut implementation
   - Performance: 3.06s on test instance

4. **OR-Tools CP-SAT**
   - Google's modern constraint solver
   - Excellent for large-scale problems
   - Performance: 0.43s on test instance

5. **CPLEX** (Commercial)
   - IBM's industry-leading optimizer
   - High-performance large-scale solving
   - Performance: 0.48s on test instance
   - Status: Requires valid license

### Gurobi Solver

**Status**: Binary installed but requires valid license

Gurobi is detected in the system but needs:
1. Valid Gurobi license (free academic license available)
2. Proper DLL path configuration

**To enable Gurobi**:
1. Get license: https://www.gurobi.com/academia/academic-program-and-licenses/
2. Install Gurobi: https://www.gurobi.com/
3. Set environment variable: `export GUROBI_HOME=/path/to/gurobi`
4. Verify: `python scripts/solvers/test_gurobi.py experiments/instances/battery-own/noncity_5buses-8stations.dzn`

## Installation

### Check Solver Status
```bash
python scripts/solvers/check_solvers.py
```

### Verify with Actual Execution
```bash
python scripts/solvers/diagnose_solvers.py experiments/instances/battery-own/noncity_5buses-8stations.dzn
```

### Diagnose Gurobi
```bash
python scripts/solvers/test_gurobi.py experiments/instances/battery-own/noncity_5buses-8stations.dzn
```

## Integration with Runner

The Runner UI automatically:
- Detects available solvers
- Allows solver selection per test
- Organizes results by solver
- Stores diagnostics for failures

## Output Organization

### Successful Results
- Location: `experiments/results/{Battery}/{Solver}/`
- Formats: JSON and TXT
- Contains: instance data, solution, execution time

### Diagnostics
- Location: `experiments/results/diagnostics/{Solver}/`
- Formats: JSON and TXT
- Contains: error information, execution time, solver used

## Troubleshooting

### Solver Not Found
```bash
# Check installation
python scripts/solvers/check_solvers.py

# Verify MiniZinc
minizinc --version

# Verify PATH
echo $PATH
```

### Timeout Issues
- Increase timeout in Runner UI (default: 300s)
- Check system resources
- Try different solver

### Gurobi Not Working
```bash
# Diagnose Gurobi specifically
python scripts/solvers/test_gurobi.py experiments/instances/battery-own/noncity_5buses-8stations.dzn

# Check license
gurobi_cl --version

# Set environment
export GUROBI_HOME=/path/to/gurobi/installation
```

## Performance Comparison

Current test results (noncity_5buses-8stations.dzn):
- Gecode: 0.402s (fastest)
- OR-Tools CP-SAT: 0.432s
- CPLEX: 0.481s
- Chuffed: 0.991s
- COIN-BC: 3.055s

## Recommendations

- **For quick testing**: Use Chuffed or Gecode
- **For production**: Use CPLEX or Gurobi (with valid license)
- **For modern solving**: Use OR-Tools CP-SAT
- **For MIP problems**: Use COIN-BC, CPLEX, or Gurobi

## Authors

Andrey Quiceno and Juan Francesco García (AVISPA Team)

Last Updated: April 2026
Version: 1.4.0
