# Runner Scripts

This folder contains the main execution entry point for the CLP-RCLP workflow.

## `run_with_cplex.py`

Main runner for executing a model with CPLEX. It resolves the repository root from its own location and can optionally generate warm-start artifacts under `scripts/warm_start/generated/`.

### Usage

```bash
python scripts/runner/run_with_cplex.py --help
python scripts/runner/run_with_cplex.py --model core/models/clp_model.mzn --dzn experiments/instances/battery-own/noncity_5buses-8stations.dzn --out experiments/results/cplex_int_20_0.json
```

### Notes

- Use `--warm-start-json` only when you want warm-start artifacts generated.
- The base model stays clean unless warm-start mode is explicitly enabled.
