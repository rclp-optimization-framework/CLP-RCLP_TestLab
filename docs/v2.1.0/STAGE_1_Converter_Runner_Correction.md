# Stage 1: Converter and Runner Correction

This document summarizes the corrections applied to align Cork conversion with the Java baseline and ensure the runner returns expected MiniZinc results.

## What Was Fixed

- Restored `original` conversion mode in `core/converter/core/converter_engine.py`.
- Maintained `java` mode for generating instances equivalent to Java baseline.
- Corrected parameter generation in `java` mode for Cork:
  - `Cmax` and `Cmin` remain in the same scale as Java-aligned instances.
  - `alpha` emitted in units per second, as expected by the model.
  - `mu`, `SM`, `psi`, `beta`, and `M` generated with same time convention used by Java.
- Improved `UNSATISFIABLE` detection in executor for correct runner status reporting.

## Verified Results

Validated `cork-1-line` case `20_0` with real JITS configuration:

- Converter: `output_format="java"`
- Source file: `external/jits2022/Code/data/cork-1-line/buses_input_20_0.json`
- Parameters: `external/jits2022/Code/data/experiment_parameters_cork1_20_0.txt`
- MiniZinc model: `core/models/clp_model_float.mzn`

Results obtained:

- `Total stations: 1`
- `Installed stations` with single active station

Runner validation on corrected instance:

```powershell
python scripts/testing/run_battery_project_tests.py --data-dir experiments/instances/battery-java-aligned --pattern "cork-1-line_battery-java20_0.dzn" --limit 1 --solver cplex --time-limit 300000
```

Output:

- `Solution: OPTIMAL`
- `Stations: 1`

## Example Corrected Instance

A corrected instance should have this header logic:

```dzn
num_buses = 4;
num_stations = 40;

Cmax = 120000;
Cmin = 15000;
alpha = 167;

mu = 240;
SM = 60;
psi = 60;
beta = 600;
M = 100000;
```

Matrices must preserve same semantics as Java:

- `D`: energy consumption in integer units equivalent to baseline
- `T`: integer travel times
- `tau_bi`: arrival times in seconds or minutes per dataset convention

## How to Reproduce

1. Generate instance using converter.
2. Run runner against generated directory.
3. Confirm Cork case `20_0` reports single station.

To regenerate manually, use Cork JSON with real JITS experiment configuration.
