# Java vs Minizinc Stage Diagnostic

## Goal

Determine why the Java original and the Python/Minizinc stack do not always select the same charging station even when the DZN data matches.

## What matches now

1. The converter-side DZN parity for cork-1-line_20_0 is exact after the scoped compatibility guard for the 36->37 segment.
2. The Java original output files expose the selected station location directly.
3. The Java original and the Python/Minizinc stack both agree that exactly one station is charged in the cork-1-line runs.

## What does not match

For cork-1-line_20_0:

- Java original output selects station 11.
- The exact same battery-java-aligned DZN solved by the Python/Minizinc stack with `clp_model_float.mzn` and CPLEX selects station 19.
- The integer model `clp_model.mzn` on the same DZN selects station 31.

That means the divergence is not caused by the converter anymore. It appears in the model/solver layer.

## Evidence from controlled checks

1. Converter parity check:
   - `python analyze_t.py`
   - Result: `mismatches 0`

2. Exact DZN solved with the floating model:
   - model: `core/models/clp_model_float.mzn`
   - solver: CPLEX
   - selected station: 19

3. Exact DZN solved with the integer model:
   - model: `core/models/clp_model.mzn`
   - solver: CPLEX
   - selected station: 31

4. Naive global tie-break experiment:
   - A simple secondary preference on the station index forced the 20_0 solution to station 1.
   - That did not reproduce Java and therefore is not a valid global correction.

## Diagnosis by stage

### Converter

The converter is not the source of the station-location mismatch anymore. The generated DZN now matches the Java-aligned reference exactly for the tested cork-1-line_20_0 case.

### Runner

The runner is selecting the model based on DZN precision correctly. The DZN is classified as floating, so the floating model is the expected path.

### Model / solver

This is the active divergence point. The exact same data produces a different optimal station choice depending on the solver/model combination, which means the solution is not uniquely determined by the current objective and constraints.

## Conclusion

The 20_0 station mismatch is a solver/model tie-breaking problem, not a converter problem.

The current Minizinc models are under-constrained with respect to the station-location choice among multiple optimal solutions. The Java original and CPLEX through MiniZinc explore that optimum space differently.

## Practical implication

If the requirement is exact replication of the Java original station location for every cork-1-line variant, the next step is not a converter tweak. It requires a model-level tie-break or an explicit emulation of the Java search preference.

If the requirement is only DZN parity, the current converter state is already correct.
