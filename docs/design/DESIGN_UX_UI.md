# UX/UI Implementation Guide

## Design Philosophy

The CLP-RCLP framework follows professional UX/UI principles to create a seamless, intuitive user experience across all tools.

## Color Scheme & Typography

### Dark Mode Palette

```python
DARK_PALETTE = {
    "bg_base": "#0D0F14",          # Main background
    "bg_surface": "#141720",        # Cards, panels
    "bg_elevated": "#1C2030",       # Elevated elements
    "bg_hover": "#232840",          # Hover states
    
    "accent_primary": "#3D8EF5",    # Main accent (buttons, toggles)
    "accent_dim": "#1F4A8C",        # Disabled states
    "accent_glow": "#5AAEFF",       # Highlights
    
    "success": "#22C55E",           # Success messages
    "warning": "#F59E0B",           # Warnings
    "error": "#EF4444",             # Errors
    
    "text_primary": "#E8ECF4",      # Main text
    "text_secondary": "#8896B3",    # Secondary text
    "text_muted": "#4A5568",        # Muted text
    "text_code": "#A8C4F0",         # Code/monospace
}
```

### Light Mode Palette

```python
LIGHT_PALETTE = {
    "bg_base": "#F8F9FA",           # Main background
    "bg_surface": "#FFFFFF",        # Cards, panels
    "bg_elevated": "#F1F3F5",       # Elevated elements
    "bg_hover": "#E9ECEF",          # Hover states
    
    "accent_primary": "#2E5FCC",    # Main accent
    "accent_dim": "#5A7FD4",        # Disabled states
    "accent_glow": "#5A9FFF",       # Highlights
    
    "success": "#27AE60",           # Success messages
    "warning": "#D68910",           # Warnings
    "error": "#E74C3C",             # Errors
    
    "text_primary": "#1A1A1A",      # Main text
    "text_secondary": "#555555",    # Secondary text
    "text_muted": "#999999",        # Muted text
    "text_code": "#003D99",         # Code/monospace
}
```

## Typography System

### Font Families

```python
class Typography:
    ui_normal = ("Segoe UI", 10)      # Regular UI text
    ui_bold = ("Segoe UI", 10, "bold") # Bold text
    ui_small = ("Segoe UI", 9)        # Small/secondary text
    
    bold = ("Arial", 14, "bold")      # Headings
    bold_small = ("Arial", 11, "bold") # Section titles
    
    mono = ("Consolas", 9)            # Code/monospace
    mono_bold = ("Consolas", 9, "bold")
```

### Font Sizes & Uses

| Size | Use Case | Example |
|------|----------|---------|
| 9pt | Captions, secondary info | Footer text, small labels |
| 10pt | Default UI text | Buttons, form fields, normal text |
| 11pt | Section headers | "Configuration", "Output Log" |
| 14pt | Page titles | "CLP-RCLP TEST RUNNER" |
| 18pt | Major headings | Back button (<), status icons |

## Component Design

### Header Layout (All Windows)

```
┌─────────────────────────────────────────────────────────────┐
│  [<] System Center  ← Accent bar   [Status] [Theme Toggle]  │
│         " Framework for CLP/RCLP Model Testing"             │
└─────────────────────────────────────────────────────────────┘
```

**Components**:
- **Left Side**: Back button (if not Orchestrator) + accent bar + title
- **Right Side**: Status indicator + Theme toggle (☀/🌙)
- **Height**: 70px (Orchestrator) / 60px (Tools)
- **Padding**: 20px horizontal, 15-16px vertical

### Footer Layout (All Windows)

```
┌─────────────────────────────────────────────────────────────┐
│ "Description and Credits"          "v2.1.0 | System Center"  │
└─────────────────────────────────────────────────────────────┘
```

**Components**:
- **Left**: Project description
- **Right**: Version and info
- **Height**: 40px
- **Padding**: 12px vertical, 20px horizontal

