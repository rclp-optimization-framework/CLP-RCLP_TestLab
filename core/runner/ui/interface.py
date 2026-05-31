"""
Runner Interface - Professional MiniZinc Test Executor GUI

Premium dark/light mode UI for executing CLP/RCLP test instances with real-time monitoring,
result generation, and professional theme support.

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)

Architecture:
- Dynamic theme switching (dark/light modes)
- Modular components from .components module
- TTK-based styling for dropdown/scrollbar consistency
- Two-panel layout: Config (left) + Results (right)
- Real-time execution monitoring with status indicators
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Any, Literal, Optional, Callable
import threading
import logging

# Import modular theme system
from .themes import ThemeManager, get_theme_dict, DARK_PALETTE, LIGHT_PALETTE
from .components import SectionLabel, FlatButton, Divider, StatusIndicator
from .layouts import LayoutBuilder, LayoutConfig
from .tooltip import Tooltip

# Import navigation utility
from core.shared.navigation import return_to_orchestrator
from core.shared.project_paths import ProjectPaths

# Import Runner core modules
from core.runner.core.executor import MiniZincExecutor
from core.runner.core.result_handler import ResultHandler
from core.runner.core.solvers import SolverType, SolverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RunnerInterface(tk.Frame):
    """Professional MiniZinc test runner interface with theme switching support."""

    def __init__(self, root: tk.Tk):
        """
        Initialize the Runner interface.

        Sets up theming, observes theme changes, builds UI, and applies styling.
        """
        super().__init__(root)
        self.root = root
        self.master = root
        self.pack(fill=tk.BOTH, expand=True)

        # Initialize theme system
        self._init_theme()

        # Setup window properties
        self.root.title("CLP-RCLP Test Runner v2.1.0")
        self.root.geometry("950x650")
        self.root.resizable(False, False)
        self._center_window()
        self.configure(bg=self.theme_dict["bg_base"])

        # Initialize core modules
        self.executor: Optional[MiniZincExecutor] = None
        self.result_handler: Optional[ResultHandler] = None
        self.execution_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.is_running = False

        # Find project root for file operations
        self.project_root = ProjectPaths.get_project_root()

        # Build UI
        self._build_ui()
        self._apply_ttk_theme()

    def _init_theme(self) -> None:
        """Initialize theme system and register observer for dynamic switching."""
        self.theme_dict = get_theme_dict("dark")
        ThemeManager.register_observer(self._on_theme_change)

    def _on_theme_change(self, mode: Literal["dark", "light"]) -> None:
        """
        Called when theme mode changes (dark ↔ light).

        Refreshes the theme dictionary and updates all UI colors dynamically.
        """
        self.theme_dict = get_theme_dict(mode)
        self._refresh_ui_colors()

    def _center_window(self) -> None:
        """Center window on screen (horizontal and vertical)."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _build_ui(self) -> None:
        """Build the complete user interface with two-panel layout."""
        # Main container
        container = tk.Frame(self, bg=self.theme_dict["bg_base"])
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        self._build_header(container)

        # Content area (two panels)
        content = tk.Frame(container, bg=self.theme_dict["bg_base"])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=0)

        # Left panel (config)
        self._build_left_panel(content)

        # Right panel (results)
        self._build_right_panel(content)

        # Footer
        self._build_footer(container)

        # Log battery discovery status
        batteries_path = Path(self.project_root) / "experiments" / "instances"
        if batteries_path.exists():
            batteries = self._load_available_batteries()
            if batteries:
                self._log(f"Found {len(batteries)} test batteries: {', '.join(batteries)}", "info")
            else:
                self._log("No test batteries found in experiments/instances", "warning")
        else:
            self._log("Warning: experiments/instances directory not found", "warning")

    def _build_header(self, parent: tk.Widget) -> None:
        """Build the header with title and status indicator."""
        header = tk.Frame(parent, bg=self.theme_dict["bg_surface"], height=70)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # Left side: Back button + Title with accent bar
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
        Tooltip(back_btn, "Return to System Center", self.theme_dict)

        tk.Frame(left, bg=self.theme_dict["accent_primary"], width=4, height=24).pack(
            side=tk.LEFT, padx=(0, 12)
        )

        tk.Label(
            left,
            text="CLP-RCLP TEST RUNNER",
            font=self.theme_dict["font_bold"],
            fg=self.theme_dict["text_primary"],
            bg=self.theme_dict["bg_surface"],
        ).pack(side=tk.LEFT)

        # Right side: Status and theme toggle
        right = tk.Frame(header, bg=self.theme_dict["bg_surface"])
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=10)

        # StatusIndicator (modular component)
        self.status_indicator = StatusIndicator(right, "Ready", self.theme_dict)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 16))

        # Theme toggle button
        toggle_text = "🌙 Dark" if ThemeManager.get_mode() == "light" else "☀ Light"
        self.theme_toggle_btn = FlatButton(
            right,
            toggle_text,
            command=self._toggle_theme,
            theme=self.theme_dict,
            accent=False,
        )
        self.theme_toggle_btn.pack(side=tk.LEFT)

    def _build_left_panel(self, parent: tk.Widget) -> None:
        """Build left configuration panel."""
        left_panel = tk.Frame(parent, bg=self.theme_dict["bg_surface"], width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        left_panel.pack_propagate(False)

        # Scrollable content area
        canvas = tk.Canvas(
            left_panel,
            bg=self.theme_dict["bg_surface"],
            highlightthickness=0,
            bd=0,
        )
        scrollbar = ttk.Scrollbar(
            left_panel, orient=tk.VERTICAL, command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg=self.theme_dict["bg_surface"])
        scrollable_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Config card
        card = tk.Frame(
            scrollable_frame,
            bg=self.theme_dict["bg_elevated"],
            relief=tk.FLAT,
            bd=0,
        )
        card.pack(fill=tk.BOTH, expand=True, padx=0, pady=12)

        # Directory selection
        SectionLabel(card, "Directory", self.theme_dict).pack(anchor="w", padx=12, pady=(14, 6))
        self.dir_var = tk.StringVar()
        dirs = self._load_available_batteries()
        self.dir_combo = ttk.Combobox(
            card,
            textvariable=self.dir_var,
            values=dirs,
            state="readonly",
            style="Dark.TCombobox",
        )
        if dirs:
            self.dir_combo.current(0)
        self.dir_combo.pack(fill=tk.X, padx=12, pady=(0, 5))
        self.dir_combo.bind("<<ComboboxSelected>>", lambda _: self._update_subdirectories())
        Tooltip(self.dir_combo, "Select test dataset directory", self.theme_dict)

        Divider(card, self.theme_dict).pack(fill=tk.X, padx=5, pady=5)

        # Subdirectory selection (for nested battery structures)
        SectionLabel(card, "Subdirectory", self.theme_dict).pack(anchor="w", padx=12, pady=(0, 6))
        self.subdir_var = tk.StringVar(value="Root")
        self.subdir_combo = ttk.Combobox(
            card,
            textvariable=self.subdir_var,
            values=["Root"],
            state="readonly",
            style="Dark.TCombobox",
        )
        self.subdir_combo.current(0)
        self.subdir_combo.pack(fill=tk.X, padx=12, pady=(0, 5))
        self.subdir_combo.bind("<<ComboboxSelected>>", lambda _: self._refresh_instances())
        Tooltip(self.subdir_combo, "Select subdirectory within battery (if available)", self.theme_dict)

        Divider(card, self.theme_dict).pack(fill=tk.X, padx=5, pady=5)

        # Test instance selection
        SectionLabel(card, "Instance", self.theme_dict).pack(anchor="w", padx=12, pady=(0, 6))
        inst_frame = tk.Frame(card, bg=self.theme_dict["bg_elevated"])
        inst_frame.pack(fill=tk.X, padx=12, pady=(0, 5))

        self.instance_var = tk.StringVar()
        self.instance_combo = ttk.Combobox(
            inst_frame,
            textvariable=self.instance_var,
            state="readonly",
            style="Dark.TCombobox",
            width=25,
        )
        self.instance_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        Tooltip(self.instance_combo, "Select test instance file (.dzn)", self.theme_dict)

        refresh_btn = FlatButton(inst_frame, "Refresh", command=self._refresh_instances,
                                theme=self.theme_dict, accent=False)
        refresh_btn.pack(side=tk.LEFT, padx=(6, 0))
        Tooltip(refresh_btn, "Reload list of available instances", self.theme_dict)

        Divider(card, self.theme_dict).pack(fill=tk.X, padx=12, pady=5)

        # Solver selection
        SectionLabel(card, "Solver", self.theme_dict).pack(anchor="w", padx=12, pady=(0, 6))
        solver_frame = tk.Frame(card, bg=self.theme_dict["bg_elevated"])
        solver_frame.pack(fill=tk.X, padx=12, pady=(0, 5))

        self.solver_var = tk.StringVar(value="chuffed")
        solver_names = [SolverManager.get_display_name(s) for s in SolverManager.get_available_solvers()]
        self.solver_combo = ttk.Combobox(
            solver_frame,
            textvariable=self.solver_var,
            values=solver_names,
            state="readonly",
            style="Dark.TCombobox",
            width=15,
        )
        self.solver_combo.current(0)
        self.solver_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        Tooltip(self.solver_combo, "Choose MiniZinc solver backend for execution", self.theme_dict)

        # Solver info button
        info_btn = tk.Label(
            solver_frame,
            text="?",
            font=("Arial", 12, "bold"),
            fg=self.theme_dict["accent_primary"],
            bg=self.theme_dict["bg_elevated"],
            cursor="hand2",
            width=2,
        )
        info_btn.pack(side=tk.LEFT, padx=(6, 0))
        info_btn.bind("<Button-1>", self._show_solver_info)
        Tooltip(info_btn, "Show solver information and capabilities", self.theme_dict)

        Divider(card, self.theme_dict).pack(fill=tk.X, padx=12, pady=12)
        self.model_var = tk.StringVar(value="CLP")

        model_frame = tk.Frame(card, bg=self.theme_dict["bg_elevated"])
        model_frame.pack(fill=tk.X, padx=12, pady=(0, 5))

        for model in ["CLP", "RCLP"]:
            rb = tk.Radiobutton(
                model_frame,
                text=model,
                variable=self.model_var,
                value=model,
                bg=self.theme_dict["bg_elevated"],
                fg=self.theme_dict["text_primary"],
                selectcolor=self.theme_dict["accent_primary"],
                activebackground=self.theme_dict["bg_hover"],
            )
            rb.pack(side=tk.LEFT, padx=8)

        Divider(card, self.theme_dict).pack(fill=tk.X, padx=12, pady=5)

        SectionLabel(card, "Number Type", self.theme_dict).pack(anchor="w", padx=12, pady=(0, 6))
        precision_frame = tk.Frame(card, bg=self.theme_dict["bg_elevated"])
        precision_frame.pack(fill=tk.X, padx=12, pady=(0, 5))

        self.precision_var = tk.StringVar(value="integer")
        for label, value in [("Integer", "integer"), ("Floating", "floating")]:
            rb = tk.Radiobutton(
                precision_frame,
                text=label,
                variable=self.precision_var,
                value=value,
                bg=self.theme_dict["bg_elevated"],
                fg=self.theme_dict["text_primary"],
                selectcolor=self.theme_dict["accent_primary"],
                activebackground=self.theme_dict["bg_hover"],
            )
            rb.pack(side=tk.LEFT, padx=8)

        Tooltip(
            precision_frame,
            "Integer models keep the current scaled workflow. Floating models preserve original decimal values.",
            self.theme_dict,
        )

        Divider(card, self.theme_dict).pack(fill=tk.X, padx=12, pady=5)

        # Action buttons
        btn_frame = tk.Frame(card, bg=self.theme_dict["bg_elevated"])
        btn_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.run_btn = FlatButton(
            btn_frame,
            "Run Test",
            command=self._start_execution,
            theme=self.theme_dict,
            accent=True,
        )
        self.run_btn.pack(fill=tk.X, pady=(0, 8))
        Tooltip(self.run_btn, "Execute test with selected instance and solver", self.theme_dict)

        self.stop_btn = FlatButton(
            btn_frame,
            "Stop",
            command=self._stop_execution,
            theme=self.theme_dict,
            accent=False,
            disabled=True,
        )
        self.stop_btn.pack(fill=tk.X)
        Tooltip(self.stop_btn, "Stop the running test execution", self.theme_dict)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_right_panel(self, parent: tk.Widget) -> None:
        """Build right results display panel."""
        right_panel = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Output log header
        log_header = tk.Frame(right_panel, bg=self.theme_dict["bg_surface"], height=40)
        log_header.pack(fill=tk.X, padx=12, pady=(12, 0))
        log_header.pack_propagate(False)

        tk.Label(
            log_header,
            text="OUTPUT LOG",
            font=self.theme_dict["font_section"],
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_surface"],
        ).pack(side=tk.LEFT, anchor="w")

        clear_btn = tk.Label(
            log_header,
            text="[Clear]",
            font=self.theme_dict["font_ui"],
            fg=self.theme_dict["accent_glow"],
            bg=self.theme_dict["bg_surface"],
            cursor="hand2",
        )
        clear_btn.pack(side=tk.RIGHT, anchor="e")
        clear_btn.bind("<Button-1>", lambda _: self._clear_log())

        # Log display
        wrap = tk.Frame(right_panel, bg=self.theme_dict["bg_base"])
        wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.log_text = tk.Text(
            wrap,
            height=25,
            width=60,
            bg=self.theme_dict["bg_elevated"],
            fg=self.theme_dict["text_code"],
            font=self.theme_dict["font_mono"],
            relief=tk.FLAT,
            bd=0,
            insertbackground=self.theme_dict["accent_primary"],
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Configure log text tags for colored output
        self.log_text.tag_configure("success", foreground=self.theme_dict["success"], font=(self.theme_dict["font_mono"][0], self.theme_dict["font_mono"][1], "bold"))
        self.log_text.tag_configure("error", foreground=self.theme_dict["error"], font=(self.theme_dict["font_mono"][0], self.theme_dict["font_mono"][1], "bold"))
        self.log_text.tag_configure("warning", foreground=self.theme_dict["warning"])
        self.log_text.tag_configure("info", foreground=self.theme_dict["accent_glow"])
        self.log_text.tag_configure("muted", foreground=self.theme_dict["text_muted"])
        self.log_text.tag_configure("key", foreground=self.theme_dict["text_secondary"])
        self.log_text.tag_configure("value", foreground=self.theme_dict["accent_glow"])

    def _build_footer(self, parent: tk.Widget) -> None:
        """Build the footer with project info."""
        footer = tk.Frame(parent, bg=self.theme_dict["bg_surface"], height=40)
        footer.pack(fill=tk.X, padx=0, pady=0)
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="MiniZinc Test Executor · CLP/RCLP Solver",
            font=self.theme_dict["font_small"],
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_surface"],
        ).pack(side=tk.LEFT, padx=12, pady=8)

        tk.Label(
            footer,
            text="v2.1.0",
            font=self.theme_dict["font_small"],
            fg=self.theme_dict["text_muted"],
            bg=self.theme_dict["bg_surface"],
        ).pack(side=tk.RIGHT, padx=12, pady=8)

    def _apply_ttk_theme(self) -> None:
        """Apply TTK styling based on current theme."""
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # Combobox styling
        style.configure(
            "Dark.TCombobox",
            fieldbackground=self.theme_dict["bg_elevated"],
            background=self.theme_dict["bg_elevated"],
            foreground=self.theme_dict["text_primary"],
            selectbackground=self.theme_dict["accent_dim"],
            selectforeground=self.theme_dict["text_primary"],
            bordercolor=self.theme_dict["border_normal"],
            darkcolor=self.theme_dict["bg_elevated"],
            lightcolor=self.theme_dict["bg_elevated"],
            arrowcolor=self.theme_dict["text_secondary"],
            padding=(10, 6),
            font=self.theme_dict["font_ui"],
            relief="flat",
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("focus", self.theme_dict["bg_elevated"])],
            bordercolor=[("focus", self.theme_dict["border_active"])],
            foreground=[("disabled", self.theme_dict["text_muted"])],
        )

        # Scrollbar styling
        style.configure(
            "Dark.Vertical.TScrollbar",
            background=self.theme_dict["bg_elevated"],
            troughcolor=self.theme_dict["bg_surface"],
            bordercolor=self.theme_dict["bg_surface"],
            arrowcolor=self.theme_dict["text_muted"],
            width=8,
            relief="flat",
        )

    def _on_back_click(self) -> None:
        """Handle back button click - return to Orchestrator."""
        return_to_orchestrator(self.root)

    def _toggle_theme(self) -> None:
        """Toggle between dark and light theme modes."""
        current_mode = ThemeManager.get_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ThemeManager.set_mode(new_mode)

    def _refresh_ui_colors(self):
        # Destruir todo
        for widget in self.winfo_children():
            widget.destroy()

        # Reconstruir UI con nuevo tema
        self._build_ui()
        self._apply_ttk_theme()
    
    def _refresh_instances(self) -> None:
        """Refresh the list of available test instances from selected battery and subdirectory."""
        directory = self.dir_var.get()
        if not directory:
            return

        subdir = self.subdir_var.get()
        data_path = Path(self.project_root) / "experiments" / "instances" / directory

        if subdir and subdir != "Root":
            data_path = data_path / subdir

        instances = sorted([f.stem for f in data_path.glob("*.dzn")]) if data_path.exists() else []

        self.instance_combo["values"] = instances
        if instances:
            self.instance_combo.current(0)

        self._log(f"Found {len(instances)} instances in {directory}/{subdir if subdir != 'Root' else ''}", "info")

    def _load_available_batteries(self) -> list:
        """Load available battery directories from experiments/instances."""
        batteries_path = Path(self.project_root) / "experiments" / "instances"

        if not batteries_path.exists():
            return []

        # Hide legacy original-decimal batteries from UI to avoid non-parity runs.
        hidden_legacy_dirs = {"battery-original"}

        batteries = sorted([
            d.name for d in batteries_path.iterdir()
            if d.is_dir() and not d.name.startswith('.') and d.name not in hidden_legacy_dirs
        ])

        return batteries

    def _get_battery_subdirectories(self, battery_name: str) -> list:
        """Return list of subdirectories in battery, or empty if none."""
        battery_path = Path(self.project_root) / "experiments" / "instances" / battery_name
        if not battery_path.exists():
            return []

        subdirs = sorted([
            d.name for d in battery_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ])

        return subdirs

    def _update_subdirectories(self) -> None:
        """Update subdirectory dropdown when battery selection changes."""
        battery_name = self.dir_var.get()
        if not battery_name:
            self.subdir_combo["values"] = ["Root"]
            self.subdir_var.set("Root")
            return

        subdirs = self._get_battery_subdirectories(battery_name)
        if subdirs:
            self.subdir_combo["values"] = ["Root"] + subdirs
        else:
            self.subdir_combo["values"] = ["Root"]

        self.subdir_var.set("Root")
        self.subdir_combo.current(0)
        self._refresh_instances()

    def _log(self, message: str, tag: str = "muted") -> None:
        """Add a message to the output log."""
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)

    def _clear_log(self) -> None:
        """Clear the output log."""
        self.log_text.delete("1.0", tk.END)

    def _start_execution(self) -> None:
        """Start execution of the selected test instance."""
        instance = self.instance_var.get()
        model = self.model_var.get()
        precision = self.precision_var.get()
        directory = self.dir_var.get()
        subdir = self.subdir_var.get()
        solver_name = self.solver_var.get()

        if not instance or not model or not precision or not directory:
            messagebox.showwarning("Missing Selection", "Please select directory, instance, model, and number type.")
            return

        if directory == "battery-original":
            self._log("'battery-original' is a legacy decimal dataset and is hidden from parity runs.", "warning")
            self._log("Use 'battery-new' or 'battery-java-aligned' for Java-compatible CLP parity.", "warning")
            messagebox.showwarning(
                "Legacy Dataset",
                "battery-original is legacy decimal data and can yield 0 stations by design.\n"
                "Use battery-new or battery-java-aligned for Java-compatible runs."
            )
            return

        subdir_str = f" ({subdir})" if subdir and subdir != "Root" else ""
        self._log(f"Starting execution: {instance} ({model}, {precision}) with {solver_name}{subdir_str}", "info")
        self.status_indicator.set_status("running", "Running...")
        self.run_btn.set_disabled(True)
        self.stop_btn.set_disabled(False)
        self.is_running = True

        self.execution_thread = threading.Thread(
            target=self._execute_test,
            args=(directory, instance, model, precision, solver_name, subdir if subdir != "Root" else None),
            daemon=True
        )
        self.execution_thread.start()

    def _execute_test(self, directory: str, instance: str, model: str, precision: str, solver_name: str, subdirectory: Optional[str] = None) -> None:
        """Execute test in background thread with proper stop signal handling."""
        try:
            self.stop_event.clear()

            # Get solver type from display name
            solver_type = SolverManager.get_solver_by_display_name(solver_name)
            if not solver_type:
                self._log(f"Invalid solver: {solver_name}", "error")
                return

            # Resolve model path using ProjectPaths
            if model == "RCLP":
                model_path = ProjectPaths.rclp_model_path(precision)
            else:  # Default to CLP
                model_path = ProjectPaths.clp_model_path(precision)

            if not model_path.exists():
                self._log(f"Model not found: {model_path}", "error")
                self.status_indicator.set_status("error", "Error")
                return

            # Run without a hard execution time limit from the UI.
            self.executor = MiniZincExecutor(str(model_path), timeout_seconds=None)

            data_path = Path(self.project_root) / "experiments" / "instances" / directory
            if subdirectory:
                instance_path = data_path / subdirectory / f"{instance}.dzn"
            else:
                instance_path = data_path / f"{instance}.dzn"

            if not instance_path.exists():
                self._log(f"Instance not found: {instance_path}", "error")
                self.status_indicator.set_status("error", "Error")
                return

            self._log(f"Executing: {model} [{precision}] ({solver_name}) on {instance}", "key")

            # execute() now returns tuple: (success: bool, result: Optional[Dict], execution_time: Optional[float])
            success, result_dict, exec_time = self.executor.execute(str(instance_path), solver_type)

            # Check if stop was requested during execution
            if self.stop_event.is_set():
                self._log("Execution stopped by user", "warning")
                self.status_indicator.set_status("idle", "Ready")
                return

            if success and result_dict:
                self._log(f"Execution completed successfully in {exec_time:.3f}s", "success")
                self.status_indicator.set_status("success", "Success")

                # Save results organized by test name and solver
                test_name = instance.replace('.dzn', '')

                # Build output directory including subdirectory structure
                output_base = Path(self.project_root) / "experiments" / "results" / "output" / directory
                if subdirectory:
                    output_base = output_base / subdirectory

                handler = ResultHandler(
                    str(output_base),
                    test_name=test_name,
                    model_type=precision
                )
                success_save, json_path, txt_path = handler.save_results(instance, result_dict, SolverManager.get_display_name(solver_type))

                if success_save:
                    self._log(f"Results saved to {Path(json_path).parent.name}/", "info")
            elif result_dict and result_dict.get('status') == 'unsatisfiable':
                self._log("Instance is UNSATISFIABLE", "warning")
                self.status_indicator.set_status("warning", "Unsatisfiable")

                # Save diagnostic
                diag_result = {
                    'test_instance': str(instance_path),
                    'model': str(model_path),
                    'error_message': "Instance is unsatisfiable",
                    'minizinc_stderr': '',
                    'execution_time': exec_time
                }
                handler = ResultHandler(str(Path(self.project_root) / "experiments" / "results"))
                handler.save_diagnostic(instance, diag_result, SolverManager.get_display_name(solver_type), "unsatisfiable")
            else:
                self._log(f"Execution failed with {solver_name}", "error")
                self.status_indicator.set_status("error", "Error")

        except Exception as e:
            self._log(f"Exception during execution: {e}", "error")
            self.status_indicator.set_status("error", "Error")
        finally:
            self.is_running = False
            self.run_btn.set_disabled(False)
            self.stop_btn.set_disabled(True)
            self.status_indicator.set_status("idle", "Ready")
            self.executor = None

    def _stop_execution(self) -> None:
        """Stop the currently running test execution by terminating subprocess."""
        if not self.is_running:
            return

        self._log("Stopping execution...", "warning")
        self.stop_event.set()

        if self.executor:
            self.executor.terminate()

        self.is_running = False
        self.run_btn.set_disabled(False)
        self.stop_btn.set_disabled(True)
        self.status_indicator.set_status("idle", "Ready")

    def _show_solver_info(self, event=None) -> None:
        """Display solver information in modal dialog."""
        solver_name = self.solver_var.get()
        solver_type = SolverManager.get_solver_by_display_name(solver_name)

        if not solver_type:
            messagebox.showerror("Error", "Unknown solver")
            return

        solver_info = SolverManager.get_solver_info(solver_type)

        # Create modal window
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{solver_info.display_name} Information")
        dialog.geometry("500x450")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center on parent
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 250
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 225
        dialog.geometry(f"+{x}+{y}")

        # Configure dialog colors
        dialog.configure(bg=self.theme_dict["bg_base"])

        # Header frame
        header = tk.Frame(dialog, bg=self.theme_dict["bg_surface"], height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # Title and close button
        title_frame = tk.Frame(header, bg=self.theme_dict["bg_surface"])
        title_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        tk.Label(
            title_frame,
            text=f"{solver_info.display_name}",
            font=("Arial", 14, "bold"),
            fg=self.theme_dict["text_primary"],
            bg=self.theme_dict["bg_surface"],
        ).pack(side=tk.LEFT)

        close_btn = tk.Label(
            title_frame,
            text="✕",
            font=("Arial", 16),
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_surface"],
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: dialog.destroy())

        # Content scrollable area
        content_frame = tk.Frame(dialog, bg=self.theme_dict["bg_base"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Description
        tk.Label(
            content_frame,
            text="Description",
            font=("Arial", 10, "bold"),
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_base"],
        ).pack(anchor="w")

        desc_text = tk.Text(
            content_frame,
            height=2,
            wrap=tk.WORD,
            bg=self.theme_dict["bg_elevated"],
            fg=self.theme_dict["text_primary"],
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5,
        )
        desc_text.insert(tk.END, solver_info.description)
        desc_text.configure(state="disabled")
        desc_text.pack(fill=tk.X, pady=(0, 12))

        # Strengths
        tk.Label(
            content_frame,
            text="Key Strengths",
            font=("Arial", 10, "bold"),
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_base"],
        ).pack(anchor="w")

        strengths_text = tk.Text(
            content_frame,
            height=3,
            wrap=tk.WORD,
            bg=self.theme_dict["bg_elevated"],
            fg=self.theme_dict["text_primary"],
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5,
        )
        strengths_text.insert(tk.END, "• " + "\n• ".join(solver_info.strengths))
        strengths_text.configure(state="disabled")
        strengths_text.pack(fill=tk.X, pady=(0, 12))

        # Use cases
        tk.Label(
            content_frame,
            text="Common Use Cases",
            font=("Arial", 10, "bold"),
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_base"],
        ).pack(anchor="w")

        use_text = tk.Text(
            content_frame,
            height=3,
            wrap=tk.WORD,
            bg=self.theme_dict["bg_elevated"],
            fg=self.theme_dict["text_primary"],
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5,
        )
        use_text.insert(tk.END, "• " + "\n• ".join(solver_info.use_cases))
        use_text.configure(state="disabled")
        use_text.pack(fill=tk.X, pady=(0, 12))

        # Commercial badge
        if solver_info.commercial:
            badge_frame = tk.Frame(content_frame, bg=self.theme_dict["bg_base"])
            badge_frame.pack(fill=tk.X)

            tk.Label(
                badge_frame,
                text="⚠ Commercial License Required",
                font=("Arial", 9),
                fg=self.theme_dict["warning"],
                bg=self.theme_dict["bg_elevated"],
                padx=8,
                pady=4,
                relief=tk.FLAT,
                bd=0,
            ).pack(side=tk.LEFT)

    @staticmethod
    def _safe_int(value: str, fallback: int) -> int:
        """Parse an integer from a text field, returning fallback on invalid input."""
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return fallback

