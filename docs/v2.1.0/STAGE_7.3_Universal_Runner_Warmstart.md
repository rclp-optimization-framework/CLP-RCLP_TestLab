# Stage 7.3: Universal Runner with Optional Warm-Start

## Objective
Thoroughly review execution flow so runner works correctly with:

- Cork instances,
- Real instances,
- Synthetic instances,
- Integer model,
- Float model,
- Warm-start only when useful reference case exists.

Priority was keeping system modular, stable, usable without depending on prior examples.

## Diagnosis

Previous warm-start solution worked for reference instance `20_0` but left two risks:

- Integer model became dependent on warm-start data that doesn't always exist,
- Could break normal runner executions on other instances.

This was problematic for general system, because runner must solve any instance without requiring prior seed.

## What Was Fixed

### 1. Integer Model
File: `core/models/clp_model.mzn`

Restored universal behavior so integer model runs without warm-start dependency.

- `xst_init` and `xst_pref` became normal vectors by default.
- Objective continues incorporating weak tie-breaking that already existed, but now activates usefully only when runner materializes temporary model version.
- Base file becomes safe for any instance, even when no prior reference JSON exists.

### 2. Runner
File: `scripts/run_with_cplex.py`

Changed warm-start approach to be optional and not invade normal flow.

- If `--warm-start-json` not passed, runner executes base model directly.
- If `--warm-start-json` passed, runner creates temporary model in `experiments/tmp/` with warm-start values embedded.
- Avoids MiniZinc error from double assignment and doesn't force auxiliary data to base model.
- Runner continues serving any instance with same usual behavior.

### 3. Executor
File: `core/runner/core/executor.py`

Executor continues supporting normal flow with single DZN and maintains general runner compatibility.

- Output parsing preserved.
- Metadata extraction from primary DZN maintained.
- No extra dependencies introduced for user interface.

## Validation Performed

System verified with CPLEX on `Battery-Decided` instances and both models.

### Base Case Without Warm-Start
- `cork-1-line_Battery-Decided20_5.dzn`
- `cork-1-line_Battery-Decided20_10.dzn`

Result:

- Integer model solved correctly,
- Float model solved correctly,
- Runner generated valid JSON in both cases.

### Case With Warm-Start
- `cork-1-line_Battery-Decided20_0.dzn`
- Using `cplex_float_20_0.json` as reference

Result:

- Runner created temporary warm-start model,
- CPLEX solved correctly,
- Integer result matched float solution in installed station and total deviation.

## Functional Result

System reached more robust state:

- Runner works for normal cases without warm-start requirement,
- Warm-start used only when provides value,
- Float model not altered,
- Integer model remains executable for entire instance catalog,
- No UI modifications added.

## Key Files

- `core/models/clp_model.mzn`
- `core/models/clp_model_float.mzn`
- `scripts/run_with_cplex.py`
- `core/runner/core/executor.py`

## Conclusion

Correct strategy for this system was not making warm-start mandatory, but keeping runner universal and using temporary template only when reliable prior reference exists. This preserves modularity and avoids breaking general system use.
