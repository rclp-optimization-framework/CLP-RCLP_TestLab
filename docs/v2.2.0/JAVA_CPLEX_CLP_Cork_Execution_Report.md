# Java CPLEX CLP — Cork Execution Report

Summary of runs from the original JITS Java stack (`core.Executor`) with **CPLEX** and the **CLP chargers** model (Laura extension, robust warm-start chain). Source detail: `JAVA_CPLEX_CLP_cork_results.md`.

---

## 1. Scope and configuration

| Item | Value |
|------|--------|
| Solver | IBM CPLEX (`method: cplex` in experiment parameters) |
| Objective | Minimize number of chargers (`CHARGERS`) |
| Battery capacity | 120,000 m |
| Model / instance speed | 20 km/h (all variants below) |
| Dataset variants | Rest time 0, 5, 10, 20 min → labels `20_0`, `20_5`, `20_10`, `20_20` |
| Instances | Cork-1 (`cork-1-line`), Cork-2 (`cork-2-lines`), Cork-3 (`cork-3-lines`) |
| Parameter files | `external/jits2022/Code/data/experiment_parameters_cork{1,2,3}_20_*.txt` |
| Solution outputs | `external/jits2022/Code/data/output_<dataset>_chargers_120000_20_<rest>_*.txt` |

**Variant label:** `20_<r>` = speed 20 km/h, driver rest time `<r>` minutes.

---

## 2. Run coverage

| Instance | Lines in dataset | 20_0 | 20_5 | 20_10 | 20_20 |
|----------|------------------|------|------|-------|-------|
| Cork-1 | 1 | Complete | Complete | Complete | Complete |
| Cork-2 | 2 | Complete | Complete | Not run | Not run |
| Cork-3 | 3 | Complete | Not run | Not run | Not run |

**7 of 12** variant runs produced a parseable solution file. **5** remain without complete CPLEX output.

---

## 3. Results overview

Stations count comes from `stations_input.csv` (579 for all three datasets). Buses count is the number of active buses in the printed solution (`Bus N:` stop-count lines in the output file).

| Instance | Variant | Status | Stations | Buses | Charger station(s) | Station name(s) |
|----------|---------|--------|----------|-------|-------------------|-----------------|
| Cork-1 | 20_0 | Complete | 579 | 4 | 11 | Togher Road (Deanwood) |
| Cork-1 | 20_5 | Complete | 579 | 3 | 19 | CUH (A and E) |
| Cork-1 | 20_10 | Complete | 579 | 3 | 19 | CUH (A and E) |
| Cork-1 | 20_20 | Complete | 579 | 3 | 0 | St. Patrick St (Brown Thomas B) |
| Cork-2 | 20_0 | Complete | 579 | 10 | 39 | South Mall (VHI House Stop A) |
| Cork-2 | 20_5 | Complete | 579 | 9 | 39 | South Mall (VHI House Stop A) |
| Cork-2 | 20_10 | Missing | 579 | — | — | — |
| Cork-2 | 20_20 | Missing | 579 | — | — | — |
| Cork-3 | 20_0 | Complete | 579 | 15 | 39, 78 | South Mall (VHI House Stop A); St. Patrick Street (Marks and Spencer) |
| Cork-3 | 20_5 | Missing | 579 | — | — | — |
| Cork-3 | 20_10 | Missing | 579 | — | — | — |
| Cork-3 | 20_20 | Missing | 579 | — | — | — |

**Note:** Cork-3 `20_0` installs **two** chargers (stations 39 and 78). Other completed runs show **one** charger with `x = 1.0` and positive charging time (`ct > 0`).

---

## 4. Output files (completed runs)

Relative paths from repository root.

