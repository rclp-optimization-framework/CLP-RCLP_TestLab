# Converter - JSON to DZN Conversion Tool

Professional interface for converting JITS2022 test batteries from JSON format to MiniZinc DZN format.

## Overview

The Converter tool provides an intuitive GUI to transform JSON bus schedule files from the JITS2022 dataset into the Java-compatible integer DZN format used by the CLP-RCLP models.

## Features

- **Directory Selection**: Browse and select from JITS2022 test directories
- **Batch Conversion**: Convert one or all tests from a selected directory
- **Data-Driven Conversion**: Reads actual instance data (stations, distances, speeds)
- **Schedule-Based Travel Times**: Derives travel times (T) from schedule time deltas in source data
- **Flexible Output**: Create new battery directories or use existing ones
- **Real-time Progress**: Monitor conversion status with live logging
- **Dark/Light Themes**: Professional UI with theme switching
- **Tooltips**: Context help on all major controls
- **Differentiated Scaling**: Energy-related values scaled by 1000, time values kept in seconds for MiniZinc
- **Single Output Mode**: Java-compatible integer output only

## Usage

### Launch the Interface

```bash
python Converter/converter.py
```

### Workflow

1. **Select Test Directory**
   - Choose a directory from JITS2022/Code/Data
   - Directories like `cork-1-line`, `cork-2-lines`, etc.

2. **Select Tests to Convert**
   - Option 1: Convert all JSON files in the directory
   - Option 2: Select specific test files

3. **Choose Output Battery**
  - Select an existing battery: Battery Own, Battery Project Integer, etc.
  - Files automatically organized by test name and solver subdirectories
  - The converter always writes Java-compatible integer data

4. **Start Conversion**
   - Click "Convert" to begin
   - Monitor progress in the log panel
   - Click "Stop" to cancel at any time

### Output Structure

Converted files are organized as:

```
Data/
├── Battery Own/
│   ├── cork-1-line/           # Test name directory
│   │   ├── cork-1-line_20.dzn
│   │   ├── cork-1-line_30.dzn
│   │   ├── distances_input.csv
│   │   ├── stations_input.csv
│   │   └── input_report.txt
│   └── ...
```

## Architecture

```
Converter/
├── converter.py              (Entry point)
├── config.py                 (Configuration)
├── __init__.py
│
├── core/
│   ├── __init__.py
│   ├── converter_engine.py   (JSON->DZN conversion logic)
│   ├── file_manager.py       (Directory and file operations)
│   └── jits_analyzer.py      (JITS2022 dataset analysis)
│
├── ui/
│   ├── __init__.py
│   ├── interface.py          (Main Tkinter interface)
│   ├── themes.py             (Dark/light theme system)
│   ├── components.py         (Reusable UI widgets)
│   └── tooltip.py            (Hover tooltips)
│
└── README.md                 (This file)
```

## Components

### converter_engine.py

Core conversion logic:

- Parse JSON bus schedules with JITS2022 format
- Load stations and distance matrix from CSV files
- Calculate travel times (T) using JITS2022 algorithm:
  - T = distance / speed (constrained by speed limits)
  - Includes rest time adjustments when applicable
- Generate integer DZN files or original decimal DZN files with proper formatting
- Batch conversion support with configurable parameters

### file_manager.py

File operations:

- Create output directory structure
- Copy required data files (distances, stations data)
- Validate output paths
- Cleanup on conversion failures

### jits_analyzer.py

JITS2022 dataset utilities:

- List available test directories
- Validate JSON file structure
- Extract test metadata
- Check required data file availability

### ui/interface.py

Professional Tkinter GUI:

- Directory and test selection
- Output configuration
- Real-time conversion monitoring
- Status indicators and logging

## Conversion Details

### Integer Scaling

Converter uses **differentiated scaling** by domain for precision and MiniZinc compatibility:

#### Energy Values (D, Cmax, Cmin, alpha)
- **Scale Factor**: 1000
- **Unit**: 1 integer unit = 0.001 kWh (0.1% precision)
- **Example**: 1.3 kWh → 1300 units (exact match, 0% error)
- **Rationale**: Eliminates truncation errors in accumulated energy calculations across 100+ stops

