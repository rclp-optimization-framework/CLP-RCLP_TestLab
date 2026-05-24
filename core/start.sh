#!/bin/bash
# CLP-RCLP System Entry Point (Bash version)
#
# Launches the System Center (Orchestrator) for accessing all tools.
# This is the recommended entry point for using the CLP-RCLP framework.
#
# Usage:
#     ./start.sh
#     or
#     bash start.sh
#
# Authors: AVISPA Research Team
# Date: April 2026

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================================================"
echo "CLP-RCLP System Center v2.1.0"
echo "========================================================================"
echo ""
echo "Launching System Center interface..."
echo ""
echo "Access all tools from the central hub:"
echo "  - Data Converter: Convert JSON to MiniZinc format"
echo "  - Instance Generator: Create test instances"
echo "  - Test Runner: Execute optimization tests"
echo ""
echo "========================================================================"
echo ""

# Run the orchestrator from the core directory
cd "$SCRIPT_DIR"
python3 start.py

# If python3 doesn't work, try python
if [ $? -ne 0 ]; then
    echo "Trying with 'python' command..."
    python start.py
fi
