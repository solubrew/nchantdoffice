# NchantdOffice Coding Standards

**Last Updated**: 2026-03-05

---

## Overview

NchantdOffice is a Qt-based office productivity application that extends the **nchantrs** core library with a PyQt5/PyQt6 GUI. It provides document management, multi-pane interfaces, and integrates with the **Pyffice** document widget library.

---

## Project Architecture

### Dependencies

| Package | Purpose |
|---------|---------|
| **nchantrs** | Core data model, storage, security, API |
| **pyffice** | Document widgets (notebooks, spreadsheets, etc.) |
| **condor** | Configuration management |
| **pycurity** | Security utilities |
| **micromole + squirl** | Data processing |

### Component Structure

```
nchantdoffice/
├── nchantdoffice/          # Main package
│   ├── __main__.py         # Entry point (GUI launch)
│   ├── cli.py              # CLI commands
│   ├── nchantdoffice.py    # Main application class
│   ├── views.py            # View controllers
│   ├── models.py           # Data models
│   ├── widgets/            # Qt widgets
│   │   ├── documents/      # Document types (Pyffice integration)
│   │   ├── tabs.py         # Tab management
│   │   ├── trees.py        # Tree navigation
│   │   ├── toolboxes.py    # Tool panels
│   │   └── controls/       # UI controls (toolbars, etc.)
│   ├── dialogs/            # Dialog windows
│   ├── wizards/            # Setup wizards
│   ├── menus/              # Context menus
│   └── utilities/          # Helper functions
├── test_nchantdoffice/     # Test suite
└── pyproject.toml          # Package configuration
```

---

## Coding Conventions

### 1. Class Naming

- **NchantdOfficeXxx** - Main application classes (NchantdOfficeApplication, NchantdOfficeTabs)
- **NchantdXxxWidget** - Custom Qt widgets (NchantdApplicationToolBox)
- **NchantdXxxDialog** - Dialog windows (NchantdAboutDialog)
- **NchantdXxxManager** - Manager classes (NchantdFileManager)

### 2. File Organization

- One major class per file
- Related classes in same module (e.g., `text.py` contains PyfficeScript and PyfficeText)
- Imports grouped: stdlib → third-party → local

```python
# Standard library
import os
import sys
from typing import Optional, List

# Third-party (Qt)
from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtCore import Qt, pyqtSignal

# Local
from nchantrs import Nchantment
from .models import NchantdDocument
```

### 3. Qt Signal/Slot Patterns

- Use `pyqtSignal` for decoupled communication
- Prefix signal names with action: `document_created`, `item_selected`, `current_changed`
- Connect signals in dedicated `_connect_pane_signals()` methods

```python
class NchantdOfficeTabs(QTabWidget):
    """Tab widget with document management"""
    
    # Signals
    current_document_changed = pyqtSignal(object)
    tab_moved = pyqtSignal(int, int)
    tab_drag_started = pyqtSignal(object)
    tab_dropped = pyqtSignal(object, int)
    
    def _connect_pane_signals(self):
        """Connect signals for document lifecycle"""
        self.currentChanged.connect(self._on_current_changed)
```

### 4. Pyffice Document Integration

All document types must inherit from **PyfficeDocument** and implement `get_pyffice_tools()`:

```python
from pyffice.documents.document import PyfficeDocument

class NchantdOfficeText(PyfficeDocument):
    """Text document with NchantdOffice integration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.document_type = "text"
    
    def get_pyffice_tools(self):
        """Return toolbox tools for this document type"""
        return [
            {"id": "bold", "label": "Bold", "icon": "format-bold"},
            {"id": "italic", "label": "Italic", "icon": "format-italic"},
        ]
```

### 5. Signal Flow Architecture

Connect toolbar → tree → tabs → toolbox for document lifecycle:

```
toolbar.document_created 
    → tree.document_selected 
        → tabs.current_document_changed 
            → toolbox (calls get_pyffice_tools())
```

### 6. Drag and Drop

Implement in both tabs and trees for cross-pane operations:

```python
# In tabs.py
def _init_drag_drop(self):
    self.setAcceptDrops(True)
    self.setDragEnabled(True)
    self.setDragDropMode(QTabWidget.DragDrop)
    self.tabBar().setDragDropMode(QTabWidget.DragDrop)

# In trees.py  
def _init_drag_drop(self):
    self.setDragEnabled(True)
    self.setAcceptDrops(True)
    self.setDragDropOverwriteMode(True)
```

### 7. Logging

Use `logma` for structured logging:

```python
import logma
logger = logma.get_logger(__name__)

class NchantdOfficeApplication:
    def __init__(self):
        logger.info("Initializing NchantdOffice application")
```

