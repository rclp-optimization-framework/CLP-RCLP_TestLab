"""
Converter Interface - JSON to DZN Conversion Tool

Professional Tkinter GUI for converting JSON bus schedules to MiniZinc DZN format.
Features directory selection, test selection, batch conversion, and result display.

Author: AVISPA Research Team
Date: April 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Dict, List, Optional, Literal
import threading
import logging
from datetime import datetime
import queue

from .themes import ThemeManager, get_theme_dict, DARK_PALETTE, LIGHT_PALETTE
from .components import SectionLabel, FlatButton, Divider, StatusIndicator, FormEntry
from .tooltip import Tooltip
from .help_window import show_help

# Import navigation utility
from core.shared.navigation import return_to_orchestrator
from core.shared.project_paths import ProjectPaths

# Import config and core modules
from core.converter.config import WINDOW_WIDTH, WINDOW_HEIGHT, FONTS
from core.converter.core.jits_analyzer import JITSAnalyzer
from core.converter.core.file_manager import FileManager
from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.experiment_config import ExperimentConfig
from core.converter.core.data_loader import DataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConverterInterface(tk.Frame):
    """Professional JSON to DZN converter interface."""

    def __init__(self, root: tk.Tk):
        """Initialize the converter interface."""
        super().__init__(root)
        self.root = root
        self.master = root
        self.pack(fill=tk.BOTH, expand=True)

        # Initialize theme
        self._init_theme()

        # Setup window
        self.root.title("CLP-RCLP JSON to DZN Converter v2.1.0")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self._center_window()
        self.configure(bg=self.theme_dict["bg_base"])

        # Project root
        self.project_root = ProjectPaths.get_project_root()

        # Conversion state
        self.is_converting = False
        self.conversion_thread: Optional[threading.Thread] = None
        self.conversion_stop_event = threading.Event()
        self.log_queue: queue.Queue = queue.Queue()

        # State variables
        self.available_tests: List[str] = []
        self.available_batteries: List[str] = []
        self.output_format_var = tk.StringVar(value="java")

        # Build UI
        self._build_ui()

    def _init_theme(self) -> None:
        """Initialize theme system."""
        self.theme_dict = get_theme_dict("dark")
        ThemeManager.register_observer(self._on_theme_change)

    def _on_theme_change(self, mode: Literal["dark", "light"]) -> None:
        """Handle theme changes."""
        self.theme_dict = get_theme_dict(mode)
        self._refresh_ui_colors()

    def _center_window(self) -> None:
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _build_ui(self) -> None:
        """Build complete user interface."""
        # Main container
        container = tk.Frame(self, bg=self.theme_dict["bg_base"])
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        self._build_header(container)

        # Content
        content = tk.Frame(container, bg=self.theme_dict["bg_base"])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Left panel (selection)
        self._build_left_panel(content)

        # Right panel (results)
        self._build_right_panel(content)

        # Footer
        self._build_footer(container)

    def _build_header(self, parent: tk.Widget) -> None:
        """Build header with title and theme toggle."""
        header = tk.Frame(parent, bg=self.theme_dict["bg_surface"], height=80)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # Title with accent bar
        left = tk.Frame(header, bg=self.theme_dict["bg_surface"])
        left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20, pady=15)

        # Back button
        back_btn = tk.Label(
            left,
            text="<",
            cursor="hand2",
            fg=self.theme_dict["accent_primary"],
            bg=self.theme_dict["bg_surface"],
            font=("Arial", 18, "bold"),
            padx=8
        )
        back_btn.pack(side=tk.LEFT, padx=(0, 8))
        back_btn.bind("<Button-1>", lambda e: self._on_back_click())
        from .tooltip import Tooltip
        Tooltip(back_btn, "Return to System Center", self.theme_dict)

        tk.Frame(left, bg=self.theme_dict["accent_primary"], width=4, height=32).pack(
            side=tk.LEFT, padx=(0, 12)
        )

        title_frame = tk.Frame(left, bg=self.theme_dict["bg_surface"])
        title_frame.pack(side=tk.LEFT)

        tk.Label(
            title_frame,
            text="JSON to DZN Converter",
            font=("Arial", 16, "bold"),
            fg=self.theme_dict["text_primary"],
            bg=self.theme_dict["bg_surface"]
        ).pack()

        tk.Label(
            title_frame,
            text="Convert JITS2022 test batteries to MiniZinc format",
            font=("Arial", 9),
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_surface"]
        ).pack(anchor=tk.W)

        # Theme toggle
        right = tk.Frame(header, bg=self.theme_dict["bg_surface"])
        right.pack(side=tk.RIGHT, padx=20, pady=15)

        theme_btn = tk.Label(
            right,
            text="☀ Light",
            cursor="hand2",
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_surface"],
            font=("Arial", 9)
        )
        theme_btn.pack()
        theme_btn.bind("<Button-1>", self._toggle_theme)

    def _build_left_panel(self, parent: tk.Widget) -> None:
        """Build left panel with selection controls."""
        left = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Directory selection
        SectionLabel(left, "1. Select Test Battery Directory", self.theme_dict["bg_base"],
                     self.theme_dict["text_primary"]).pack(fill=tk.X, pady=(0, 0))

        self._build_directory_selector(left)

        Divider(left, self.theme_dict["border"]).pack(fill=tk.X, pady=0)

        # Test selection
        SectionLabel(left, "2. Select Tests to Convert", self.theme_dict["bg_base"],
                     self.theme_dict["text_primary"]).pack(fill=tk.X, pady=(0, 5))

        self._build_test_selector(left)

        Divider(left, self.theme_dict["border"]).pack(fill=tk.X, pady=0)

        # Output configuration
        SectionLabel(left, "3. Output Configuration", self.theme_dict["bg_base"],
                     self.theme_dict["text_primary"]).pack(fill=tk.X, pady=(0, 0))

        self._build_output_config(left)

        # Control buttons
        tk.Frame(left, bg=self.theme_dict["bg_base"], height=0).pack(fill=tk.X, pady=0)

        btn_frame = tk.Frame(left, bg=self.theme_dict["bg_base"])
        btn_frame.pack(fill=tk.X, pady=0)

        self.convert_btn = FlatButton(
            btn_frame,
            "Convert",
            command=self._start_conversion,
            theme=self.theme_dict,
            accent=True
        )
        self.convert_btn.pack(fill=tk.X, pady=(0, 1))
        Tooltip(self.convert_btn, "Start converting selected tests", self.theme_dict)

        self.stop_btn = FlatButton(
            btn_frame,
            "Stop",
            command=self._stop_conversion,
            theme=self.theme_dict,
            accent=False,
            disabled=True
        )
        self.stop_btn.pack(fill=tk.X)
        Tooltip(self.stop_btn, "Stop the conversion process", self.theme_dict)

    def _build_directory_selector(self, parent: tk.Widget) -> None:
        """Build directory selection controls."""
        frame = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        frame.pack(fill=tk.X, pady=(0, 0))

        # Instances directory
        tk.Label(
            frame,
            text="Instances to convert:",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"],
            font=("Arial", 9)
        ).pack(anchor=tk.W, pady=(0, 2))

        jits_frame = tk.Frame(frame, bg=self.theme_dict["bg_base"])
        jits_frame.pack(fill=tk.X, pady=(0, 2))

        self.jits_dir_var = tk.StringVar()
        self.jits_dir_combo = ttk.Combobox(jits_frame, textvariable=self.jits_dir_var, state="readonly")
        self.jits_dir_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        browse_btn = tk.Button(
            jits_frame,
            text="Browse",
            command=self._browse_jits_directory,
            bg=self.theme_dict["bg_surface"],
            fg=self.theme_dict["text_primary"],
            relief=tk.FLAT,
            font=("Arial", 9)
        )
        browse_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Help button - now positioned at the right of Browse
        help_btn = tk.Button(
            jits_frame,
            text="?",
            command=self._show_instance_help,
            bg=self.theme_dict["bg_elevated"],
            fg=self.theme_dict["accent_primary"],
            relief=tk.FLAT,
            font=("Arial", 9, "bold"),
            padx=6,
            pady=2
        )
        help_btn.pack(side=tk.LEFT, padx=(5, 0))
        Tooltip(help_btn, "Instance directory format requirements", self.theme_dict)

        # Load JITS directories
        self._load_jits_directories()

    def _build_test_selector(self, parent: tk.Widget) -> None:
        """Build test selection controls."""
        frame = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        frame.pack(fill=tk.X, pady=(0, 10))

        # Test selection mode
        tk.Label(
            frame,
            text="Tests:",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"],
            font=("Arial", 9)
        ).pack(anchor=tk.W, pady=(0, 5))

        mode_frame = tk.Frame(frame, bg=self.theme_dict["bg_base"])
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.test_mode_var = tk.StringVar(value="all")

        tk.Radiobutton(
            mode_frame,
            text="All tests",
            variable=self.test_mode_var,
            value="all",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"],
            selectcolor=self.theme_dict["bg_surface"],
            command=self._update_test_selection
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            mode_frame,
            text="Select a test",
            variable=self.test_mode_var,
            value="selected",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"],
            selectcolor=self.theme_dict["bg_surface"],
            command=self._update_test_selection
        ).pack(anchor=tk.W)

        # Test combobox with refresh button
        test_combo_frame = tk.Frame(frame, bg=self.theme_dict["bg_base"])
        test_combo_frame.pack(fill=tk.X, pady=(5, 0))

        self.test_var = tk.StringVar()
        self.test_combo = ttk.Combobox(
            test_combo_frame,
            textvariable=self.test_var,
            state="disabled",
            font=("Arial", 9)
        )
        self.test_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Refresh button
        self.test_refresh_btn = tk.Button(
            test_combo_frame,
            text="Refresh",
            command=self._refresh_tests,
            bg=self.theme_dict["bg_elevated"],
            fg=self.theme_dict["text_primary"],
            relief=tk.FLAT,
            font=("Arial", 9),
            padx=8,
            pady=4,
            state=tk.DISABLED
        )
        self.test_refresh_btn.pack(side=tk.LEFT, padx=(5, 0))
        Tooltip(self.test_refresh_btn, "Reload available tests", self.theme_dict)

    def _build_output_config(self, parent: tk.Widget) -> None:
        """Build output configuration controls."""
        frame = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        frame.pack(fill=tk.X, pady=(0, 10))

        # Conversion format (Java-compatible only)
        tk.Label(
            frame,
            text="Conversion Format:",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"],
            font=("Arial", 9)
        ).pack(anchor=tk.W, pady=(0, 5))

        format_frame = tk.Frame(frame, bg=self.theme_dict["bg_base"])
        format_frame.pack(fill=tk.X, pady=(0, 10))

        # NOTE: Only Java-compatible mode is supported.
        format_info = tk.Label(
            format_frame,
            text="Java-compatible mode (scaled energy units, seconds for time)",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"]
        )
        format_info.pack(anchor=tk.W)

        Tooltip(
            format_frame,
            "Converts to Java-compatible units: energy in distance units (m), time in seconds, using experiment parameters.",
            self.theme_dict
        )

        # Output battery
        tk.Label(
            frame,
            text="Output Battery:",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"],
            font=("Arial", 9)
        ).pack(anchor=tk.W, pady=(0, 5))

        output_frame = tk.Frame(frame, bg=self.theme_dict["bg_base"])
        output_frame.pack(fill=tk.X, pady=(0, 10))

        self.output_battery_var = tk.StringVar()
        self.output_combo = ttk.Combobox(
            output_frame,
            textvariable=self.output_battery_var,
            state="readonly",
            font=("Arial", 9)
        )
        self.output_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Refresh button for output batteries
        self.battery_refresh_btn = tk.Button(
            output_frame,
            text="Refresh",
            command=self._refresh_batteries,
            bg=self.theme_dict["bg_elevated"],
            fg=self.theme_dict["text_primary"],
            relief=tk.FLAT,
            font=("Arial", 9),
            padx=8,
            pady=4
        )
        self.battery_refresh_btn.pack(side=tk.LEFT, padx=(5, 0))
        Tooltip(self.battery_refresh_btn, "Reload available output batteries", self.theme_dict)

        # Directory selection options
        self.output_option_var = tk.StringVar(value="existing")

        tk.Radiobutton(
            frame,
            text="Use existing directory",
            variable=self.output_option_var,
            value="existing",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"],
            selectcolor=self.theme_dict["bg_surface"],
            command=self._update_output_option
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            frame,
            text="Create new directory",
            variable=self.output_option_var,
            value="new",
            bg=self.theme_dict["bg_base"],
            fg=self.theme_dict["text_primary"],
            selectcolor=self.theme_dict["bg_surface"],
            command=self._update_output_option
        ).pack(anchor=tk.W, pady=(0, 10))

        # New directory entry (initially disabled)
        self.new_dir_var = tk.StringVar()
        self.new_dir_entry = tk.Entry(
            frame,
            textvariable=self.new_dir_var,
            bg=self.theme_dict["bg_surface"],
            fg=self.theme_dict["text_primary"],
            relief=tk.FLAT,
            state=tk.DISABLED,
            font=("Arial", 9)
        )
        self.new_dir_entry.pack(fill=tk.X)

        # Load available batteries
        self._load_batteries()

    def _load_jits_directories(self) -> None:
        """Load JITS2022 test directories."""
        jits_path = ProjectPaths.jits_data_dir()
        directories = JITSAnalyzer.get_test_directories(jits_path)

        if directories:
            self.jits_dir_var.set(directories[0])
            # Update the combobox values if it exists
            if hasattr(self, 'jits_dir_combo'):
                self.jits_dir_combo['values'] = directories

    def _load_batteries(self) -> None:
        """Load available battery directories from experiments/instances folder."""
        data_path = ProjectPaths.instances_dir()
        batteries = []

        if data_path.exists():
            for item in data_path.iterdir():
                if item.is_dir():
                    batteries.append(item.name)

        batteries.sort()
        self.available_batteries = batteries

        if hasattr(self, 'output_combo'):
            self.output_combo['values'] = batteries
            if batteries:
                self.output_battery_var.set(batteries[0])

    def _refresh_batteries(self) -> None:
        """Refresh the list of available output batteries."""
        self._load_batteries()
        self._log(f"Refreshed battery list: {len(self.available_batteries)} batteries found", "info")

    def _update_test_selection(self) -> None:
        """Update test selection controls based on mode."""
        if self.test_mode_var.get() == "all":
            self.test_combo.config(state=tk.DISABLED)
            self.test_refresh_btn.config(state=tk.DISABLED)
        else:
            self.test_combo.config(state="readonly")
            self.test_refresh_btn.config(state=tk.NORMAL)
            self._refresh_tests()

    def _refresh_tests(self) -> None:
        """Refresh available tests from selected directory."""
        jits_dir = self.jits_dir_var.get()
        if not jits_dir:
            messagebox.showwarning("Warning", "Please select a directory first")
            return

        try:
            jits_path = ProjectPaths.jits_data_dir() / jits_dir
            # Search for buses_input*.json files
            json_files = JITSAnalyzer.get_json_files(jits_path, "buses_input*.json")
            self.available_tests = [f.stem.replace("buses_input_", "").replace("buses_input", "") for f in json_files]
            self.test_combo['values'] = self.available_tests
            if self.available_tests:
                self.test_combo.current(0)
            self._log(f"Found {len(self.available_tests)} tests in {jits_dir}", "info")
        except Exception as e:
            self._log(f"Error loading tests: {str(e)}", "error")

    def _update_output_option(self) -> None:
        """Update output option controls."""
        if self.output_option_var.get() == "new":
            self.new_dir_entry.config(state=tk.NORMAL)
            self.output_combo.config(state=tk.DISABLED)
        else:
            self.new_dir_entry.config(state=tk.DISABLED)
            self.output_combo.config(state="readonly")

    def _browse_jits_directory(self) -> None:
        """Browse for JITS directory."""
        initial_dir = ProjectPaths.jits_data_dir()
        directory = filedialog.askdirectory(initialdir=str(initial_dir))
        if directory:
            self.jits_dir_var.set(Path(directory).name)

    def _start_conversion(self) -> None:
        """Start conversion process in separate thread."""
        if self.is_converting:
            messagebox.showwarning("Warning", "Conversion already in progress")
            return

        self.is_converting = True
        self.conversion_stop_event.clear()  # Reset stop flag
        self.log_queue.queue.clear()  # Clear previous logs
        self.convert_btn.set_disabled(True)
        self.stop_btn.set_disabled(False)

        self.conversion_thread = threading.Thread(target=self._do_conversion, daemon=True)
        self.conversion_thread.start()

        # Start polling for log messages from thread
        self._poll_log_queue()

    def _do_conversion(self) -> None:
        """Perform the actual conversion (runs in background thread)."""
        try:
            # Validate inputs
            jits_dir = self.jits_dir_var.get()
            output_dir_name = self.output_battery_var.get()
            test_mode = self.test_mode_var.get()

            if not jits_dir or not output_dir_name:
                self.log_queue.put(("Error: Please select directory and output battery", "error"))
                return

            # Get output directory path
            if self.output_option_var.get() == "new":
                new_dir_name = self.new_dir_var.get().strip()
                if not new_dir_name:
                    self.log_queue.put(("Error: Please enter a name for the new directory", "error"))
                    return
                output_path = ProjectPaths.instances_dir() / new_dir_name
            else:
                output_path = ProjectPaths.instances_dir() / output_dir_name

            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)
            self.log_queue.put((f"Output directory: {output_path}", "info"))

            # Get JSON files to convert
            jits_path = ProjectPaths.jits_data_dir() / jits_dir
            json_files = JITSAnalyzer.get_json_files(jits_path, "buses_input*.json")

            if not json_files:
                self.log_queue.put((f"No JSON files found in {jits_dir}", "error"))
                return

            # Filter by test selection mode
            if test_mode == "selected":
                selected_test = self.test_var.get()
                if not selected_test:
                    self.log_queue.put(("Error: Please select a test", "error"))
                    return
                # Filter files by selected test
                json_files = [f for f in json_files if selected_test in f.stem]

            if not json_files:
                self.log_queue.put(("No tests selected for conversion", "error"))
                return

            self.log_queue.put((f"Converting {len(json_files)} tests from {jits_dir}...", "info"))

            # Load experiment data
            self.log_queue.put(("Loading stations and distance data...", "info"))

            # Load stations and distances
            stations, station_count = DataLoader.load_stations(jits_path)
            distances, dist_station_count = DataLoader.load_distances(jits_path)

            if distances:
                self.log_queue.put((f"Loaded {len(distances)} distance entries", "info"))
            else:
                self.log_queue.put(("No distance data found. Using fallback calculation.", "warning"))

            output_format = self.output_format_var.get()
            self.log_queue.put((f"Using conversion format: {output_format}", "info"))

            # Load JITS experiment parameters when available.
            # This preserves Java baseline semantics in java-compatible mode.
            config_file = self._find_experiment_config(jits_path)
            config = ExperimentConfig(config_file=config_file) if config_file else ExperimentConfig()
            if config_file:
                self.log_queue.put((f"Loaded experiment config: {config_file.name}", "info"))
            else:
                self.log_queue.put(("No experiment_parameters*.txt found; using default conversion parameters.", "warning"))

            self.log_queue.put((
                f"Using config: cmax={config.cmax}, cmin={config.cmin}, charging_rate={config.charging_rate}, "
                f"model_speed={config.model_speed}, rest_time={config.rest_time}",
                "info"
            ))

            distances, dist_station_count = DataLoader.load_distances(jits_path)

            # Perform conversion with source directory name and loaded data
            success_count, failure_count, messages = ConverterEngine.batch_convert_files(
                json_files,
                output_path,
                jits_dir,
                config=config,
                distances_dict=distances,
                output_format=output_format
            )

            # Log results
            for msg in messages:
                if msg.startswith("✓"):
                    self.log_queue.put((msg, "success"))
                else:
                    self.log_queue.put((msg, "error"))

            # Summary
            self.log_queue.put((f"Conversion complete: {success_count} successful, {failure_count} failed", "success"))

        except Exception as e:
            self.log_queue.put((f"Error: {str(e)}", "error"))
            logger.error(f"Conversion error: {e}", exc_info=True)
        finally:
            self.is_converting = False
            # Schedule UI updates in main thread
            self.root.after(0, lambda: self.convert_btn.set_disabled(False))
            self.root.after(0, lambda: self.stop_btn.set_disabled(True))

    def _stop_conversion(self) -> None:
        """Stop ongoing conversion."""
        self.conversion_stop_event.set()  # Signal thread to stop
        self._log("Conversion stopped by user", "warning")
        self.convert_btn.set_disabled(False)
        self.stop_btn.set_disabled(True)

    def _find_experiment_config(self, jits_path: Path) -> Optional[Path]:
        """Find best experiment parameter file in the selected JITS dataset directory or parent."""
        priority = [
            "experiment_parameters.txt",
            "experiment_parameters_clean.txt",
            "experiment_parameters_cork1.txt",
            "experiment_parameters_toy.txt",
        ]

        # First try the current directory
        for filename in priority:
            candidate = jits_path / filename
            if candidate.exists():
                return candidate

        # Try parent directory (for subdirectories like cork-1-line/)
        for filename in priority:
            candidate = jits_path.parent / filename
            if candidate.exists():
                return candidate

        # Wildcard search in current directory
        wildcard_matches = sorted(jits_path.glob("experiment_parameters*.txt"))
        if wildcard_matches:
            return wildcard_matches[0]

        # Wildcard search in parent directory
        parent_matches = sorted(jits_path.parent.glob("experiment_parameters*.txt"))
        if parent_matches:
            return parent_matches[0]

        return None

    def _build_right_panel(self, parent: tk.Widget) -> None:
        """Build right panel with conversion results."""
        right = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Status
        SectionLabel(right, "Conversion Status", self.theme_dict["bg_base"],
                     self.theme_dict["text_primary"]).pack(fill=tk.X, pady=(0, 10))

        self.status_indicator = StatusIndicator(right, self.theme_dict["bg_base"])
        self.status_indicator.pack(fill=tk.X, pady=(0, 15))

        # Results display header with clear button
        log_header_frame = tk.Frame(right, bg=self.theme_dict["bg_base"])
        log_header_frame.pack(fill=tk.X, pady=(0, 10))

        SectionLabel(log_header_frame, "Conversion Log", self.theme_dict["bg_base"],
                     self.theme_dict["text_primary"]).pack(side=tk.LEFT, fill=tk.X, expand=True)

        clear_btn = tk.Button(
            log_header_frame,
            text="Clear",
            command=self._clear_log,
            bg=self.theme_dict["bg_surface"],
            fg=self.theme_dict["text_primary"],
            relief=tk.FLAT,
            font=("Arial", 8)
        )
        clear_btn.pack(side=tk.RIGHT)

        scrollbar = ttk.Scrollbar(right)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(
            right,
            bg=self.theme_dict["bg_surface"],
            fg=self.theme_dict["text_primary"],
            yscrollcommand=scrollbar.set,
            font=("Courier New", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)

    def _build_footer(self, parent: tk.Widget) -> None:
        """Build footer with version and help."""
        footer = tk.Frame(parent, bg=self.theme_dict["bg_surface"], height=30)
        footer.pack(fill=tk.X, padx=0, pady=0)
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="v2.1.0 | Click [?] icons for help | Select a battery and tests to convert",
            bg=self.theme_dict["bg_surface"],
            fg=self.theme_dict["text_secondary"],
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=20, pady=5)

    def _poll_log_queue(self) -> None:
        """Poll log queue for messages from conversion thread (thread-safe)."""
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                self._log(message, level)
        except queue.Empty:
            pass

        # Continue polling if conversion is still running
        if self.is_converting:
            self.root.after(100, self._poll_log_queue)

    def _log(self, message: str, level: str = "info") -> None:
        """Log message to results display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"

        self.results_text.insert(tk.END, log_line)
        self.results_text.see(tk.END)

        if level == "success":
            self.status_indicator.set_status("success", "Success")
        elif level == "error":
            self.status_indicator.set_status("error", "Error")
        elif level == "warning":
            self.status_indicator.set_status("warning", "Warning")

    def _clear_log(self) -> None:
        """Clear the conversion log."""
        self.results_text.delete("1.0", tk.END)
        self.status_indicator.set_status("idle", "Ready")

    def _on_back_click(self) -> None:
        """Handle back button click - return to Orchestrator."""
        return_to_orchestrator(self.root)

    def _toggle_theme(self, event=None) -> None:
        """Toggle between dark and light themes."""
        current = ThemeManager.get_current_theme()
        new_theme = "light" if current == "dark" else "dark"
        ThemeManager.switch_theme(new_theme)

    def _show_instance_help(self) -> None:
        """Show styled help window for instance directory requirements."""
        help_content = """JITS2022 INSTANCE DIRECTORY REQUIREMENTS
════════════════════════════════════════════════════════════════

REQUIRED FILES:

✓ buses_input_<SPEED>_<REST>.json
  Bus schedules and routes in JSON format.
  Example: buses_input_20_0.json (20 km/h speed, 0 min rest)

✓ stations_input.csv
  Station information with IDs and names.
  Format: name, id

✓ distances_input.csv
  Distance matrix between all station pairs (in kilometers).
  Format: from_id, to_id, distance


HOW THE CONVERTER USES THESE FILES:

1. SCHEDULES (buses_input JSON)
   • Extracts bus routes and timetables
   • Calculates travel times (T) between stops
   • Determines energy consumption (D) per arc

2. STATIONS (stations_input.csv)
   • Maps station IDs to physical locations
   • Creates station-to-index mapping for DZN file
   • Validates route feasibility

3. DISTANCES (distances_input.csv)
   • Provides distance data for energy calculations
   • Allows precise consumption modeling
   • Critical for accuracy of converted data


CONVERSION OUTPUT:

The converter generates a .dzn file with:
• st_bi: Station sequence for each bus
• D: Energy consumption per arc (scaled for precision)
• T: Travel times between stops
• tau_bi: Original schedule times
• Problem dimensions and parameters

Energy precision uses SCALE_ENERGY=1000:
  1 unit = 0.001 kWh (0.1% precision)
  This ensures model feasibility without precision loss.


OPTIONAL FILES (ignored):

⊘ input_report.txt (ignored)
⊘ Other files not listed above


CONVERSION FORMATS:

• Normalized integer mode
    Keeps the current scaled integer output used by the CLP pipeline.

• Original decimal mode
    Preserves raw decimal distances and energy calculations for the external model.
    Use this when you need the same values that appear in the source JSON/CSV files.


EXAMPLE DIRECTORY STRUCTURE:

JITS2022/Code/Data/
├── cork-1-line/
│   ├── buses_input_20_0.json
│   ├── buses_input_20_5.json
│   ├── stations_input.csv
│   └── distances_input.csv
└── cork-2-lines/
    ├── buses_input_30_0.json
    ├── stations_input.csv
    └── distances_input.csv


TIPS FOR SUCCESSFUL CONVERSION:

• Ensure all three file types are present
• Verify file encoding is UTF-8
• Check that station IDs match across files
• Use consistent distance units (meters recommended)
• Verify JSON syntax is valid

"""
        show_help(self.root, "Instance Directory Requirements", help_content, self.theme_dict)

    def _on_format_change(self) -> None:
        """React to format selection changes."""
        # Format is now Java-compatible only
        self._log("Java-compatible mode: outputs will follow Java unit conventions.", "info")

    def _refresh_ui_colors(self) -> None:
        """Refresh UI colors after theme change by rebuilding the entire interface."""
        # Destroy all existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Rebuild UI with new theme
        self._build_ui()


def main():
    """Entry point for Converter GUI."""
    root = tk.Tk()
    app = ConverterInterface(root)
    root.mainloop()


if __name__ == "__main__":
    main()