| Instance | Variant | Output file |
|----------|---------|-------------|
| Cork-1 | 20_0 | `external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_0_4_1_1_0_0_0_0_4_31-05-2026-11-24-34-p--m-_4_0.txt` |
| Cork-1 | 20_5 | `external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_5_4_1_1_0_0_0_0_4_31-05-2026-11-23-45-p--m-_3_0.txt` |
| Cork-1 | 20_10 | `external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_10_4_1_1_0_0_0_0_4_01-06-2026-01-09-46_3_0.txt` |
| Cork-1 | 20_20 | `external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_20_4_1_1_0_0_0_0_4_01-06-2026-01-14-28_3_0.txt` |
| Cork-2 | 20_0 | `external/jits2022/Code/data/output_cork-2-lines_chargers_120000_20_0_4_1_1_0_0_0_0_4_31-05-2026-10-58-36-p--m-_10_0.txt` |
| Cork-2 | 20_5 | `external/jits2022/Code/data/output_cork-2-lines_chargers_120000_20_5_4_1_1_0_0_0_0_4_01-06-2026-01-18-49_9_0.txt` |
| Cork-3 | 20_0 | `external/jits2022/Code/data/output_cork-3-lines_chargers_120000_20_0_4_1_1_0_0_0_0_4_31-05-2026-11-25-35-p--m-_15_0.txt` |

---

## 5. Charger selection evidence (completed runs)

Selection criterion: stop where `x = 1.0` with charging activity (`ct > 0` or `e > 0`, `xBStop = 1.0`). Line numbers refer to the output file listed above.

| Instance | Variant | Station ID | Location | Bus (output) | Evidence (output line) |
|----------|---------|------------|----------|--------------|-------------------------|
| Cork-1 | 20_0 | 11 | Togher Road (Deanwood) | 0, stop 11 | Station ~122, `x=1.0` ~129 |
| Cork-1 | 20_5 | 19 | CUH (A and E) | 0, stop 271 | Station ~2721, `x=1.0` ~2728 |
| Cork-1 | 20_10 | 19 | CUH (A and E) | 0, stop 104 | Station ~1051, `x=1.0` ~1058 |
| Cork-1 | 20_20 | 0 | St. Patrick St (Brown Thomas B) | 0, stop 41 | Station ~421, `x=1.0` ~428 |
| Cork-2 | 20_0 | 39 | South Mall (VHI House Stop A) | 0, stop 82 | Station ~838, `x=1.0` ~845 |
| Cork-2 | 20_5 | 39 | South Mall (VHI House Stop A) | 0, stop 82 | Station ~837, `x=1.0` ~844 |
| Cork-3 | 20_0 | 39 | South Mall (VHI House Stop A) | 0, stop 292 | Station ~2943, `x=1.0` ~2950 |
| Cork-3 | 20_0 | 78 | St. Patrick Street (Marks and Spencer) | 4, stop 117 | Station ~19881, `x=1.0` ~19888 |

### Example (Cork-1, 20_0)

```
Bus 0, Stop 11
Station 11 / Togher Road (Deanwood)
 ...
 ct=60.0
 xBStop=1.0
 x=1.0
```

---

## 6. Pending runs

| Instance | Variants not completed |
|----------|-------------------------|
| Cork-2 | 20_10, 20_20 |
| Cork-3 | 20_5, 20_10, 20_20 |

To run missing variants and refresh the detailed log:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_java_cork_results.ps1
```

The script skips variants that already have a complete output file, then updates `JAVA_CPLEX_CLP_cork_results.md`. Regenerate this report from that file after new runs finish.

**Data:** `cork-3-lines` bus and distance inputs (`buses_input_*.json`, `distances_input.csv`) are required for Cork-3 pending variants; they were restored from git for execution.

---

## 7. How to read the tables

| Column | Meaning |
|--------|---------|
| Stations | Candidate charging locations in the instance |
| Buses | Buses kept after preprocessing, as reported in the solution output |
| Charger station(s) | Station ID(s) where a charger is installed in the parsed solution |
| Status **Complete** | Output file exists, contains route dumps, and at least one valid `x=1.0` charge stop |
| Status **Missing** | No complete output file yet (run not finished or failed before write) |

---

*Generated from execution artifacts recorded in `JAVA_CPLEX_CLP_cork_results.md`.*
