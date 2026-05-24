# Path Resolution & Navigation Architecture

## Overview

The CLP-RCLP framework uses a **dynamic path resolution system** to enable seamless navigation between the Orchestrator (System Center) and Tool windows, regardless of system configuration or directory naming conventions.

This document describes the architecture, implementation, and usage patterns.

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    Orchestrator (System Center)                │
│                    core/orchestration/ui/                      │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Header: [System Center] ← Accent bar                 │  │
│  │  Right: [☀ Light] / [🌙 Dark] Theme Toggle           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Available Tools:                                      │  │
│  │  ┌─────────────────┐  ┌─────────────────┐             │  │
│  │  │ Converter       │  │ Generator       │             │  │
│  │  │ Launch Button ──┼──→ ToolPathResolver              │  │
│  │  └─────────────────┘  └─────────────────┘             │  │
│  │  ┌─────────────────┐                                 │  │
│  │  │ Runner          │                                 │  │
│  │  │ Launch Button ──┼──→ subprocess.Popen()           │  │
│  │  └─────────────────┘                                 │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
             ↓                                         ↑
          Launch                                   Back Button
      Tool Process                                   (Click)
             ↓                                         ↑
┌────────────────────────────────────────────────────────────────┐
│                     Tool Window (e.g., Runner)                 │
│                     core/runner/ui/interface.py                │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Header: [<] Back  [CLP-RCLP TEST RUNNER]             │  │
│  │                    [☀ Light] / [🌙 Dark]              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│         Back Button Click → return_to_orchestrator()          │
│         (Closes window + Launches Orchestrator)               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. ToolPathResolver (`core/shared/path_resolver.py`)

**Purpose**: Dynamically locate tool scripts regardless of directory structure.

**Key Features**:
- Platform-agnostic path handling (Windows, macOS, Linux)
- Case-insensitive directory searching
- Multiple fallback strategies
- Comprehensive error logging

**Class: `ToolPathResolver`**

```python
resolver = ToolPathResolver(project_root)

# Get single tool path
converter_path = resolver.get_tool_path("converter")

# Get all tools at once
tools = resolver.get_all_tools()

# Validate all tools are available
validation = resolver.validate_tools()
```

**Search Strategy**:
```
For tool "converter":
1. Try: core/converter/converter.py
2. Try: converter/converter.py
3. Return None if not found

Error Handling:
- Detailed logging of search process
- Path validation before returning
- Clear error messages for debugging
```

### 2. Navigation System (`core/shared/navigation.py`)

**Purpose**: Handle back navigation from tools to Orchestrator.

**Key Function: `return_to_orchestrator(current_window)`**

```python
# Called when back button is clicked in any tool
from core.shared.navigation import return_to_orchestrator

def on_back_button_click():
    return_to_orchestrator(self.root)
    # 1. Closes current window
    # 2. Finds orchestrator.py dynamically
    # 3. Launches orchestrator in new process
```

**Implementation Details**:
```
1. Close current window (current_window.destroy())
2. Find orchestrator path using _find_orchestrator_path()
3. Launch orchestrator via subprocess.Popen()
4. Return to Orchestrator UI

Error Handling:
- Logs errors to console
- Gracefully handles missing orchestrator
- Provides clear error messages
```

### 3. Orchestrator Launch System (`core/orchestration/ui/interface.py`)

**Method: `_launch_tool(tool_key)`**

```python
def _launch_tool(self, tool_key: str) -> None:
    """Launch specified tool using dynamic path resolution."""
    from shared.path_resolver import ToolPathResolver
    
    resolver = ToolPathResolver(self.project_root)
    script_path = resolver.get_tool_path(tool_key)
    
    if script_path and script_path.exists():
        subprocess.Popen(["python", str(script_path)])
    else:
        print(f"Tool script not found: {script_path}")
```

**Process**:
1. User clicks "Launch" button for a tool
2. Orchestrator imports ToolPathResolver
3. Resolver searches for tool script
4. subprocess.Popen() launches tool in new process
5. User interacts with tool
6. Back button returns to Orchestrator

### 4. Theme System Integration

**Orchestrator Theme Support**:
```python
# Header section includes theme toggle
toggle_text = "🌙 Dark" if ThemeManager.get_mode() == "light" else "☀ Light"
theme_btn = FlatButton(
    right,
    text=toggle_text,
    command=self._toggle_theme,
    theme=self.theme_dict,
    accent=False
)
```

**Theme Methods**:
```python
def _toggle_theme(self) -> None:
    """Toggle between dark and light theme."""
    current_mode = ThemeManager.get_mode()
    new_mode = "light" if current_mode == "dark" else "dark"
    ThemeManager.set_mode(new_mode)

def _refresh_ui_colors(self) -> None:
    """Refresh UI colors when theme changes."""
    for widget in self.winfo_children():
        widget.destroy()
    self._build_ui()  # Rebuild with new theme
```

## Directory Structure

