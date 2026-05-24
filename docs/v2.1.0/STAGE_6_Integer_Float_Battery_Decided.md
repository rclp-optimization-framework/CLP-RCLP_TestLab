# Stage 6: Integer/Float Model Alignment for Battery-Decided

## Current Status

- Runner interface no longer exposes CPLEX parameters to users.
- Runner uses CPLEX internally with hidden default values.
- `scripts/check_java_equivalence.py` now targets `experiments/instances/Battery-Decided`.
- Equivalence checking no longer depends on manual CPLEX parameters.
- Equivalence checking no longer imposes internal timeout in `MiniZincExecutor`.

## Confirmed Findings

- Java reference for `Battery-Decided` indicates:
  - `20_0` -> Station 11 in Java text, but reference JSON stores position 20 as one-hot.
  - `20_5` -> Station 19.
  - `20_10` -> Station 19.
- Active MiniZinc models still do not reproduce this selection stably across variants.
- Mismatch does not appear to come from DZN converter; solver/model is the active issue.
- Current validation against `Battery-Decided` shows active model still selects different stations than Java reference.

## Suggested Next Steps

- Compare full MiniZinc model output against `Battery-Decided` reference JSON.
- Review if solver wrapper or MiniZinc/CPLEX search order alters station selection.
- If needed, introduce controlled constraint or secondary preference to match Java station.
