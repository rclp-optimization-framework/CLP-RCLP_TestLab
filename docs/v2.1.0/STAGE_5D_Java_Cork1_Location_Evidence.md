# Java Original Cork-1 Location Evidence

## Question

Can the Java original results provide the location of selected charging stations (not only the count)?

## Answer

Yes. The Java output text files include explicit station blocks with both:
- station id and station name (`Station <id> / <name>`)
- decision value (`x=1.0` when that station is selected)

## Extracted locations from executed tests

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

## Mapping note versus Battery-Decided JSON

Battery-Decided JSON stores charging locations as a one-hot vector. For these cork-1-line files, the 1 appears at position 20 (1-based), which corresponds to station id 19 in the Java text output (0-based indexing).

## Verdict

It is fully possible to obtain charging station locations from the Java original system. The information is available directly in the generated output text files, including human-readable station names.