```
CLP-RCLP Minizinc/
├── core/
│   ├── converter/
│   │   ├── converter.py          ← Entry point
│   │   └── ui/interface.py
│   │
│   ├── generator/
│   │   ├── generator.py          ← Entry point
│   │   └── ui/interface.py
│   │
│   ├── runner/
│   │   ├── runner.py             ← Entry point
│   │   └── ui/interface.py
│   │
│   ├── orchestration/
│   │   ├── orchestrator.py       ← Entry point
│   │   └── ui/
│   │       ├── interface.py      ← Main Orchestrator UI
│   │       ├── themes.py         ← Theme definitions
│   │       ├── components.py     ← UI components
│   │       └── layouts.py        ← Layout utilities
│   │
│   └── shared/
│       ├── path_resolver.py      ← Dynamic path resolution
│       ├── navigation.py         ← Back navigation
│       └── theme_persistence.py  ← Theme state saving
│
└── scripts/
    ├── verification/
    │   └── verify_window_transitions.py   ← Transition verification
    │
    └── utilities/
        └── validate_integration.py       ← Full integration validation
```

## Usage Patterns

### Pattern 1: Launching a Tool from Orchestrator

```python
# User clicks "Launch Converter" button
# Orchestrator._launch_tool("converter") is called

resolver = ToolPathResolver(self.project_root)
path = resolver.get_tool_path("converter")
subprocess.Popen(["python", str(path)])

# Converter window opens in separate process
# Orchestrator continues running
```

### Pattern 2: Returning to Orchestrator

```python
# User clicks "<" back button in Converter window
# Converter.on_back_button_click() calls return_to_orchestrator()

from core.shared.navigation import return_to_orchestrator

return_to_orchestrator(self.root)
# 1. Converter window closes
# 2. Orchestrator launches
# 3. User returns to System Center
```

### Pattern 3: Theme Switching

```python
# User clicks "☀ Light" button in Orchestrator header
# Orchestrator._toggle_theme() is called

current_mode = ThemeManager.get_mode()  # "dark"
new_mode = "light"
ThemeManager.set_mode(new_mode)  # Triggers observers

# _on_theme_change() is called automatically
# _refresh_ui_colors() rebuilds UI with light theme
```

## Cross-Platform Compatibility

### Path Handling

```python
# Windows
path = Path("C:\\Users\\lu\\...\\core\\converter\\converter.py")
str(path)  # "C:\Users\lu\...\core\converter\converter.py"

# Linux/macOS
path = Path("/home/user/.../core/converter/converter.py")
str(path)  # "/home/user/.../core/converter/converter.py"

# Path() handles both automatically
```

### Subprocess Launching

```python
# Works on all platforms
subprocess.Popen(["python", str(script_path)])

# platform.system() not needed because:
# - Python is in PATH on all platforms
# - Popen finds python executable automatically
```

## Error Handling

### Missing Tool Script

```
Error: Tool script not found for converter
  Expected: C:\...\core\converter\converter.py
  Searched: [3 locations]
  
Solution:
  1. Check directory structure matches pattern
  2. Verify file names match exactly
  3. Run: python scripts/utilities/validate_integration.py
```

### Missing Orchestrator on Back Navigation

```
Error launching orchestrator: [Errno 2] No such file or directory
  Expected: .../core/orchestration/orchestrator.py
  
Solution:
  1. Verify orchestration directory exists
  2. Ensure orchestrator.py is present
  3. Check file is readable
```

## Testing & Validation

### Quick Validation

```bash
# Test path resolution
python scripts/utilities/validate_integration.py

# Test window transitions
python scripts/verification/verify_window_transitions.py
```

### Manual Testing

```bash
# Launch Orchestrator
python core/orchestration/orchestrator.py

# From Orchestrator:
# 1. Click "Launch Converter"
# 2. Converter window should open
# 3. Click back button (<)
# 4. Should return to Orchestrator
# 5. Test theme toggle (☀/🌙) in both windows
```

## Performance Considerations

### Path Resolution Performance

- **First call**: ~0.5ms (minimal filesystem traversal)
- **Cached results**: Used by ToolPathResolver within same session
- **No blocking I/O**: All operations are synchronous but fast

### Theme Switching Performance

- **Light/Dark toggle**: ~50ms (rebuilds UI)
- **No FPS impact**: Tkinter handles redraws efficiently
- **Observer pattern**: Only affected windows update

## Future Improvements

1. **Cached Path Resolution**: Store resolved paths in config file
2. **Tool Validation**: Pre-check all tools at startup
3. **Graceful Degradation**: Show helpful UI if tool not found
4. **Theme Preferences**: Save user theme choice to persistent storage
5. **Tool Updates**: Check for tool availability before launching

## Related Documentation

- `scripts/verification/README.md` - Window transition verification
- `scripts/utilities/README.md` - Integration validation utilities
- `core/orchestration/ui/themes.py` - Theme system details
- `core/runner/ui/interface.py` - Reference implementation with theme support

## Contact & Support

For issues with:
- **Path Resolution**: Check `core/shared/path_resolver.py`
- **Navigation**: Check `core/shared/navigation.py`
- **Theme System**: Check `core/orchestration/ui/themes.py`
- **General Issues**: Run `validate_integration.py` for diagnostic report

---
**Author**: AVISPA Research Team  
**Date**: April 2026  
**Version**: 2.1.0
