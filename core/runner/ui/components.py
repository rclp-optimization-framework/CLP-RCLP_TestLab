"""
Components Module - Reusable custom Tkinter widgets.
"""

import tkinter as tk
from typing import Callable, Optional, Dict, Any

class SectionLabel(tk.Frame):
    """Labeled section header with left accent bar."""
    def __init__(self, parent: tk.Widget, text: str, theme: Dict[str, Any], **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=theme["bg_base"], highlightthickness=0)
        accent_bar = tk.Frame(self, bg=theme["accent_primary"], width=4, height=24)
        accent_bar.pack(side=tk.LEFT, padx=(0, 12), pady=0)
        accent_bar.pack_propagate(False)
        label = tk.Label(self, text=text.upper(), font=theme["font_section"], 
                        fg=theme["text_secondary"], bg=theme["bg_base"], anchor=tk.W)
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)

class Divider(tk.Frame):
    """Simple horizontal divider line."""
    def __init__(self, parent: tk.Widget, theme: Dict[str, Any], **kwargs):
        super().__init__(parent, bg=theme["border_normal"], height=1, **kwargs)
        self.pack_propagate(False)

class FlatButton(tk.Frame):
    """Modern flat button without 3D effects."""
    def __init__(self, parent: tk.Widget, text: str, command: Optional[Callable] = None,
                theme: Optional[Dict[str, Any]] = None, accent: bool = False, disabled: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=theme["bg_base"], highlightthickness=0)
        self._theme = theme
        self._command = command
        self._disabled = disabled
        self._accent = accent

        if accent:
            self._normal_bg = theme["accent_primary"]
            self._normal_fg = "#FFFFFF"
            self._hover_bg = theme["accent_glow"]
        else:
            self._normal_bg = theme["bg_elevated"]
            self._normal_fg = theme["text_primary"]
            self._hover_bg = theme["bg_hover"]

        self._disabled_bg = theme["bg_surface"]
        self._disabled_fg = theme["text_muted"]

        self.btn = tk.Label(
            self, text=text, font=theme["font_bold"],
            fg=self._normal_fg if not disabled else self._disabled_fg,
            bg=self._normal_bg if not disabled else self._disabled_bg,
            padx=16, pady=0, cursor="hand2" if not disabled else "arrow", anchor=tk.CENTER
        )
        self.btn.pack(fill=tk.BOTH, expand=True)

        if not disabled:
            self.btn.bind("<Button-1>", self._on_click)
            self.btn.bind("<Enter>", self._on_enter)
            self.btn.bind("<Leave>", self._on_leave)

    def _on_click(self, event):
        if self._command:
            self._command()

    def _on_enter(self, event):
        if not self._disabled:
            self.btn.configure(bg=self._hover_bg)

    def _on_leave(self, event):
        if not self._disabled:
            self.btn.configure(bg=self._normal_bg)

    def set_disabled(self, disabled: bool):
        self._disabled = disabled
        if disabled:
            self.btn.configure(bg=self._disabled_bg, fg=self._disabled_fg, cursor="arrow")
        else:
            self.btn.configure(bg=self._normal_bg, fg=self._normal_fg, cursor="hand2")

class StatusIndicator(tk.Frame):
    """Animated status indicator with label."""
    def __init__(self, parent: tk.Widget, text: str = "Ready", theme: Optional[Dict[str, Any]] = None):
        super().__init__(parent, bg=theme["bg_base"], highlightthickness=0)
        self._theme = theme
        self._status = "idle"

        self.dot = tk.Canvas(self, width=12, height=12, bg=theme["bg_base"], 
                           highlightthickness=0, relief=tk.FLAT)
        self.dot.pack(side=tk.LEFT, padx=(0, 8))

        self.label = tk.Label(self, text=text, font=theme["font_ui"],
                            fg=theme["text_secondary"], bg=theme["bg_base"])
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._update_dot()

    def set_status(self, status: str, text: str = None) -> None:
        self._status = status
        if text:
            self.label.configure(text=text)
        self._update_dot()

    def _update_dot(self):
        self.dot.delete("all")
        status_colors = {
            "idle": self._theme["text_muted"],
            "running": self._theme["accent_primary"],
            "success": self._theme["success"],
            "error": self._theme["error"],
            "warning": self._theme["warning"],
        }
        color = status_colors.get(self._status, self._theme["text_muted"])
        self.dot.create_oval(2, 2, 10, 10, fill=color, outline=color)
