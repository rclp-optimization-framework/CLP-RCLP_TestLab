#!/usr/bin/env python3
"""
CLP-RCLP System Entry Point

Launches the System Center (Orchestrator) for accessing all tools.
This is the recommended entry point for using the CLP-RCLP framework.

Usage:
    python start.py
    or
    ./start.py

Authors: AVISPA Research Team
Date: April 2026
"""

import sys
from pathlib import Path

# Add project root to path (parent of core directory)
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from core.orchestration.orchestrator import launch_orchestrator

    print("=" * 70)
    print("CLP-RCLP System Center v2.1.0")
    print("=" * 70)
    print("\nLaunching System Center interface...")
    print("\nAccess all tools from the central hub:")
    print("  - Data Converter: Convert JSON to MiniZinc format")
    print("  - Instance Generator: Create test instances")
    print("  - Test Runner: Execute optimization tests")
    print("\n" + "=" * 70)

    launch_orchestrator()

except ImportError as e:
    print(f"Error: Could not import orchestrator module: {e}", file=sys.stderr)
    print("\nMake sure you're running from the repository root directory.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error launching System Center: {e}", file=sys.stderr)
    sys.exit(1)
