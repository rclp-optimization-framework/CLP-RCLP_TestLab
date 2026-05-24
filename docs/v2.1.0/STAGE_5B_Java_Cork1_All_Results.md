# Java Original Cork-1-Line Run Matrix

This report consolidates every cork-1-line Java original test run that is available in the repository and records the selected charging station location from the Java output text.

## Results

### Variant 20_0

- file: external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_0_4_1_1_0_0_0_0_4_java-cork-20_0_4_0.txt
- selected station id: 11
- selected station name: Togher Road (Deanwood)
- evidence lines: station block around line 122, x=1.0 around line 129

### Variant 20_5

- file: external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_5_4_1_1_0_0_0_0_4_java-cork-20_5_3_0.txt
- selected station id: 19
- selected station name: CUH (A and E)
- evidence lines: station block around line 201, x=1.0 around line 208

### Variant 20_10

- file: external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_10_4_1_1_0_0_0_0_4_java-cork-20_10_3_0.txt
- selected station id: 19
- selected station name: CUH (A and E)
- evidence lines: station block around line 201, x=1.0 around line 208

### Variant 20_20

- file: external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_20_4_1_1_0_0_0_0_4_2026-05-22_11-15-58_3_0.txt
- selected station id: 0
- selected station name: St. Patrick St (Brown Thomas B)
- evidence lines: station block around line 11, x=1.0 around line 18

## Key observation

The Java output files include both the numeric station id and the human-readable station name. The location is therefore available directly in the original Java outputs, not only the total station count.

## Comparison note

The repository contains Battery-Decided JSON references for 20_0, 20_5, and 20_10, but no Battery-Decided JSON reference was found for 20_20.