### 8. Error Handling

- Use try/except for file operations
- Log errors with context
- Provide user feedback via dialogs

```python
try:
    document = self._load_document(path)
except FileNotFoundError:
    logger.error(f"Document not found: {path}")
    self._show_error_dialog(f"File not found: {path}")
```

---

## Document Types (Pyffice Integration)

### Implemented Document Classes

| Document Type | File | Features |
|---------------|------|----------|
| NchantdOfficeNotebook | notebooks.py | Jupyter-style notebooks |
| NchantdOfficeSpreadSheet | spreadsheet.py | Excel-style spreadsheets |
| NchantdOfficeMatrix | spreadsheet.py | Mathematical matrices |
| NchantdOfficeChart | charts.py | Data visualization |
| NchantdOfficeScript | text.py | Code/script editing |
| NchantdOfficeCalendar | calendars.py | Event scheduling |
| NchantdOfficePDF | pdf.py | PDF viewing |
| NchantdOfficePresentation | presentation.py | Slide presentations |
| NchantdOfficeContact | contacts.py | Contact management |
| NchantdOfficeVideo | video.py | Video playback |
| NchantdOfficeAudio | audio.py | Audio playback |
| NchantdOfficeImage | image.py | Image viewing |
| NchantdOfficeText | text.py | Rich text editing |

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `nchantdoffice-cli gui` | Launch GUI application |
| `nchantdoffice-cli new <path>` | Create new document |
| `nchantdoffice-cli open <path>` | Open existing document |
| `nchantdoffice-cli save <path>` | Save document |
| `nchantdoffice-cli export <path>` | Export to different format |
| `nchantdoffice-cli list` | List recent documents |
| `nchantdoffice-cli search <query>` | Search documents |
| `nchantdoffice-cli validate <path>` | Validate document |
| `nchantdoffice-cli repair <path>` | Repair corrupted document |

---

## Development Workflow

### 1. Create New Document Type

1. Create file in `nchantdoffice/widgets/documents/`
2. Inherit from `PyfficeDocument`
3. Implement `get_pyffice_tools()` method
4. Add to `__init__.py` exports

### 2. Add New Signal

1. Define signal in class `__init__`
2. Connect in `_connect_pane_signals()`
3. Document in AXN.md

### 3. Add UI Feature (Drag-drop, Context Menu)

1. Implement in appropriate widget file
2. Add to AXN.md under Phase 5
3. Test cross-pane integration

### 4. Build & Test

```bash
# Build package
cd nchantdoffice
pip install -e .

# Test CLI
nchantdoffice-cli gui
```

---

## Key Patterns

### Pane Signal Connection Pattern

```python
def _connect_pane_signals(self):
    """Connect all pane signals for document lifecycle"""
    # Toolbar creates documents
    self.toolbar.document_created.connect(self._on_document_created)
    
    # Tree selection opens in tabs
    self.tree.document_selected.connect(self._on_document_selected)
    
    # Tab changes update toolbox
    self.tabs.current_document_changed.connect(self._on_current_changed)

def _on_document_created(self, document):
    """Handle new document from toolbar"""
    self.tree.add_document(document)
    self.tabs.open_document(document)

def _on_document_selected(self, document):
    """Handle document selection from tree"""
    self.tabs.open_document(document)

def _on_current_changed(self, document):
    """Handle tab change - update toolbox"""
    if document:
        tools = document.get_pyffice_tools()
        self.toolbox.populate(tools)
```

### Dynamic Toolbox Pattern

```python
def _populate_tools_drawer(self, tools: List[dict]):
    """Dynamically populate toolbox based on document type"""
    # Clear existing
    self.tools_drawer.clear()
    
    # Add tools from document
    for tool in tools:
        button = QToolButton()
        button.setText(tool.get("label", ""))
        button.setIcon(QIcon(tool.get("icon", "")))
        button.clicked.connect(lambda checked, t=tool: self._on_tool_clicked(t))
        self.tools_drawer.addWidget(button)
```

---

## Testing

### Unit Tests
- Test in `test_nchantdoffice/`
- Use `pytest` framework
- Mock Qt components where possible

### Integration Tests
- Test signal connections between panes
- Test document lifecycle (create → tree → tabs → toolbox)
- Test drag-drop between panes

---

## Notes

- **No external 'crow' module** - Dynamic imports handled locally
- **Headless support** - GUI fails gracefully without display (expected on servers)
- **nchantrs integration** - Core data model handles storage, NchantdOffice provides UI

---

## References

- [AXN.md](./AXN.md) - Implementation tracking
- [pyffice_tasks.md](../pyffice_tasks.md) - Pyffice integration tasks
- [STATE.md](./STATE.md) - Current project state
