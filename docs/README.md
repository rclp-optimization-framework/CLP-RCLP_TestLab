# CLP-RCLP Documentation

Complete documentation for the CLP-RCLP optimization framework.

## Quick Navigation

### Getting Started

- **[getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md)** - Installation and first steps ⭐ Start here!
- **[overview/PROJECT_OVERVIEW.md](overview/PROJECT_OVERVIEW.md)** - What is CLP-RCLP and how it works
- **[reference/VERSION_HISTORY.md](reference/VERSION_HISTORY.md)** - Version history and migration guides

### Using the Tools

- **[reference/USAGE_GUIDE.md](reference/USAGE_GUIDE.md)** - Detailed guide for each tool (GUI and CLI)
- **[guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)** - Solutions to common problems
- **[guides/](guides/)** - Additional user guides

### Technical Documentation

- **[model/QUICKSTART.md](model/QUICKSTART.md)** - Quick mathematical overview
- **[model/MathModel.tex](model/MathModel.tex)** - Complete mathematical formulation
- **[model/README.md](model/README.md)** - Model documentation index

### Installation & Setup

- **[installation/minizinc_installation.md](installation/minizinc_installation.md)** - MiniZinc setup
- **[installation/gurobi_installation.md](installation/gurobi_installation.md)** - Gurobi solver (optional)
- **[installation/cplex_installation.md](installation/cplex_installation.md)** - CPLEX solver (optional)
- **[installation/README.md](installation/README.md)** - Installation index

## Directory Structure

```
docs/
├── README.md                           # This file (documentation index)
│
├── getting-started/                    # For new users
│   └── GETTING_STARTED.md             # Installation and quick start
│
├── overview/                           # Project information
│   └── PROJECT_OVERVIEW.md            # Features and architecture
│
├── reference/                          # Complete reference documentation
│   ├── USAGE_GUIDE.md                 # How to use each tool
│   └── VERSION_HISTORY.md             # Release notes and roadmap
│
├── guides/                             # User guides and troubleshooting
│   └── TROUBLESHOOTING.md             # Problem solutions
│
├── installation/                       # Solver installation guides
│   ├── minizinc_installation.md
│   ├── gurobi_installation.md
│   ├── cplex_installation.md
│   └── README.md
│
└── model/                              # Mathematical documentation
    ├── QUICKSTART.md
    ├── MathModel.tex
    └── README.md
```

## For Different Users

### First-Time Users

1. Read: [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md)
2. Launch: `python core/start.py`
3. Explore: System Center GUI
4. Learn: [overview/PROJECT_OVERVIEW.md](overview/PROJECT_OVERVIEW.md)

### Researchers & Scientists

1. Review: [overview/PROJECT_OVERVIEW.md](overview/PROJECT_OVERVIEW.md)
2. Study: [model/MathModel.tex](model/MathModel.tex)
3. Use: [reference/USAGE_GUIDE.md](reference/USAGE_GUIDE.md)
4. Benchmark: Compare solvers with Runner tool
5. History: [reference/VERSION_HISTORY.md](reference/VERSION_HISTORY.md)

### Developers & Contributors

1. Setup: [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md)
2. Understand: [core/README.md](../core/README.md)
3. Reference: [model/MathModel.tex](model/MathModel.tex)
4. Debug: [guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)

### System Administrators

1. Install: [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md) + [installation/](installation/)
2. Verify: Run `python scripts/solvers/check_solvers.py`
3. Configure: `core/*/config.py` files
4. Monitor: Check `experiments/results/`

## Finding What You Need

### By Topic

| Topic                     | Location                                                                 |
| ------------------------- | ------------------------------------------------------------------------ |
| Getting Started           | [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md) |
| How to Use Tools          | [reference/USAGE_GUIDE.md](reference/USAGE_GUIDE.md)                     |
| Understanding the Project | [overview/PROJECT_OVERVIEW.md](overview/PROJECT_OVERVIEW.md)             |
| Mathematical Model        | [model/MathModel.tex](model/MathModel.tex)                               |
| Installation Issues       | [installation/](installation/)                                           |
| Solver Problems           | [guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)                   |
| Version Information       | [reference/VERSION_HISTORY.md](reference/VERSION_HISTORY.md)             |

### By Task

**Generate and Run Optimization**
→ [reference/USAGE_GUIDE.md](reference/USAGE_GUIDE.md#batch-workflow-example)

**Install Additional Solvers**
→ [installation/](installation/)

**Compare Solver Performance**
→ [reference/USAGE_GUIDE.md](reference/USAGE_GUIDE.md#test-runner)

**Convert Data to MiniZinc**
→ [reference/USAGE_GUIDE.md](reference/USAGE_GUIDE.md#data-converter)

**Generate Test Instances**
→ [reference/USAGE_GUIDE.md](reference/USAGE_GUIDE.md#instance-generator)

**Understand the Model**
→ [model/QUICKSTART.md](model/QUICKSTART.md) or [model/MathModel.tex](model/MathModel.tex)

**Troubleshoot Problems**
→ [guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)

## System Requirements

- Python 3.8+
- MiniZinc 2.6+
- 2GB disk space for solvers
- 8GB RAM minimum
- Multi-core CPU recommended

See [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md) for details.

## Key Features

✓ Multi-tool framework (Generator, Converter, Runner)
✓ Professional GUI (System Center)
✓ Multiple solvers (6 supported)
✓ Complete documentation
✓ Real-world data support
✓ Scalable to large instances

See [overview/PROJECT_OVERVIEW.md](overview/PROJECT_OVERVIEW.md) for more.

## Version Information

**Current Version**: 2.1.0 (May 2026)

Major update with:

- System Center GUI with theme support
- Multi-solver integration
- Professional documentation
- Complete project restructuring

See [reference/VERSION_HISTORY.md](reference/VERSION_HISTORY.md) for upgrade guides.

## Support

| Question                | Resource                                                                 |
| ----------------------- | ------------------------------------------------------------------------ |
| How do I install?       | [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md) |
| How do I use a tool?    | [reference/USAGE_GUIDE.md](reference/USAGE_GUIDE.md)                     |
| Something isn't working | [guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)                   |
| What is the framework?  | [overview/PROJECT_OVERVIEW.md](overview/PROJECT_OVERVIEW.md)             |
| How do solvers work?    | [installation/](installation/)                                           |

## Contributing

Documentation improvements welcome! See main README.md for contribution guidelines.

---

**Last Updated**: April 20, 2026  
**Version**: 2.1.0
