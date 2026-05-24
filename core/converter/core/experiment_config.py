"""
Experiment Configuration Module

Loads and manages experiment-level parameters from JITS2022 format config files.
Ensures converter uses the same parameters as the original JITS2022 solver.

Format: JITS2022 experiment_parameters.txt compatible
Author: AVISPA Research Team
Date: April 2026
"""

import logging
from pathlib import Path
from typing import Dict, Optional
import configparser
import json

logger = logging.getLogger(__name__)


class ExperimentConfig:
    """Load and manage experiment parameters from configuration files."""

    # Default values (in case config is missing)
    DEFAULTS = {
        'cmax': 120.0,          # Battery capacity (kWh)
        'cmin': 15.0,           # Minimum reserve (kWh)
        'alpha': 10.0,          # Fast charging rate (kWh/min)
        'mu': 4.0,              # Maximum delay allowed (min)
        'sm': 1.0,              # Safety margin (min)
        'psi': 1.0,             # Minimum charging time (min)
        'beta': 486.0,          # Maximum charging time (reference-aligned output)
        'model_speed': 30,      # Minimum speed for model (km/h)
        'instance_speed': 50,   # Instance speed parameter (km/h)
        'rest_time': 10,        # Rest duration (min)
        'dt_max': 4,            # Maximum delay tolerance (min)
        'min_ct': 1,            # Minimum change time (min)
        'charging_rate': 10,    # Charging rate (kWh/min)
        'scale': 50,            # Scaling factor for integer conversion (increased from 10 to minimize distance precision loss)
    }

    def __init__(self, config_file: Optional[Path] = None, **kwargs):
        """
        Initialize configuration from file or defaults.

        Args:
            config_file: Path to config file (INI or JITS2022 format)
            **kwargs: Override parameters as keyword arguments
        """
        self.params = self.DEFAULTS.copy()

        if config_file and config_file.exists():
            self._load_from_file(config_file)

        # Override with kwargs
        self.params.update({k: v for k, v in kwargs.items() if k in self.params})

        logger.info(f"Config loaded: cmax={self.cmax}, model_speed={self.model_speed}, rest_time={self.rest_time}")

    def _load_from_file(self, config_file: Path) -> None:
        """
        Load parameters from configuration file.

        Supports both INI format and JITS2022 format.

        Args:
            config_file: Path to config file
        """
        try:
            if config_file.suffix.lower() == '.ini':
                self._load_ini(config_file)
            elif config_file.suffix.lower() == '.txt':
                self._load_jits2022_format(config_file)
            elif config_file.suffix.lower() == '.json':
                self._load_json(config_file)
            else:
                logger.warning(f"Unknown config format: {config_file.suffix}. Using defaults.")
        except Exception as e:
            logger.error(f"Error loading config from {config_file}: {e}. Using defaults.")

    def _load_ini(self, config_file: Path) -> None:
        """Load INI format configuration file."""
        config = configparser.ConfigParser()
        config.read(config_file)

        if 'experiment' in config:
            for key, value in config['experiment'].items():
                if key in self.params:
                    try:
                        # Try to parse as int first, then float
                        if isinstance(self.DEFAULTS[key], int):
                            self.params[key] = int(value)
                        else:
                            self.params[key] = float(value)
                    except ValueError:
                        logger.warning(f"Could not parse {key}={value}")

    def _load_jits2022_format(self, config_file: Path) -> None:
        """
        Load JITS2022 format experiment_parameters.txt.

        Format:
            input_folders
            execution_time
            solving_method
            cMaxes: val1,val2,...
            minSpeeds: val1,val2,...
            insSpeeds: val1,val2,...
            restTimes: val1,val2,...
            dtTimes: val1,val2,...
            ...
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                raw_lines = f.readlines()

            # Remove inline comments and blank lines.
            # JITS files frequently use: "120000 # Capacity ...".
            lines = []
            for raw in raw_lines:
                line = raw.strip()
                if not line:
                    continue
                if '#' in line:
                    line = line.split('#', 1)[0].strip()
                if line:
                    lines.append(line)

            # Expected order of parameter arrays (after first 3 lines)
            param_names = [
                'cmax', 'model_speed', 'instance_speed', 'rest_time', 'dt_max',
                'laura', 'arriving_without_charging', 'robust', 'back_to_primary',
                'min_ct', 'objective', 'threads', 'cmin', 'sm', 'charging_rate',
                'warm_start', 'solving_method'
            ]

            # Skip first 3 metadata lines (input folders, exec time, method)
            if len(lines) > 3:
                for i, param_name in enumerate(param_names):
                    if i + 3 < len(lines):
                        values_str = lines[i + 3].split(',')[0].strip()  # Take first value when list-like
                        try:
                            if param_name in self.params:
                                if param_name in {'cmax', 'cmin'}:
                                    # JITS2022 experiment files store battery values in mts units.
                                    # Normalize to internal kWh-style units so to_scaled_dict() can
                                    # apply the single required ×1000 conversion exactly once.
                                    self.params[param_name] = float(values_str) / 1000.0
                                elif isinstance(self.DEFAULTS[param_name], int):
                                    self.params[param_name] = int(values_str)
                                else:
                                    self.params[param_name] = float(values_str)
                        except ValueError:
                            logger.warning(f"Could not parse {param_name}={values_str}")
        except Exception as e:
            logger.error(f"Error loading JITS2022 format: {e}")

    def _load_json(self, config_file: Path) -> None:
        """Load JSON format configuration file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for key, value in data.items():
                if key in self.params:
                    self.params[key] = value
        except Exception as e:
            logger.error(f"Error loading JSON config: {e}")

    @property
    def cmax(self) -> float:
        """Battery capacity (kWh)."""
        return self.params['cmax']

    @property
    def cmin(self) -> float:
        """Minimum reserve (kWh)."""
        return self.params['cmin']

    @property
    def alpha(self) -> float:
        """Fast charging rate (kWh/min)."""
        return self.params['alpha']

    @property
    def mu(self) -> float:
        """Maximum delay allowed (min)."""
        return self.params['mu']

    @property
    def sm(self) -> float:
        """Safety margin (min)."""
        return self.params['sm']

    @property
    def psi(self) -> float:
        """Minimum charging time (min)."""
        return self.params['psi']

    @property
    def beta(self) -> float:
        """Maximum charging time (min)."""
        return self.params['beta']

    @property
    def model_speed(self) -> int:
        """Minimum speed for model (km/h)."""
        return int(self.params['model_speed'])

    @property
    def instance_speed(self) -> int:
        """Instance speed parameter (km/h)."""
        return int(self.params['instance_speed'])

    @property
    def rest_time(self) -> int:
        """Rest duration (min)."""
        return int(self.params['rest_time'])

    @property
    def dt_max(self) -> int:
        """Maximum delay tolerance (min)."""
        return int(self.params['dt_max'])

    @property
    def min_ct(self) -> int:
        """Minimum change time (min)."""
        return int(self.params['min_ct'])

    @property
    def charging_rate(self) -> int:
        """Charging rate (kWh/min)."""
        return int(self.params['charging_rate'])

    @property
    def scale(self) -> int:
        """Scaling factor for integer conversion."""
        return int(self.params['scale'])

    def to_dict(self) -> Dict[str, float]:
        """Return all parameters as dictionary."""
        return self.params.copy()

    def to_scaled_dict(self) -> Dict[str, int]:
        """
        Return all parameters with DIFFERENTIATED scaling for precision and MiniZinc compatibility.

        Scaling strategy:
        - Energy parameters (Cmax, Cmin, D): Scaled by 1000
          → 1 unit = 0.001 kWh (0.1% precision, minimal error propagation)
          → Eliminates truncation errors from distance-based energy calculations
        - Charging rate (alpha): Scaled by 1000/60 (convert kWh/min to units/second)
          → Formula: (charging_rate_kWh_per_min * 1000) / 60
          → Matches Java convention for charging calculations
        - Time parameters (mu, SM, psi, beta, T, tau_bi): NO scaling (SCALE_TIME=1)
          → Keep as native minutes (avoids excessive Big-M, MiniZinc compatible)

        Rationale for SCALE_ENERGY=1000:
        - Previous scale of 50 caused ~10% error in energy calculations
        - Error accumulates across multiple buses and stops in routing models
        - Higher scale reduces truncation (floor → round at higher precision)
        - 1000 chosen to maintain integer arithmetic while minimizing precision loss
        - All energy constraints remain feasible with scaled values

        This separates concerns:
        - Energy domain: High precision (1000×) for accurate power calculations
        - Time domain: Native units (1×) for schedule compatibility
        - No inflation of Big-M or other multipliers beyond necessity
        """
        SCALE_ENERGY = 1000  # For energy: 1 unit = 0.001 kWh (0.1% precision)

        return {
            'cmax': round(self.cmax * SCALE_ENERGY),           # 100 kWh -> 100000
            'cmin': round(self.cmin * SCALE_ENERGY),           # 20 kWh -> 20000
            'alpha': round((self.alpha * SCALE_ENERGY) / 60),  # 10 kWh/min -> (10*1000)/60 = 167 units/second
            'mu': int(self.mu),                                # 5 min -> 5 (no scaling)
            'sm': int(self.sm),                                # 1 min -> 1 (no scaling)
            'psi': int(self.psi),                              # 1 min -> 1 (no scaling)
            'beta': int(round(self.beta)),                     # 486.0 -> 486 (already reference-aligned)
            'scale_energy': SCALE_ENERGY,
            'scale_time': 1,  # Time is not scaled
        }
