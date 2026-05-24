# Orchestrator - System Center Interface

Professional central hub for accessing all CLP-RCLP tools.

## Overview

The Orchestrator (System Center) provides a unified, professional entry point to the CLP-RCLP framework. From here, you can access:

- **Data Converter**: Convert JSON schedules to MiniZinc DZN format
- **Instance Generator**: Create test instances with customizable parameters
- **Test Runner**: Execute optimization tests with multiple solvers

## Features

- Professional dark/light theme support
- Seamless tool navigation
- System overview and capabilities
- Direct access to community resources

## Quick Start

```bash
python core/orchestration/orchestrator.py
```

The interface will open with:
- System Center header with theme toggle
- Four virtue cards highlighting framework capabilities
- Three tool launch cards
- Community contribution invitation

## Navigation

Each tool card includes:
- Tool name and description
- Direct launch button
- Consistent styling matching other interfaces

Click any "Launch" button to open the corresponding tool. From each tool, use the "Back" button in the header to return to System Center.

## Theme Support

Toggle between dark and light modes using the button in the header. Your preference is maintained throughout your session.

## Architecture

- **interface.py**: Main UI class with all components
- **themes.py**: Unified theming system (copied from Runner)
- **components.py**: Reusable custom widgets
- **layouts.py**: Layout builders and configuration
- **tooltip.py**: Enhanced tooltips with theme support
- **help_window.py**: Styled help dialogs
- **config.py**: Configuration and constants
- **orchestrator.py**: Entry point script

## Version

v2.1.0 - Central System Center Interface

## Authors

Andrey Quiceno and Juan Francesco García (AVISPA Team)
