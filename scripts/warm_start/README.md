# Warm Start Artifacts

This folder stores the warm-start research assets for CPLEX runs.

## Purpose

- Keep the base integer model clean and universally runnable.
- Materialize a warm-start-aware copy only when `--warm-start-json` is provided.
- Preserve a trace of the reference instances used during validation.

## Reference Cases

- `experiments/instances/Battery-Decided/cork-1-line_Battery-Decided20_0.dzn`
- `experiments/instances/Battery-Decided/cork-1-line_Battery-Decided20_5.dzn`
- `experiments/instances/Battery-Decided/cork-1-line_Battery-Decided20_10.dzn`

## Generated Files

When warm-start is enabled, the runner writes generated artifacts to `scripts/warm_start/generated/`:

- `*_warmstart.mzn` - temporary warm-start copy of the model.
- `*_warmstart.dzn` - warm-start assignment record.

These files are generated from the base model and the reference JSON, and can be deleted safely after inspection.

Added utilities in this folder:

- `clp_model_warmstart.mzn` — the warm-start-capable MiniZinc model (keeps `warm_start(xst,xst_init)` hook).
- `instances/` — reference instance files (copied from `experiments/instances/Battery-Decided/`) for quick testing.
- `run_warmstart.py` — small wrapper to run `minizinc --solver cplex` on a chosen model and instance and save the output.

Quick example (from `scripts/warm_start`):

```bash
python run_warmstart.py --instance instances/cork-1-line_Battery-Decided20_0.dzn --out tmp/out_20_0.txt --time 60
```

If you want the runner that generates warm-start artifacts from a float JSON, keep using `scripts/runner/run_with_cplex.py --warm-start-json <json>`; that script will place generated model and dzn files under `scripts/warm_start/generated/`.
