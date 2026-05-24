"""
================================================================================
Configuration Module - CLP Instance Generator
================================================================================
Central configuration for the entire generator system.
Author: AVISPA Research Team
Version: 2.1.0
================================================================================
"""

class Config:
    """Centralized configuration for instance generation"""

    def __init__(self):
        # =========================================================================
        # BATTERY PARAMETERS (scaled ×10)
        # =========================================================================
        self.Cmax = 1000          # 100 kWh max capacity
        self.Cmin = 200           # 20 kWh min reserve
        self.USABLE_CAPACITY = self.Cmax - self.Cmin  # 80 kWh usable
        self.alpha = 100          # 10 kWh/min charging rate

        # =========================================================================
        # TIME PARAMETERS (scaled ×10)
        # =========================================================================
        self.mu = 50              # 5 min max delay
        self.SM = 10              # 1 min safety margin
        self.psi = 10             # 1 min minimum charging time
        self.beta = 100           # 10 min maximum charging time
        self.M = 10000            # Big-M constant

        # =========================================================================
        # GENERATION PARAMETERS (derived from constraint analysis)
        # =========================================================================
        # Energy consumption bounds (scaled ×10)
        self.MIN_CONSUMPTION_PER_STOP = 100    # 10 kWh
        self.MAX_CONSUMPTION_PER_STOP = 300    # 30 kWh
        self.OPTIMAL_CONSUMPTION_PER_STOP = 180  # 18 kWh

        # Travel times (scaled ×10)
        self.MIN_TRAVEL_TIME = 60      # 6 min
        self.MAX_TRAVEL_TIME = 300     # 30 min
        self.OPTIMAL_TRAVEL_TIME = 120 # 12 min

        # Route constraints
        self.MIN_STOPS_PER_BUS = 4
        self.MAX_STOPS_PER_BUS = 10

        # Generation strategy
        self.TARGET_CONSUMPTION_FACTOR_MIN = 1.2  # Ensure charging is needed
        self.TARGET_CONSUMPTION_FACTOR_MAX = 1.55  # Feasibility bound (from working examples)

        # =========================================================================
        # VALIDATION PARAMETERS
        # =========================================================================
        self.SOLVER_TIMEOUT = 600000  # 600 seconds = 10 minutes (milliseconds)
        self.VALIDATION_ATTEMPTS = 1000  # No limit on retries until SAT found

        # =========================================================================
        # UI COLORS
        # =========================================================================
        self.COLOR_DARK_BLUE = "#1e3a5f"
        self.COLOR_LIGHT_BLUE = "#4a90e2"
        self.COLOR_WHITE = "#ffffff"
        self.COLOR_LIGHT_GRAY = "#f5f5f5"
        self.COLOR_GRAY = "#cccccc"
        self.COLOR_SUCCESS = "#28a745"
        self.COLOR_ERROR = "#dc3545"
        self.COLOR_WARNING = "#ffc107"
        self.COLOR_INFO = "#17a2b8"
