"""
Orchestrator Interface - Central System Center for CLP-RCLP Framework

Professional main interface providing unified entry point to all tools with
high-quality UI, dark/light theme support, and seamless navigation.

Authors: Andrey Quiceno and Juan Francesco García (AVISPA Team)
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Any, Literal, Optional
import subprocess
import sys
import webbrowser

from .themes import ThemeManager, get_theme_dict
from .components import SectionLabel, FlatButton, Divider
from .layouts import LayoutBuilder, LayoutConfig
from .tooltip import Tooltip
from ..config import TOOLS, VIRTUES, GITHUB_URL, VERSION
from core.shared.project_paths import ProjectPaths


class OrchestratorInterface(tk.Frame):
    """Professional system center interface with theme switching support."""

    def __init__(self, root: tk.Tk):
        """Initialize the Orchestrator interface."""
        super().__init__(root)
        self.root = root
        self.master = root
        self.pack(fill=tk.BOTH, expand=True)

        # Initialize theme system
        self._init_theme()

        # Setup window properties
        self.root.title(f"CLP-RCLP System Center v{VERSION}")
        self.root.geometry(f"{LayoutConfig.WINDOW_WIDTH}x{LayoutConfig.WINDOW_HEIGHT}")
        self.root.minsize(LayoutConfig.MIN_WIDTH, LayoutConfig.MIN_HEIGHT)
        self.root.resizable(True, True)
        self._center_window()
        self.configure(bg=self.theme_dict["bg_base"])

        # Find project root for file operations
        self.project_root = ProjectPaths.get_project_root()

        # Build UI
        self._build_ui()

    def _init_theme(self) -> None:
        """Initialize theme system and register observer for dynamic switching."""
        self.theme_dict = get_theme_dict("dark")
        ThemeManager.register_observer(self._on_theme_change)
        # Setup cleanup handler for observer deregistration
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _on_theme_change(self, mode: Literal["dark", "light"]) -> None:
        """Called when theme mode changes."""
        self.theme_dict = get_theme_dict(mode)
        self._refresh_ui_colors()

    def _on_destroy(self, event=None) -> None:
        """Cleanup handler called when widget is destroyed."""
        ThemeManager.unregister_observer(self._on_theme_change)

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
        """Build the complete user interface."""
        # Main container
        container = tk.Frame(self, bg=self.theme_dict["bg_base"])
        container.pack(fill=tk.BOTH, expand=True)

        # Build header
        self._build_header(container)

        # Build content
        content = LayoutBuilder.create_content_area(container, self.theme_dict)

        # Build scrollable content
        self._build_content(content)

        # Build footer
        self._build_footer(container)

    def _build_header(self, parent: tk.Widget) -> None:
        """Build header with title, subtitle, and theme toggle."""
        header = tk.Frame(parent, bg=self.theme_dict["bg_elevated"], height=LayoutConfig.HEADER_HEIGHT)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Left section: Accent bar + title + subtitle
        left = tk.Frame(header, bg=self.theme_dict["bg_elevated"])
        left.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Accent bar
        accent_bar = tk.Frame(left, bg=self.theme_dict["accent_primary"], width=4, height=40)
        accent_bar.pack(side=tk.LEFT, padx=(0, 12))
        accent_bar.pack_propagate(False)

        # Text section
        text_section = tk.Frame(left, bg=self.theme_dict["bg_elevated"])
        text_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_label = tk.Label(
            text_section,
            text="System Center",
            font=self.theme_dict["font_bold"],
            fg=self.theme_dict["text_primary"],
            bg=self.theme_dict["bg_elevated"]
        )
        title_label.pack(anchor=tk.W)

        subtitle_label = tk.Label(
            text_section,
            text="Framework for CLP/RCLP Model Testing",
            font=self.theme_dict["font_small"],
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_elevated"]
        )
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))

        # Right section: Theme toggle
        right = tk.Frame(header, bg=self.theme_dict["bg_elevated"])
        right.pack(side=tk.RIGHT, padx=20, pady=16)

        toggle_text = "🌙 Dark" if ThemeManager.get_mode() == "light" else "☀ Light"
        theme_btn = FlatButton(
            right,
            text=toggle_text,
            command=self._toggle_theme,
            theme=self.theme_dict,
            accent=False
        )
        theme_btn.pack()

    def _build_content(self, parent: tk.Widget) -> None:
        """Build main content area with scrolling."""
        # Create canvas with scrollbar
        canvas_frame = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        canvas = tk.Canvas(
            canvas_frame,
            bg=self.theme_dict["bg_base"],
            highlightthickness=0,
            relief=tk.FLAT
        )
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_dict["bg_base"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel for scrolling only within this scrollable area
        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_linux_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        def _unbind_mousewheel(_event=None):
            for widget in (canvas, scrollable_frame):
                try:
                    # widget may have been destroyed; guard against TclError
                    if getattr(widget, 'winfo_exists', lambda: False)():
                        widget.unbind("<MouseWheel>")
                        widget.unbind("<Button-4>")
                        widget.unbind("<Button-5>")
                except tk.TclError:
                    # Ignore errors when the underlying Tk window no longer exists
                    pass

        # Bind only to the canvas and scrollable_frame, not globally
        for widget in (canvas, scrollable_frame):
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>", _on_linux_mousewheel)
            widget.bind("<Button-5>", _on_linux_mousewheel)

        # Unbind on widget destruction
        canvas.bind("<Destroy>", _unbind_mousewheel, add="+")

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Build content inside scrollable frame
        self._build_information_section(scrollable_frame)
        self._build_virtues_section(scrollable_frame)
        self._build_tools_section(scrollable_frame)
        self._build_community_section(scrollable_frame)

    def _build_information_section(self, parent: tk.Widget) -> None:
        """Build information section at the top."""
        section = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        section.pack(fill=tk.X, padx=20, pady=(20, 24))

        # Title
        title = tk.Label(
            section,
            text="Information",
            font=self.theme_dict["font_bold"],
            fg=self.theme_dict["text_primary"],
            bg=self.theme_dict["bg_base"]
        )
        title.pack(anchor=tk.W, pady=(0, 12))

        # Description
        description = tk.Label(
            section,
            text=(
                "CLP-RCLP is a comprehensive optimization framework for electric vehicle charging "
                "logistics. Access three powerful tools: convert battery schedules to constraint models, "
                "generate synthetic test instances, and execute optimization with multiple solvers. "
                "Use the System Center to manage all operations with an intuitive interface."
            ),
            font=self.theme_dict["font_ui"],
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_base"],
            justify=tk.LEFT,
            wraplength=1000
        )
        description.pack(anchor=tk.W, fill=tk.X)

    def _build_virtues_section(self, parent: tk.Widget) -> None:
        """Build system features in 2x2 grid layout."""
        section = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        section.pack(fill=tk.X, padx=0, pady=(0, 20))

        # Section label
        label_frame = tk.Frame(section, bg=self.theme_dict["bg_base"])
        label_frame.pack(fill=tk.X, padx=20, pady=(0, 12))
        SectionLabel(label_frame, "System Features", self.theme_dict).pack(fill=tk.X)

        # Grid container (2x2)
        grid_frame = tk.Frame(section, bg=self.theme_dict["bg_base"])
        grid_frame.pack(fill=tk.X, padx=20, pady=0)

        # Create grid of virtue cards
        for idx, virtue in enumerate(VIRTUES):
            row = idx // 2
            col = idx % 2
            card_frame = tk.Frame(grid_frame, bg=self.theme_dict["bg_base"])
            card_frame.grid(row=row, column=col, sticky="nsew", padx=(0, 12 if col == 0 else 0), pady=(0, 12))

            # Make both columns have equal weight
            grid_frame.columnconfigure(0, weight=1)
            grid_frame.columnconfigure(1, weight=1)

            self._create_virtue_card(card_frame, virtue, idx)

    def _create_virtue_card(self, parent: tk.Widget, virtue: Dict[str, str], idx: int) -> None:
        """Create a virtue card for grid layout."""
        card = tk.Frame(
            parent,
            bg=self.theme_dict["bg_elevated"],
            relief=tk.FLAT,
            borderwidth=1
        )
        card.pack(fill=tk.BOTH, expand=True)

        # Accent indicator
        accent = tk.Frame(
            card,
            bg=self.theme_dict["accent_primary"],
            width=4,
            height=80
        )
        accent.pack(side=tk.LEFT)
        accent.pack_propagate(False)

        # Content
        content = tk.Frame(card, bg=self.theme_dict["bg_elevated"])
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        tk.Label(
            content,
            text=virtue["title"],
            font=self.theme_dict["font_bold"],
            fg=self.theme_dict["text_primary"],
            bg=self.theme_dict["bg_elevated"],
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        tk.Label(
            content,
            text=virtue["description"],
            font=self.theme_dict["font_ui"],
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_elevated"],
            justify=tk.LEFT,
            wraplength=400
        ).pack(anchor=tk.W, pady=(4, 0))

    def _build_tools_section(self, parent: tk.Widget) -> None:
        """Build tools navigation section."""
        section = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        section.pack(fill=tk.X, padx=0, pady=(0, 20))

        # Section label
        label_frame = tk.Frame(section, bg=self.theme_dict["bg_base"])
        label_frame.pack(fill=tk.X, padx=20, pady=(0, 12))
        SectionLabel(label_frame, "Available Tools", self.theme_dict).pack(fill=tk.X)

        # Tools cards
        for tool_key, tool_info in TOOLS.items():
            self._create_tool_card(section, tool_key, tool_info)

    def _create_tool_card(self, parent: tk.Widget, tool_key: str, tool_info: Dict[str, str]) -> None:
        """Create a tool navigation card."""
        card = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        card.pack(fill=tk.X, padx=20, pady=8)

        # Card background
        card_bg = tk.Frame(
            card,
            bg=self.theme_dict["bg_elevated"],
            relief=tk.FLAT,
            borderwidth=1
        )
        card_bg.pack(fill=tk.X)

        # Content
        content = tk.Frame(card_bg, bg=self.theme_dict["bg_elevated"])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Title and description
        info_frame = tk.Frame(content, bg=self.theme_dict["bg_elevated"])
        info_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        tk.Label(
            info_frame,
            text=tool_info["title"],
            font=self.theme_dict["font_bold"],
            fg=self.theme_dict["text_primary"],
            bg=self.theme_dict["bg_elevated"]
        ).pack(anchor=tk.W)

        tk.Label(
            info_frame,
            text=tool_info["description"],
            font=self.theme_dict["font_ui"],
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_elevated"],
            wraplength=750,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(4, 0))

        # Launch button
        btn_frame = tk.Frame(content, bg=self.theme_dict["bg_elevated"])
        btn_frame.pack(side=tk.RIGHT, padx=(16, 0))

        launch_btn = FlatButton(
            btn_frame,
            text="Launch",
            command=lambda: self._launch_tool(tool_key),
            theme=self.theme_dict,
            accent=True
        )
        launch_btn.pack()

        Tooltip(launch_btn, f"Open {tool_info['title']}", self.theme_dict)

    def _build_community_section(self, parent: tk.Widget) -> None:
        """Build community invitation section."""
        section = tk.Frame(parent, bg=self.theme_dict["bg_base"])
        section.pack(fill=tk.X, padx=20, pady=20)

        card = tk.Frame(
            section,
            bg=self.theme_dict["bg_elevated"],
            relief=tk.FLAT,
            borderwidth=1
        )
        card.pack(fill=tk.X)

        # Accent bar
        accent = tk.Frame(
            card,
            bg=self.theme_dict["accent_primary"],
            width=4,
            height=100
        )
        accent.pack(side=tk.LEFT)
        accent.pack_propagate(False)

        # Content
        content = tk.Frame(card, bg=self.theme_dict["bg_elevated"])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        tk.Label(
            content,
            text="Join Our Community",
            font=self.theme_dict["font_bold"],
            fg=self.theme_dict["text_primary"],
            bg=self.theme_dict["bg_elevated"]
        ).pack(anchor=tk.W)

        tk.Label(
            content,
            text="Contribute to the CLP-RCLP optimization framework. Help us improve research tools and solver integration.",
            font=self.theme_dict["font_ui"],
            fg=self.theme_dict["text_secondary"],
            bg=self.theme_dict["bg_elevated"],
            wraplength=850,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(4, 12))

        # Button
        github_btn = FlatButton(
            content,
            text="Visit GitHub Repository",
            command=self._open_github,
            theme=self.theme_dict,
            accent=False
        )
        github_btn.pack(anchor=tk.W)

        Tooltip(github_btn, "Open project repository", self.theme_dict)

    def _build_footer(self, parent: tk.Widget) -> None:
        """Build footer with version and info."""
        LayoutBuilder.create_footer(
            parent,
            left_text="CLP-RCLP Research Framework",
            right_text=f"v{VERSION} | Multi-Solver Support",
            theme=self.theme_dict
        )

    def _launch_tool(self, tool_key: str) -> None:
        """
        Launch specified tool using dynamic path resolution.

        Uses ToolPathResolver to find tool scripts regardless of system
        configuration or directory naming conventions.

        Args:
            tool_key: Tool identifier ('converter', 'generator', 'runner')
        """
        try:
            # Use direct path resolution without imports
            from pathlib import Path
            import subprocess

            # Find tool script dynamically
            tool_path = self._resolve_tool_path(tool_key)

            if tool_path and tool_path.exists():
                # Use sys.executable to ensure same interpreter as orchestrator
                subprocess.Popen([sys.executable, str(tool_path)])
                # Fully close the orchestrator window after launching the tool
                self.root.destroy()
            else:
                print(f"Tool script not found for {tool_key}: {tool_path}")
        except Exception as e:
            import traceback
            print(f"Error launching tool {tool_key}: {e}")
            traceback.print_exc()

    def _resolve_tool_path(self, tool_name: str) -> Path:
        """
        Resolve path to a tool script dynamically.

        Searches for the tool in the core directory structure.

        Args:
            tool_name: Tool identifier ('converter', 'generator', 'runner')

        Returns:
            Path: Path to the tool script if found
        """
        from pathlib import Path

        # Strategy 1: core/<tool_name>/<tool_name>.py
        path = self.project_root / "core" / tool_name / f"{tool_name}.py"
        if path.exists():
            return path

        # Strategy 2: <tool_name>/<tool_name>.py (legacy)
        path = self.project_root / tool_name / f"{tool_name}.py"
        if path.exists():
            return path

        # Return primary path for error reporting
        return self.project_root / "core" / tool_name / f"{tool_name}.py"

    def _open_github(self) -> None:
        """Open GitHub repository in browser."""
        webbrowser.open(GITHUB_URL)

    def _toggle_theme(self) -> None:
        """Toggle between dark and light theme."""
        current_mode = ThemeManager.get_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ThemeManager.set_mode(new_mode)

    def _refresh_ui_colors(self) -> None:
        """Refresh UI colors when theme changes."""
        # Destroy all widgets
        for widget in self.winfo_children():
            widget.destroy()
        # Rebuild UI with new theme
        self._build_ui()
