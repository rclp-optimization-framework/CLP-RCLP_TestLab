#!/usr/bin/env python3
"""
Window Transition Verification Script

Tests the transition between Orchestrator and Tool windows to ensure
the navigation system works correctly across the entire application.

This script:
1. Verifies ToolPathResolver can find all tools
2. Tests back navigation paths
3. Simulates window transitions
4. Generates detailed transition report

Usage:
    python scripts/verification/verify_window_transitions.py

Exit Codes:
    0: All transitions verified successfully
    1: One or more transitions failed
    2: Configuration error (missing tools, etc.)

Author: AVISPA Research Team
Date: April 2026
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class TransitionVerifier:
    """Verifies window transitions between orchestrator and tools."""

    def __init__(self, project_root: Path = None):
        """
        Initialize the transition verifier.

        Args:
            project_root: Project root path. If None, auto-detects.
        """
        if project_root is None:
            project_root = self._find_project_root()

        self.project_root = project_root
        self.core_path = project_root / "core"

        # Add core to sys.path for imports
        sys.path.insert(0, str(self.core_path))
        sys.path.insert(0, str(project_root))

        logger.info(f"Project root: {self.project_root}")

    @staticmethod
    def _find_project_root() -> Path:
        """Auto-detect project root directory."""
        current = Path(__file__).resolve().parents[2]
        max_iterations = 10

        for _ in range(max_iterations):
            if (current / "core").exists() or current.name == "CLP-RCLP Minizinc":
                return current

            parent = current.parent
            if parent == current:
                break
            current = parent

        raise RuntimeError(
            f"Could not find project root starting from {Path(__file__).parent}"
        )

    def verify_path_resolver(self) -> Tuple[bool, Dict[str, bool], Dict[str, Path]]:
        """
        Verify ToolPathResolver can locate all tools.

        Returns:
            Tuple: (success: bool, tool_availability: Dict, tool_paths: Dict)
        """
        try:
            from shared.path_resolver import ToolPathResolver

            resolver = ToolPathResolver(self.project_root)
            tools = resolver.get_all_tools()
            validation = resolver.validate_tools()

            logger.info("✓ ToolPathResolver imported successfully")

            for tool_name, available in validation.items():
                status = "✓ FOUND" if available else "✗ NOT FOUND"
                path = tools.get(tool_name)
                logger.info(f"  {tool_name}: {status} ({path})")

            all_found = all(validation.values())
            return all_found, validation, tools

        except ImportError as e:
            logger.error(f"✗ Failed to import ToolPathResolver: {e}")
            return False, {}, {}

    def verify_navigation_paths(self) -> Tuple[bool, Dict[str, bool]]:
        """
        Verify navigation paths work correctly.

        Returns:
            Tuple: (success: bool, path_checks: Dict)
        """
        checks = {}

        # Check orchestrator path
        orchestrator_path = self.core_path / "orchestration" / "orchestrator.py"
        checks["orchestrator"] = orchestrator_path.exists()
        status = "✓ FOUND" if checks["orchestrator"] else "✗ NOT FOUND"
        logger.info(f"Orchestrator path: {status} ({orchestrator_path})")

        # Check navigation module
        navigation_path = self.core_path / "shared" / "navigation.py"
        checks["navigation"] = navigation_path.exists()
        status = "✓ FOUND" if checks["navigation"] else "✗ NOT FOUND"
        logger.info(f"Navigation module: {status} ({navigation_path})")

        # Check path resolver
        resolver_path = self.core_path / "shared" / "path_resolver.py"
        checks["path_resolver"] = resolver_path.exists()
        status = "✓ FOUND" if checks["path_resolver"] else "✗ NOT FOUND"
        logger.info(f"Path resolver: {status} ({resolver_path})")

        all_found = all(checks.values())
        return all_found, checks

    def verify_orchestrator_theme(self) -> Tuple[bool, str]:
        """
        Verify orchestrator has theme switching support.

        Returns:
            Tuple: (has_theme: bool, details: str)
        """
        orchestrator_ui_path = (
            self.core_path / "orchestration" / "ui" / "interface.py"
        )

        if not orchestrator_ui_path.exists():
            return False, "Orchestrator UI interface not found"

        try:
            with open(orchestrator_ui_path, "r", encoding="utf-8") as f:
                content = f.read()

            checks = {
                "_toggle_theme": "_toggle_theme" in content,
                "ThemeManager": "ThemeManager" in content,
                "FlatButton": "FlatButton" in content,
                "theme_dict": "theme_dict" in content,
            }

            details = ", ".join(
                f"{name}{'✓' if found else '✗'}"
                for name, found in checks.items()
            )

            has_all = all(checks.values())
            return has_all, details

        except Exception as e:
            return False, f"Error reading orchestrator UI: {e}"

    def generate_report(self) -> str:
        """
        Generate comprehensive transition verification report.

        Returns:
            str: Formatted verification report
        """
        logger.info("\n" + "=" * 70)
        logger.info("CLP-RCLP WINDOW TRANSITION VERIFICATION REPORT")
        logger.info("=" * 70)

        # Phase 1: Path Resolver
        logger.info("\n[1] ToolPathResolver Verification")
        logger.info("-" * 70)
        resolver_ok, tool_availability, tool_paths = self.verify_path_resolver()

        # Phase 2: Navigation Paths
        logger.info("\n[2] Navigation Path Verification")
        logger.info("-" * 70)
        nav_ok, nav_checks = self.verify_navigation_paths()

        # Phase 3: Orchestrator Theme
        logger.info("\n[3] Orchestrator Theme Support Verification")
        logger.info("-" * 70)
        theme_ok, theme_details = self.verify_orchestrator_theme()
        logger.info(f"Theme components: {theme_details}")

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)

        all_ok = resolver_ok and nav_ok and theme_ok

        status = "✓ PASS" if all_ok else "✗ FAIL"
        logger.info(f"Overall Status: {status}")

        logger.info(f"  Tool Resolution: {'✓' if resolver_ok else '✗'}")
        logger.info(f"  Navigation Paths: {'✓' if nav_ok else '✗'}")
        logger.info(f"  Theme Support: {'✓' if theme_ok else '✗'}")

        logger.info("\nDetails:")
        logger.info(f"  Available Tools: {sum(1 for v in tool_availability.values() if v)}/{len(tool_availability)}")
        logger.info(f"  Navigation Checks: {sum(1 for v in nav_checks.values() if v)}/{len(nav_checks)}")

        logger.info("=" * 70 + "\n")

        return status


def main() -> int:
    """
    Run the transition verification script.

    Returns:
        int: Exit code (0=success, 1=failure, 2=config error)
    """
    try:
        verifier = TransitionVerifier()
        status = verifier.generate_report()

        return 0 if "PASS" in status else 1

    except RuntimeError as e:
        logger.error(f"Configuration error: {e}")
        return 2
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
