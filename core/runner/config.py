"""
Runner Configuration - UI Colors and Constants

Professional color palette for the Runner interface.
"""

class RunnerConfig:
    """Central configuration for Runner UI and execution."""

    # UI Colors - Professional palette
    COLOR_GRAY = "#CCCCCC"           # Light gray background
    COLOR_DARK_BLUE = "#1E3A5F"      # Deep blue accents
    COLOR_BLACK = "#000000"          # Text and borders
    COLOR_WHITE = "#FFFFFF"          # Contrast/highlights

    # Derived shades for better aesthetics
    COLOR_LIGHT_GRAY = "#E8E8E8"     # Slightly lighter gray
    COLOR_MEDIUM_BLUE = "#2C5AA0"    # Medium blue for hover/active
    COLOR_LIGHT_BLUE = "#E8EEF5"     # Very light blue for backgrounds

    # Text colors
    COLOR_TEXT_PRIMARY = "#000000"   # Black text
    COLOR_TEXT_SECONDARY = "#404040" # Dark gray text

    # Status colors
    COLOR_SUCCESS = "#2E7D32"        # Green for success
    COLOR_ERROR = "#C62828"          # Red for error
    COLOR_WARNING = "#F57C00"        # Orange for warning
    COLOR_INFO = "#1565C0"           # Blue for info

    # Font configuration
    FONT_FAMILY = "Segoe UI" if __import__('platform').system() == "Windows" else "Helvetica"
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_HEADER = 12
    FONT_SIZE_TITLE = 14

    # Paths - Resolved dynamically from project root at runtime
    # Format: "battery-name" → resolved as "experiments/instances/battery-name"
    DATA_DIRECTORIES = [
        "battery-own",
        "battery-generated",
        "battery-project-integer",
        "battery-project-variant"
    ]
    DATA_BASE_PATH = "experiments/instances"  # Root directory for all test batteries

    MODELS = ["clp", "rclp"]

    # MiniZinc
    SOLVER = "chuffed"
    TIMEOUT_SECONDS = 300  # 5 minutes per test

    # CPLEX defaults used by the runner when the CPLEX backend is selected.
    # These mirror the Java reference runs found in external/jits2022 logs.
    CPLEX_PARALLEL = 4
    CPLEX_RANDOM_SEED = 0
    CPLEX_MIPFOCUS = 0
    CPLEX_GENERATE_PARAM_FILE = True
