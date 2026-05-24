# Stage 8: Integer/Float Alignment and Warm-Start Flow

## Summary
- **Objective**: Document decision to align integer model with float model and describe reproducible warm-start flow.
- **Status**: Implemented; warm-start is optional and materialized in `scripts/warm_start/generated/` when requested.

## Key Decisions
- Removed lexicographic tie-breaker from integer model (`core/models/clp_model.mzn`) so objective function equivalent to float model: minimize `sum(st in ST)(xst[st])`.
- Removed warm-start placeholders and directives from base model to avoid duplicate DZN assignments.

## Warm-Start Design
- Warm-start generated only when `--warm-start-json` passed to runner (`scripts/run_with_cplex.py`).
- Flow: First obtain float model output (JSON), then pass that JSON to runner to generate temporary model and warm-start `.dzn` executed against integer model.
- Generated artifacts saved in `scripts/warm_start/generated/` with names like:
  - `clp_model_<instance>_warmstart.mzn`
  - `<instance>_warmstart.dzn`

## How to Reproduce (Examples)

### Run float model (generates reference JSON)
```bash
python scripts/run_with_cplex.py --model core/models/clp_model_float.mzn --dzn <instance.dzn> --out experiments/results/cplex_float_<id>.json --time 1200
```

### Run integer model WITHOUT warm-start
```bash
python scripts/run_with_cplex.py --model core/models/clp_model.mzn --dzn <instance.dzn> --out experiments/results/post_int_<id>.json --time 1200
```

### Run integer model WITH warm-start (uses JSON from float)
```bash
python scripts/run_with_cplex.py --model core/models/clp_model.mzn --dzn <instance.dzn> --warm-start-json experiments/results/cplex_float_<id>.json --out experiments/results/post_int_<id>_ws.json --time 1200
```

## Validated Instances
Verified equality of `charging_locations` between integer and float models on instances: `Battery-Decided20_0`, `Battery-Decided20_5`, `Battery-Decided20_10` (known as `cork-1-line_...`).

## Relevant Technical Changes
- `core/runner/core/executor.py`: Output parsing correction using `dzn_paths[0]` to avoid undefined `dzn_path` error.
- `core/models/clp_model.mzn`: Removed warm-start placeholders and lexicographic tie-breaker; objective aligned to float model.
- `scripts/run_with_cplex.py`: Implemented generation of model and warm-start `.dzn` in `scripts/warm_start/generated/` only when requested.

## Notes and Recommendations
- Do not modify base models to include warm-start values by default; always materialize artifacts in `scripts/warm_start/generated/` for reproducibility.
- Suggested next step: Review `ConverterEngine/DataLoader` to ensure no regressions in instance preparation.

## Additional Validation
- Run exhaustive validation on entire `Battery-Decided` set.
- Review and document `ConverterEngine/DataLoader`.
