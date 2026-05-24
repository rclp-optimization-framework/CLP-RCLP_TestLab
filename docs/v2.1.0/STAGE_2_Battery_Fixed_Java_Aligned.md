# Battery-Fixed vs Java-Aligned

This note records the final comparison between the regenerated `Battery-Fixed` cork instance and the known-good `battery-java-aligned` baseline.

## What was wrong

The old `Battery-Fixed` generation path used two incorrect inputs:

- `model_speed=30` and `rest_time=10` were hardcoded instead of using the real JITS experiment values.
- The distance map was not loaded from the cork-1-line `distances_input.csv`, so the script fell back to incomplete data.

That changed the generated `T` block, and the runner reported `UNSATISFIABLE`.

## What was corrected

The generator in [generate_instances.py](generate_instances.py) now:

- loads the real cork-1-line experiment config from `external/jits2022/Code/data/experiment_parameters_cork1_20_0.txt`
- loads the real distance table from `external/jits2022/Code/data/cork-1-line/distances_input.csv`
- writes the regenerated instances directly into `experiments/instances/Battery-Fixed`

## Verification

After regeneration, the `Battery-Fixed20_0` instance matches `battery-java-aligned` at the data-block level:

- `Cmax`, `Cmin`, `alpha`, `mu`, `SM`, `psi`, `beta`: match
- `D`: match
- `T`: match
- `tau_bi`: match
- `st_bi`: match

The remaining SHA-256 difference is only from comment text, not from model data.

Runner validation on the regenerated file also passed:

- `Battery-Fixed20_0` -> `OPTIMAL`

## Practical outcome

The runner now sees the full `Battery-Fixed` battery at the root of `experiments/instances/Battery-Fixed`, and the cork `20_0` instance is aligned with the Java baseline.
