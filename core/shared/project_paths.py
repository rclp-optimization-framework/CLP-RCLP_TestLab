"""
Project Paths - Centralized path resolution for all modules

Provides a single source of truth for path resolution across the project.
Ensures all modules resolve paths relative to the project root correctly.

Features:
- Automatic project root detection
- Centralized path definitions
- Cross-platform path handling
- Type-safe path operations

Usage:
    from core.shared.project_paths import ProjectPaths

    paths = ProjectPaths()
    input_path = paths.jits_data_dir
    output_path = paths.battery_generated_dir

Author: AVISPA Research Team
Date: April 2026
"""

from pathlib import Path
from typing import Optional


class ProjectPaths:
    """
    Centralized project path management.

    Resolves all paths relative to the project root directory.
    Project root is automatically detected by finding the directory
    containing 'core/', 'experiments/', and 'external/' subdirectories.
    """

    _project_root: Optional[Path] = None

    @classmethod
    def _find_project_root(cls) -> Path:
        """
        Auto-detect project root directory.

        Searches upward from this file's location until it finds
        a directory containing the 'core' subdirectory.

        Returns:
            Path: Project root directory
        """
        # Start from this file's location
        current = Path(__file__).parent.parent.parent.absolute()
        max_iterations = 10

        for _ in range(max_iterations):
            # Check if current directory has 'core', 'experiments', 'external'
            if (current / "core").exists() and (current / "experiments").exists():
                return current

            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent

        # Fallback: return calculated path
        return Path(__file__).parent.parent.parent.absolute()

    @classmethod
    def get_project_root(cls) -> Path:
        """
        Get the project root path.

        Returns:
            Path: Absolute path to project root
        """
        if cls._project_root is None:
            cls._project_root = cls._find_project_root()
        return cls._project_root

    @classmethod
    def set_project_root(cls, path: Path) -> None:
        """
        Override project root (for testing).

        Args:
            path: Project root path
        """
        cls._project_root = Path(path).absolute()

    # =========================================================================
    # INPUT PATHS
    # =========================================================================

    @classmethod
    def jits_data_dir(cls) -> Path:
        """
        JITS2022 data directory (input for converter).

        Location: external/jits2022/Code/data (at project root)
        """
        return cls.get_project_root() / "external" / "jits2022" / "Code" / "data"

    # =========================================================================
    # OUTPUT PATHS
    # =========================================================================

    @classmethod
    def experiments_dir(cls) -> Path:
        """
        Experiments directory (at project root).

        Contains:
        - instances/ (test batteries and instances)
        - results/ (execution results)
        """
        return cls.get_project_root() / "experiments"

    @classmethod
    def instances_dir(cls) -> Path:
        """
        Test instances directory.

        Location: experiments/instances (at project root)
        Contains all battery directories
        """
        return cls.get_project_root() / "experiments" / "instances"

    @classmethod
    def battery_generated_dir(cls) -> Path:
        """
        Generated batteries directory (output from generator).

        Location: experiments/instances/battery-generated (at project root)
        """
        return cls.get_project_root() / "experiments" / "instances" / "battery-generated"

    @classmethod
    def results_dir(cls) -> Path:
        """
        Results directory (output from runner).

        Location: experiments/results (at project root)
        """
        return cls.get_project_root() / "experiments" / "results"

    # =========================================================================
    # MODEL PATHS
    # =========================================================================

    @classmethod
    def models_dir(cls) -> Path:
        """
        Models directory.

        Location: core/models (at project root)
        Contains .mzn files
        """
        return cls.get_project_root() / "core" / "models"

    @classmethod
    def clp_model_path(cls, precision: str = "integer") -> Path:
        """CLP model file path."""
        if precision == "floating":
            return cls.models_dir() / "clp_model_float.mzn"
        return cls.models_dir() / "clp_model.mzn"

    @classmethod
    def rclp_model_path(cls, precision: str = "integer") -> Path:
        """RCLP model file path."""
        if precision == "floating":
            return cls.models_dir() / "rclp_model_float.mzn"
        return cls.models_dir() / "rclp_model.mzn"

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    @classmethod
    def get_battery_dir(cls, battery_name: str) -> Path:
        """
        Get path to a specific battery directory.

        Args:
            battery_name: Battery directory name (e.g., 'battery-own')

        Returns:
            Path: Absolute path to battery directory
        """
        return cls.instances_dir() / battery_name

    @classmethod
    def validate_paths(cls) -> dict:
        """
        Validate that all critical paths exist.

        Returns:
            dict: Status of each path
        """
        return {
            "jits_data_dir": cls.jits_data_dir().exists(),
            "instances_dir": cls.instances_dir().exists(),
            "battery_generated_dir": cls.battery_generated_dir().parent.exists(),
            "results_dir": cls.results_dir().parent.exists(),
            "models_dir": cls.models_dir().exists(),
        }
