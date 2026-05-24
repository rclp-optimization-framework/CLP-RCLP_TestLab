# Stage 7.2: Integer Model Alignment with CPLEX Warm-Start

## Objective
Align integer model with float reference solution without touching float model, maintaining execution exclusively with CPLEX.

## What Changed

### 1. Integer Model
File: `core/models/clp_model.mzn`

- Added warm-start support for CPLEX.
- Introduced auxiliary arrays `xst_init_ws` and `xst_pref_ws` to load external seed without double-assignment errors.
- Derived effective variables `xst_init` and `xst_pref` from these auxiliary arrays.
- Maintained integer objective with weak preference to break ties among equivalent optimal solutions and favor station set chosen by float solution.

### 2. CPLEX Runner
File: `scripts/run_with_cplex.py`

- Added float reference JSON reading via `--warm-start-json`.
- Generated temporary warm-start DZN with auxiliary arrays expected by model.
- Corrected flow so runner uses original instance DZN and adds auxiliary DZN as second data file.
- Preserved temporary file in `experiments/tmp/` on failure for debugging exact MiniZinc input.

### 3. MiniZinc Executor
File: `core/runner/core/executor.py`

- Fixed support for multiple DZN files.
- Repaired broken `dzn_path` reference when parsing output, using primary instance DZN to extract metadata.
- Runner now works without external comparison scripts.

## Validated Results

- `Battery-Decided20_0` instance executed correctly with CPLEX.
- Warm-start version produced solution coherent with float for installed station.
- Runner generated valid JSON and output parsing works.

Result file: `experiments/results/cplex_int_20_0_ws.json`

## Important Observation

Original integer and float model solutions had same objective function but differed by tie-breaking among optima. Applied correction does not change float formulation and focuses on making integer model station set selection deterministic.

## Validation Completed

Direct comparison executed on available `Battery-Decided` set using runner and CPLEX, without external comparison scripts.

Validated cases:

- `cork-1-line_Battery-Decided20_0.dzn`: integer with warm-start and float agree on station 20 and total deviation.
- `cork-1-line_Battery-Decided20_5.dzn`: integer and float agree on station 20 and total deviation.
- `cork-1-line_Battery-Decided20_10.dzn`: integer and float agree on station 20 and total deviation.

Global result:

- Integer model continues working with CPLEX,
- Float model continues working with CPLEX,
- Runner processes both models correctly,
- Warm-start does not break normal execution when not used.