### Button Design (FlatButton)

```
┌─────────────────────┐
│   LAUNCH CONVERTER  │  ← Accent color, bold
└─────────────────────┘
```

**Accent Button** (Primary actions):
```python
accent=True
background: accent_primary
foreground: text_primary (white/dark)
hover: accent_dim
padding: 10px 20px
```

**Flat Button** (Secondary actions):
```python
accent=False
background: transparent/surface
foreground: text_primary
border: 1px border_normal
hover: bg_hover
padding: 8px 16px
```

### Card/Panel Design

```
┌──────────────────────────────────────┐ ← 1px border (border_normal)
│ ┌────┐ Title                         │
│ │ 4  │ Description line 1             │
│ │ px │ Description line 2             │
│ └────┘                                │
│       Padding: 12px                   │
└──────────────────────────────────────┘
  ↑ accent bar (left side)
```

**Card Properties**:
- **Background**: bg_elevated
- **Border**: 1px, border_normal color
- **Padding**: 12px internal
- **Accent Bar**: 4px left border, accent_primary color
- **Border Radius**: 0 (flat design)

### Text Input Design

```
┌─────────────────────────────────┐ ← border_active on focus
│ Select directory...              │
└─────────────────────────────────┘
```

**Properties**:
- **Background**: bg_elevated
- **Foreground**: text_primary
- **Border**: border_normal (focus: border_active)
- **Padding**: 10px 6px
- **Font**: font_ui

## Layout Patterns

### Two-Panel Layout (Runner)

```
┌─────────────────────────────────────────────────────┐
│                   HEADER                             │
├──────────────────┬──────────────────────────────────┤
│                  │                                  │
│   CONFIG PANEL   │        RESULTS PANEL             │
│   (300px width)  │   (Fill remaining space)         │
│                  │                                  │
│  • Directory     │  ┌──────────────────────────┐   │
│  • Instance      │  │ OUTPUT LOG               │   │
│  • Solver        │  │                          │   │
│  • Run / Stop    │  │ [execution output...]    │   │
│                  │  │                          │   │
├──────────────────┴──────────────────────────────────┤
│                   FOOTER                             │
└─────────────────────────────────────────────────────┘
```

**Left Panel**:
- Fixed width: 300px
- Scrollable content
- Card-based sections with dividers

**Right Panel**:
- Flexible width (fill available space)
- Log display area
- Status indicators

### Single-Column Layout (Orchestrator)

```
┌─────────────────────────────────────────────────────┐
│                   HEADER                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Information Section]                              │
│                                                     │
│  [System Features Grid - 2x2]                       │
│                                                     │
│  [Available Tools - Card List]                      │
│    ┌────────────────────────────────────────┐      │
│    │ Converter ← [Launch]                   │      │
│    │ Convert battery schedules...           │      │
│    └────────────────────────────────────────┘      │
│                                                     │
│  [Community Section]                                │
│                                                     │
├─────────────────────────────────────────────────────┤
│                   FOOTER                             │
└─────────────────────────────────────────────────────┘
```

**Scrollable Areas**:
- Main content is vertically scrollable
- Comfortable vertical padding (20px between sections)
- Grid layout for features (2 columns, 2 rows)

## Interaction Patterns

### Button Hover States

```
Before Hover:           On Hover:
┌──────────────┐       ┌──────────────┐
│ LAUNCH TOOL  │  →    │ LAUNCH TOOL  │ ← bg_hover
└──────────────┘       └──────────────┘
```

### Focus States (Form Fields)

```
Normal:                 Focused:
┌──────────────┐       ┌──────────────┐
│ Select...    │  →    │ Select...    │ ← border_active
└──────────────┘       └──────────────┘
```

### Status Indicators

```
Ready:      ● (success color)
Running:    ◐ (accent_glow color, animated)
Error:      ● (error color)
```

## Theme Switching Implementation

### Dynamic Theme Change

