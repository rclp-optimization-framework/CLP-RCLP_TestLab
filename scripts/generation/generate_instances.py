#!/usr/bin/env python3
"""
Generate all cork-1-line instances using battery-java-aligned configuration.

This script regenerates all 12 test cases with the correct configuration
that matches battery-java-aligned (which produces SATISFIABLE instances).

Configuration parameters used:
    - Cmax: 120 kWh (Java units: 120000)
    - Cmin: 15 kWh (Java units: 15000)
    - chargingRate: 10 kWh/min (Java units: 167 after conversion)
    - dt_max: 4 min (Java units: 240 seconds)
"""

import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.converter.core.experiment_config import ExperimentConfig
from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.data_loader import DataLoader
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Cork-1-line test variants
VARIANTS = [
    "20_0", "20_5", "20_10", "20_20",
    "30_0", "30_5", "30_10", "30_20",
    "40_0", "40_5", "40_10", "40_20"
]

def main():
    """Generate all instances."""
    
    # Load the real JITS experiment parameters for cork-1-line.
    # These values drive the travel-time convention and must match the
    # Java-aligned baseline exactly.
    config_file = project_root / "external" / "jits2022" / "Code" / "data" / "experiment_parameters_cork1_20_0.txt"
    config = ExperimentConfig(config_file=config_file) if config_file.exists() else ExperimentConfig()
    
    logger.info("=" * 70)
    logger.info("Generating cork-1-line instances with battery-java-aligned config")
    logger.info("=" * 70)
    logger.info(f"Config: cmax={config.cmax}, cmin={config.cmin}, "
                f"charging_rate={config.charging_rate}, dt_max={config.dt_max}")
    
    # Output directory
    battery_dir = project_root / "experiments" / "instances" / "Battery-Fixed"
    battery_dir.mkdir(parents=True, exist_ok=True)

    json_dir = project_root / "external" / "jits2022" / "Code" / "data" / "cork-1-line"
    
    # Load the exact JITS distance table used by the cork-1-line data.
    logger.info("\nLoading distances data...")
    distances_dict, _ = DataLoader.load_distances(json_dir)
    logger.info(f"Loaded {len(distances_dict)} distance entries")
    
    # Convert each variant
    successful = 0
    failed = 0
    
    for variant in VARIANTS:
        json_file = json_dir / f"buses_input_{variant}.json"
        if not json_file.exists():
            logger.warning(f"JSON file not found: {json_file.name}")
            failed += 1
            continue
        
        dzn_file = battery_dir / f"cork-1-line_Battery-Fixed{variant}.dzn"
        
        logger.info(f"\n[{VARIANTS.index(variant) + 1}/{len(VARIANTS)}] Converting {json_file.name}...")
        
        success, message = ConverterEngine.convert_json_to_dzn(
            json_file=json_file,
            output_file=dzn_file,
            variant_name=variant,
            config=config,
            distances_dict=distances_dict,
            output_format="java"
        )
        
        if success:
            logger.info(f"✓ {dzn_file.name}: {message}")
            successful += 1
        else:
            logger.error(f"✗ {dzn_file.name}: {message}")
            failed += 1
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Conversion complete: {successful} successful, {failed} failed")
    logger.info(f"Output directory: {battery_dir}")
    logger.info("=" * 70)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
