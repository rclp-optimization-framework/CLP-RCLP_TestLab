#!/usr/bin/env python3
"""
Generate the Battery-Last cork-1-line battery using the core converter.

This script writes the 12 cork-1-line instances directly into
experiments/instances/Battery-Last so the runner can discover them
without needing to recurse into a subdirectory.
"""

import sys
import logging
from pathlib import Path


project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.converter.core.data_loader import DataLoader
from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.experiment_config import ExperimentConfig


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


VARIANTS = [
    "20_0", "20_5", "20_10", "20_20",
    "30_0", "30_5", "30_10", "30_20",
    "40_0", "40_5", "40_10", "40_20",
]


def main() -> int:
    config_file = project_root / "external" / "jits2022" / "Code" / "data" / "experiment_parameters_cork1_20_0.txt"
    config = ExperimentConfig(config_file=config_file) if config_file.exists() else ExperimentConfig()

    json_dir = project_root / "external" / "jits2022" / "Code" / "data" / "cork-1-line"
    output_dir = project_root / "experiments" / "instances" / "Battery-Last"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 70)
    logger.info("Generating Battery-Last with core converter")
    logger.info("=" * 70)
    logger.info(
        "Config: cmax=%s, cmin=%s, charging_rate=%s, dt_max=%s",
        config.cmax,
        config.cmin,
        config.charging_rate,
        config.dt_max,
    )

    logger.info("\nLoading distances data...")
    distances_dict, _ = DataLoader.load_distances(json_dir)
    logger.info("Loaded %s distance entries", len(distances_dict))

    successful = 0
    failed = 0

    for index, variant in enumerate(VARIANTS, start=1):
        json_file = json_dir / f"buses_input_{variant}.json"
        if not json_file.exists():
            logger.warning("JSON file not found: %s", json_file.name)
            failed += 1
            continue

        dzn_file = output_dir / f"cork-1-line_Battery-Last{variant}.dzn"

        logger.info("\n[%s/%s] Converting %s...", index, len(VARIANTS), json_file.name)

        success, message = ConverterEngine.convert_json_to_dzn(
            json_file=json_file,
            output_file=dzn_file,
            variant_name=variant,
            config=config,
            distances_dict=distances_dict,
            output_format="java",
        )

        if success:
            logger.info("✓ %s: %s", dzn_file.name, message)
            successful += 1
        else:
            logger.error("✗ %s: %s", dzn_file.name, message)
            failed += 1

    logger.info("\n" + "=" * 70)
    logger.info("Conversion complete: %s successful, %s failed", successful, failed)
    logger.info("Output directory: %s", output_dir)
    logger.info("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())