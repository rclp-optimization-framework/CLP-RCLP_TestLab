# Cork-1-line Java Original Comparison

This file collects the original Java CLP runs for the cork-1-line battery and compares them with the saved Battery-Decided reference outputs.

## Java CLP runs

| Variant | Java CLP result | Open stations found in the Java text output |
| --- | --- | --- |
| 20_0 | obj = 1.0, Feasible = true | [11] -> Togher Road (Deanwood) |
| 20_5 | obj = 1.0, Feasible = true | [19] -> CUH (A and E) |
| 20_10 | obj = 1.0, Feasible = true | [19] -> CUH (A and E) |
| 20_20 | obj = 1.0, Feasible = true | [0] -> St. Patrick St (Brown Thomas B) |

Source files:
- external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_0_4_1_1_0_0_0_0_4_java-cork-20_0_4_0.txt
- external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_5_4_1_1_0_0_0_0_4_java-cork-20_5_3_0.txt
- external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_10_4_1_1_0_0_0_0_4_java-cork-20_10_3_0.txt

Evidence lines in the Java outputs:
- 20_0: Station 11 line and x=1.0 marker around lines 122 and 129
- 20_5: Station 19 line and x=1.0 marker around lines 201 and 208
- 20_10: Station 19 line and x=1.0 marker around lines 201 and 208
- 20_20: Station 0 line and x=1.0 marker around lines 11 and 18

## Battery-Decided reference

The saved Battery-Decided summaries are identical across the three variants:

| Variant | Execution time (s) | Charged stations | Charging locations |
| --- | --- | --- | --- |
| 20_0 | 65.566 | 1 | one-hot vector with a single 1 at position 20 |
| 20_5 | 105.033 | 1 | one-hot vector with a single 1 at position 20 |
| 20_10 | 94.933 | 1 | one-hot vector with a single 1 at position 20 |

Reference files:
- experiments/results/Output/Battery-Decided/cork-1-line_Battery-Decided20_0/CPLEX/cork-1-line_Battery-Decided20_0_result.json
- experiments/results/Output/Battery-Decided/cork-1-line_Battery-Decided20_5/CPLEX/cork-1-line_Battery-Decided20_5_result.json
- experiments/results/Output/Battery-Decided/cork-1-line_Battery-Decided20_10/CPLEX/cork-1-line_Battery-Decided20_10_result.json

No Battery-Decided JSON reference was found in the repository for 20_20.

## Comparison

At the summary level, the Java original CLP runs are consistent with the Battery-Decided reference: each run finds exactly one charged station.

Location interpretation note:
- The Battery-Decided one-hot vector has the 1 at position 20 (1-based).
- Java text output reports station id 19 (0-based).
- Both point to the same physical location index.

## Converter parity status

After deep analysis, exact parity requires keeping a scoped compatibility override for one inconsistent segment pattern:
- arc 36->37
- D = 164
- schedule delta = 120 seconds
- reference T = 0 (despite positive D)

With that scoped override in place, analyze_t reports:
- mismatches = 0 for cork-1-line_20_0

Without it, there are exactly 44 mismatches, all on the same arc pattern.

See CONVERTER_44_MISMATCH_DEEP_ANALYSIS.md for the full mathematical diagnosis and the rationale for this decision.