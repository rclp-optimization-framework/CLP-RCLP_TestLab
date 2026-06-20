"""
Theme Persistence - Cross-session and cross-tool theme preference management

Maintains user theme preferences (dark/light mode) across multiple tool launches
and sessions. Provides a centralized configuration file at the project root.

Features:
- Persistent theme storage in JSON format
- Default fallback to dark mode if config missing or invalid
- Robust error handling for file I/O operations
- Cross-platform path handling

Usage:
    from core.shared.theme_persistence import ThemePersistence

    # Get saved theme or default
    current_theme = ThemePersistence.get_theme()

    # Save new theme preference
    ThemePersistence.set_theme("light")

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
"""

import json
from pathlib import Path
from typing import Literal

class ThemePersistence:
    """
    Manages theme preference persistence across sessions.

    Stores and retrieves the user's theme choice (dark or light mode) in a JSON
    configuration file. Handles file I/O errors gracefully, always providing a
    valid theme value.

    Config file location: <project_root>/.theme_config.json
    """

    CONFIG_FILE = Path(__file__).parent.parent.parent / ".theme_config.json"
    DEFAULT_THEME = "dark"

    @classmethod
    def get_theme(cls) -> Literal["dark", "light"]:
        """
        Get saved theme preference or return default.

        Returns:
            str: Theme preference ("dark" or "light"), defaults to "dark" if:
                - Config file doesn't exist
                - Config file is malformed
                - Saved theme is invalid
        """
        try:
            if cls.CONFIG_FILE.exists():
                with open(cls.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    theme = config.get("theme", cls.DEFAULT_THEME)
                    if theme in ("dark", "light"):
                        return theme
        except (json.JSONDecodeError, IOError):
            pass
        return cls.DEFAULT_THEME

    @classmethod
    def set_theme(cls, theme: Literal["dark", "light"]) -> None:
        """
        Save theme preference to configuration file.

        Args:
            theme: Theme to save ("dark" or "light")

        Note:
            Invalid theme values are silently ignored. Errors during file I/O
            are logged but not raised to allow graceful degradation.
        """
        if theme not in ("dark", "light"):
            return

        try:
            config = {}
            if cls.CONFIG_FILE.exists():
                try:
                    with open(cls.CONFIG_FILE, 'r') as f:
                        config = json.load(f)
                except (json.JSONDecodeError, IOError):
                    config = {}

            config["theme"] = theme

            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass
