#!/usr/bin/env python3
"""
Test script to verify Java-compatible converter mode with cork-1-line data.
Tests that config is loaded and correct parameters are generated.
"""

from pathlib import Path
import logging
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.experiment_config import ExperimentConfig
from core.converter.core.data_loader import DataLoader

# Setup logging with DEBUG level to see all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Also enable debug for converter engine
logging.getLogger('core.converter.core.converter_engine').setLevel(logging.DEBUG)

def test_cork_1_line_conversion():
    """Test conversion of cork-1-line data with Java-compatible mode."""
    
    # Paths
    workspace_root = ROOT
    jits_data_dir = workspace_root / "external" / "jits2022" / "Code" / "data"
    cork_1_line_dir = jits_data_dir / "cork-1-line"
    
    output_dir = workspace_root / "experiments" / "instances" / "Battery-Final"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Workspace root: {workspace_root}")
    logger.info(f"Cork-1-line directory: {cork_1_line_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    # Check that input data exists
    if not cork_1_line_dir.exists():
        logger.error(f"Cork-1-line directory not found: {cork_1_line_dir}")
        return False
    
    # Find JSON files in cork-1-line
    json_files = list(cork_1_line_dir.glob("buses_input_*.json"))
    logger.info(f"Found {len(json_files)} JSON files in cork-1-line")
    if not json_files:
        logger.error("No buses_input_*.json files found")
        return False
    
    # Find experiment config file
    logger.info(f"Searching for experiment_parameters file...")
    config_file = cork_1_line_dir.parent / "experiment_parameters_cork1_20_0.txt"
    
    if not config_file.exists():
        logger.warning("Config file not found - will use defaults")
        config = None
    else:
        try:
            config = ExperimentConfig(config_file=config_file)
            logger.info(f"Loaded config: Cmax={config.cmax}, Cmin={config.cmin}, "
                       f"alpha={config.alpha}, charging_rate={config.charging_rate}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            config = None
    
    # Load distances
    logger.info("Loading distances from CSV...")
    try:
        distances_dict = DataLoader.load_distances(
            stations_file=cork_1_line_dir / "stations_input.csv",
            distances_file=cork_1_line_dir / "distances_input.csv"
        )
        logger.info(f"Loaded {len(distances_dict)} distance entries")
    except Exception as e:
        logger.error(f"Error loading distances: {e}")
        distances_dict = {}
    
    # Convert JSON files
    logger.info(f"\n{'='*80}")
    logger.info(f"Starting conversion with Java-compatible mode")
    logger.info(f"Config object: {config}")
    if config:
        logger.info(f"  Cmax={config.cmax}, Cmin={config.cmin}, charging_rate={config.charging_rate}")
    logger.info(f"{'='*80}\n")
    
    success_count, failure_count, messages = ConverterEngine.batch_convert_files(
        json_files=json_files,
        output_dir=output_dir,
        source_dir_name="cork-1-line",
        config=config,
        distances_dict=distances_dict,
        output_format="java"
    )
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Conversion Results:")
    logger.info(f"  Success: {success_count}")
    logger.info(f"  Failures: {failure_count}")
    logger.info(f"  Messages: {messages}")
    logger.info(f"{'='*80}\n")
    
    # Verify generated DZN file
    expected_dzn = output_dir / "cork-1-line" / "cork-1-line_Battery-Final20_0.dzn"
    if expected_dzn.exists():
        logger.info(f"Generated DZN file: {expected_dzn}")
        
        # Read and display header
        with open(expected_dzn, 'r') as f:
            lines = f.readlines()
        
        # Find energy parameters section
        logger.info(f"\nGenerated DZN Header Parameters:")
        in_energy_section = False
        for i, line in enumerate(lines[:100]):  # Check first 100 lines
            if "Energy Parameters" in line:
                in_energy_section = True
            if in_energy_section:
                if line.strip() and not line.startswith("%"):
                    print(f"  {line.rstrip()}")
                if "Problem Dimensions" in line:
                    break
        
        # Expected values for cork-1-line (from battery-java-aligned reference)
        logger.info(f"\nExpected values (battery-java-aligned reference):")
        logger.info(f"  Cmax = 120000")
        logger.info(f"  Cmin = 15000")
        logger.info(f"  alpha = 167")
        logger.info(f"  beta = 486")
        
        # Check if parameters match
        content = ''.join(lines)
        has_correct_params = (
            "Cmax = 120000" in content and
            "Cmin = 15000" in content and
            "alpha = 167" in content and
            "beta = 486" in content
        )
        
        if has_correct_params:
            logger.info(f"\n✅ SUCCESS: Generated DZN has correct Java-compatible parameters!")
            return True
        else:
            logger.warning(f"\n⚠️  WARNING: Generated DZN parameters may not match reference values")
            return False
    else:
        logger.error(f"Expected DZN file not found: {expected_dzn}")
        return False

if __name__ == "__main__":
    success = test_cork_1_line_conversion()
    exit(0 if success else 1)