#### Time Values (T, tau_bi)
- **Scale Factor**: 1 (no scaling)
- **Unit**: Minutes as-is
- **Example**: 42 minutes → 42 units (exact)
- **Rationale**: Schedule times already precise in minutes; no scaling needed for MiniZinc compatibility

**Precision Improvement**: This approach reduces error per arc from ±10.4% (SCALE=50) to ±0.05%, improving cumulative accuracy across multi-stop routes by 200×.

### Original Decimal Mode

This mode preserves the source decimal values from the input JSON and CSV files.

- **Energy Values**: `D`, `Cmax`, `Cmin`, and `alpha` remain in raw kWh units
- **Distance Precision**: Distances are read as decimals and multiplied without rounding before writing the energy matrix
- **Time Values**: `T`, `tau_bi`, `mu`, `SM`, `psi`, `beta`, and `M` remain in their native units
- **Use Case**: Validation against the external reference model and research workflows that need the exact original decimals

### Model Parameters

Configurable parameters for CLP model (from experiment_config.py):

- **Cmax**: 100.0 kWh (battery capacity) → 100000 units
- **Cmin**: 20.0 kWh (minimum reserve) → 20000 units
- **alpha**: 10.0 kWh/min (charging rate) → 10000 units
- **mu**: 5.0 min (maximum delay) → 5 minutes (no scaling)
- **model_speed**: 30 km/h (minimum speed constraint)
- **rest_time**: 10 min (rest duration at stops)

Configuration can be modified via experiment_config.py or config files.

### Required Data Files

The converter requires the following files for correct operation:

- **buses*input*<speed>\_<rest>.json**: Bus routes, stops, and schedules
  - REQUIRED for all conversions
  - Filename pattern determines speed and rest parameters

- **distances_input.csv**: Distance matrix between stations
  - REQUIRED for calculating travel times (T)
  - Used with actual speeds to compute journey durations
  - Values in kilometers (converted to meters internally)

- **stations_input.csv**: Station names and identifiers
  - REQUIRED for mapping station references
  - Defines num_stations and station names

Optional/Legacy Files:

- **input_report.txt**: Dataset statistics
  - Currently not used by converter
  - Kept for reference but does not affect conversion

## Theme Support

Toggle between Dark and Light modes using the button in the header:

- **Dark Mode** (default): Optimized for extended use
- **Light Mode**: High contrast alternative

## Tooltips

Hover over [?] icons to get context-specific help:

- Which directory to select
- How conversion works
- What JSON and DZN formats are
- Support file information

## Requirements

- Python 3.8+
- tkinter (usually included with Python)
- pathlib, json, logging (standard library)

## Related Tools

- **Generator**: Create new test instances
- **Runner**: Execute tests with multiple solvers
- Scripts/data-processing/convert_json_to_integer_dzn.py: CLI conversion script
- scripts/verification/verify_original_decimal_converter.py: Validates the original decimal output mode

## Troubleshooting

### "No JSON files found"

- Verify the selected directory contains JSON files
- Check file names match `buses_input_*.json` pattern

### "Loading stations and distance data..." error

- Ensure distances_input.csv exists in the directory
- Ensure stations_input.csv exists in the directory
- These files are now REQUIRED (not optional)
- Check file names are exactly: `distances_input.csv`, `stations_input.csv`

### Conversion failed

- Check output directory is writable
- Ensure JSON files are valid
- Verify required CSV files are present and readable
- Check available disk space

### "Zero or negative time delta" warnings

- These are normal for JITS2022 instances with consecutive duplicate stations
- Indicates a stop where bus stays at same location (rest)
- Converter handles this gracefully by using default 1-minute delta

## Technical Notes

- Conversion is performed in a separate thread to keep UI responsive
- Failed conversions are cleaned up automatically
- All paths are cross-platform compatible (Windows/Linux/macOS)
- Logging with timestamps for debugging

## Author

AVISPA Research Team
Date: April 2026
Version: 1.5.0 (Energy Precision Enhancement - SCALE_ENERGY=1000)
