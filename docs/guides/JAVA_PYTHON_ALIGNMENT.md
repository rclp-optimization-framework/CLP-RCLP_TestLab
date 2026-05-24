# Java and Python Alignment for Battery Instances

This note records the alignment work done to match the Python/MiniZinc pipeline with the original JITS2022 Java baseline for battery instances.

## What was found

The Java baseline and the Python converter were not using the same unit convention:

- Java stores route consumption in integer distance-like units, using `distance * 1000`.
- The Python converter originally produced `battery-original` instances in raw decimal kWh.
- The Java baseline also computes a minimum added-energy requirement per bus and uses it in the optimization model.

For the `cork-1-line` `20_0` case, the original decimal DZN did not force any charging under the CLP energy constraint, while Java still produced an optimal solution with one installed charger.

## What changed

### Converter

A new `java` output mode was added to the converter engine:

- `D` is emitted in Java-compatible integer units.
- `Cmax`, `Cmin`, and `alpha` are emitted using the Java convention.
- Time-related values are emitted in seconds so the instance is closer to the Java execution model.
- The UI exposes the new `Java-compatible mode` option.

### CLP model

The integer CLP model was adjusted to use data-driven bounds instead of fixed hardcoded ranges. This lets the model work with larger Java-aligned values without type or bound issues.

### RCLP model

The float RCLP model had a sign bug in the time recursion:

- Before: `t[b,i] >= t[b,i-1] + ct[b,i-1] - T[b,i]`
- After: `t[b,i] >= t[b,i-1] + ct[b,i-1] + T[b,i]`

The float model bounds were also updated to use data-driven upper limits.

## Verification performed

For `cork-1-line_battery-original20_0.json` converted with the Java-compatible mode:

- CLP solved optimally with `Total stations = 1`.
- That matches the Java baseline non-robust objective for the same case.

The RCLP float model is still harder to solve on this instance and currently returns `UNKNOWN` under the tested time limits, even after fixing the sign bug.

## Current status

- CLP: aligned on the tested case `20_0`.
- RCLP: formula corrected, but still needs more tuning or a separate robustness calibration pass.

## Practical recommendation

Use the `java` conversion mode when the goal is to compare Python/MiniZinc against the Java baseline.
Use the existing normalized/original modes only when you intentionally want those alternate semantics.

## Files touched

- [core/converter/core/converter_engine.py](../../core/converter/core/converter_engine.py)
- [core/converter/ui/interface.py](../../core/converter/ui/interface.py)
- [core/models/clp_model.mzn](../../core/models/clp_model.mzn)
- [core/models/clp_model_float.mzn](../../core/models/clp_model_float.mzn)
- [core/models/rclp_model_float.mzn](../../core/models/rclp_model_float.mzn)