```python
# User clicks theme toggle button
ThemeManager.set_mode("light")  # from "dark"

# All registered observers are notified
for observer in ThemeManager.observers:
    observer("light")  # _on_theme_change is called

# Each window rebuilds its UI
self._refresh_ui_colors()
```

### Observer Pattern

```python
class OrchestratorInterface:
    def _init_theme(self):
        self.theme_dict = get_theme_dict("dark")
        ThemeManager.register_observer(self._on_theme_change)
    
    def _on_theme_change(self, mode: str):
        self.theme_dict = get_theme_dict(mode)
        self._refresh_ui_colors()  # Rebuild UI
```

## Responsive Design

### Window Sizing

```python
class LayoutConfig:
    WINDOW_WIDTH = 1400     # Orchestrator width
    WINDOW_HEIGHT = 850     # Orchestrator height
    MIN_WIDTH = 800         # Minimum width
    MIN_HEIGHT = 600        # Minimum height
```

**Breakpoints**:
- **Small**: < 800px (desktop tablets, narrow windows)
- **Medium**: 800-1200px (standard desktop)
- **Large**: > 1200px (wide monitors)

### Padding & Spacing

```python
# Consistent spacing system
SPACING = {
    "xs": 4,      # Minimal gaps
    "sm": 8,      # Small gaps
    "md": 12,     # Medium (default card padding)
    "lg": 16,     # Large (header/footer padding)
    "xl": 20,     # Extra large (section margins)
}
```

## Accessibility Guidelines

### Contrast Ratios

- **Text on Background**: Minimum 4.5:1 (WCAG AA)
- **UI Components**: Minimum 3:1 (WCAG A)

**Dark Mode**:
- Primary text (#E8ECF4) on base (#0D0F14): ~13:1 ✓
- Secondary text (#8896B3) on base (#0D0F14): ~4.5:1 ✓

**Light Mode**:
- Primary text (#1A1A1A) on base (#F8F9FA): ~15:1 ✓
- Secondary text (#555555) on base (#F8F9FA): ~7:1 ✓

### Focus Indicators

```python
# Clear visual focus indicators for keyboard navigation
selectcolor=self.theme_dict["accent_primary"]  # RadioButton
border=self.theme_dict["border_active"]        # Input focus
```

## Code Example: Button Implementation

```python
class FlatButton:
    """Professional flat button component."""
    
    def __init__(self, parent, text, command=None, theme=None, accent=False):
        self.button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=theme["accent_primary"] if accent else theme["bg_surface"],
            fg=theme["text_primary"],
            border=0 if accent else 1,
            borderwidth=1 if accent else 1,
            padx=20 if accent else 16,
            pady=10 if accent else 8,
            font=theme["font_ui"],
            cursor="hand2",
            activebackground=theme["accent_dim"] if accent else theme["bg_hover"],
            activeforeground=theme["text_primary"],
            relief="flat",
        )
        self.button.pack()
```

## Best Practices

### Do ✓

- Use consistent padding/spacing throughout
- Provide clear visual feedback on interactions
- Include helpful tooltips on complex elements
- Test both dark and light themes
- Maintain consistent typography
- Use color meaningfully (success=green, error=red)

### Don't ✗

- Mix color schemes in same window
- Use too many font sizes/weights
- Exceed 4px accent bar width
- Use borders on all elements (use sparingly)
- Force specific window size (allow resizing)
- Hide important info under hover/click

## Testing Checklist

- [ ] Theme toggle works in Orchestrator
- [ ] Back button works in all tools
- [ ] Hover states are visible
- [ ] Text is readable (high contrast)
- [ ] Layout is responsive
- [ ] All buttons are clickable (min 44px height)
- [ ] No visual glitches on theme switch
- [ ] Scrollbars are styled consistently

---

**Author**: AVISPA Research Team  
**Date**: April 2026  
**Version**: 2.1.0
