"""
Orchestrator Configuration

Central configuration for the System Center interface.
"""

VERSION = "2.1.0"

TOOLS = {
    "converter": {
        "title": "Data Converter",
        "description": "Convert JSON schedules to MiniZinc DZN format for model execution",
        "icon": "E",  # Placeholder for icon
    },
    "generator": {
        "title": "Instance Generator",
        "description": "Generate test instances with configurable parameters and validation",
        "icon": "G",
    },
    "runner": {
        "title": "Test Runner",
        "description": "Execute optimization tests with multiple solvers and real-time monitoring",
        "icon": "R",
    },
}

VIRTUES = [
    {
        "title": "Comprehensive Modeling",
        "description": "Advanced mathematical formulation of the Charging Location Problem",
        "icon": "M",
    },
    {
        "title": "Professional Execution",
        "description": "Multi-solver support with real-time monitoring and detailed results",
        "icon": "E",
    },
    {
        "title": "Advanced Generation",
        "description": "Intelligent test instance creation with feasibility guarantees",
        "icon": "G",
    },
    {
        "title": "Data Management",
        "description": "Seamless conversion and management of test datasets and formats",
        "icon": "D",
    },
]

GITHUB_URL = "https://github.com/AndreyQuicenoC/CLP-RCLP_Minizinc_Lab_Enviroment"
