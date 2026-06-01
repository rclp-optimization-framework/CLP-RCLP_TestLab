"""
Core Package - CLP-RCLP Optimization Framework Core Modules

The core package contains the main functional modules of the CLP-RCLP framework:

Modules:
    - converter: Transform JITS2022 benchmark data into MiniZinc format
    - generator: Generate diverse test instances from battery configurations
    - runner: Execute MiniZinc models with multiple solvers and manage results
    - orchestration: Main system orchestrator coordinating all tools
    - shared: Shared utilities (paths, navigation, themes, solvers)

Architecture:
    Each major module (converter, generator, runner, orchestration) contains:
    - ui/: Tkinter-based graphical user interface
    - core/: Business logic and core algorithms
    - config.py: Module-specific configuration
    - Module entry point: <module>.py

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
"""
