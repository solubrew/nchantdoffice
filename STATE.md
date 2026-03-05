# STATE.md - NchantdOffice

## Current State: v0.3.0 Aligned with nchantrs

### Project
| Attribute | Value |
|-----------|-------|
| **Name** | NchantdOffice |
| **Type** | PyQt5/PySide6 GUI Application |
| **Branch** | gamma |
| **Location** | `/home/solubrew/.orin/workspace/projects/nchantdoffice` |
| **Repository** | `file:///mnt/overse/SBST01/vein/GitVein/nchantdoffice.git` |
| **Version** | 0.3.0 |
| **Last Updated** | 2026-03-04 |

### Purpose
NchantdOffice is a document-based productivity application that combines Pyffice document handling with nchantrs core framework. It provides tabs for various document types (TODOs, Notes, Calendar, Concerns, etc.) with advanced vector search capabilities.

---

## Internal Project Integrations

### Core Dependencies (Required)

| Project | Integration | Location | Purpose |
|---------|-------------|----------|---------|
| **nchantrs** | Inheritance | `nchantrs.models.models.NchantdStore` | Core storage layer |
| **nchantrs.widgets** | Composition | `nchantrs.widgets.*` | UI widget components |
| **pyffice** | Inheritance | `pyffice.document.PyfficeDocument` | Document base class |
| **micromole** | Via NchantdStore | `micromole.micromole.MicroMole` | Data collection (RSS feeds) |
| **squirl** | Via NchantdStore | `squirl.squirl.SQuiRL` | Database queries (SQL/NoSQL) |
| **condor** | Config | `condor.condor` | YAML configuration management |
| **ogma** | Logging | `ogma.logma.Logma` | Rich logging and debugging |
| **subtrix** | Utilities | `subtrix.utilities.uuid` | UUID generation |

### Optional Integrations

| Project | Integration | Location | Purpose |
|---------|-------------|----------|---------|
| **pycurity** | Via nchantrs | `nchantrs.pycurity` | Security/encryption |
| **apig** | NEW | `nchantdoffice/utilities/apig.py` | REST API client with retry/caching |
| **worldbridgeserver** | NEW | `nchantdoffice/utilities/worldbridge.py` | Web2 (HTTP) + Web3 (blockchain) data |
| **elv1r4** | Via worldbridge | `elv1r4.elv1r4` | Blockchain/Web3 interactions |
| **glain** | NchantdAgent | `nchantdoffice/nchantdagent/` | Context memory (optional agent layer) |
| **sentinel** | NchantdAgent | `nchantdoffice/nchantdagent/sentinel/` | Supervisory loop for spawning agents |

---

## Architecture

```
nchantdoffice (Pyffice + nchantrs GUI)
│
├── NchantdOfficeStore (NchantdStore + VectorSearchMixin)
│   ├── Inherits from: nchantrs.NchantdStore → MicroStash → SQuiRL
│   ├── Vector Search: create_embedding, similarity_search, semantic_search
│   └── WorldBridge: Optional web2/web3 data
│
├── NchantdOfficeCloakModel
│   └── Extends: nchantrs.NchantdCloakModel
│
├── utilities/
│   ├── apig.py              ← NEW: API client with retry/caching
│   ├── worldbridge.py       ← NEW: Web2/Web3 data integration
│   ├── vector_search.py     ← NEW: Vector search mixin
│   ├── cache.py             ← Caching utilities
│   ├── config.py            ← Configuration
│   ├── links.py             ← Link management
│   └── ...
│
├── [OPTIONAL] NchantdAgent Package
│   ├── GlainMixin (context memory)
│   ├── sentinel (monitoring/health)
│   └── agent components
│
└── nchantrs (core framework)
    ├── pycurity (security)
    ├── micromole + squirl (data storage)
    └── condor (configuration)
```

---

## Implemented Features

### Pyffice Document Integration (v0.3.1)
- [x] NchantdOfficeDocument inherits from PyfficeDocument
- [x] PYTYPE class variable maps to Pyffice classes
- [x] _init_pyffice_type() initializes Pyffice document
- [x] NchantdOfficeScript implements PyfficeScript
- [x] NchantdOfficeMatrix implements PyfficeMatrix
- [ ] NchantdOfficeSpreadsheet implements PyfficeSpreadSheet
- [ ] NchantdOfficeChart implements PyfficeChart
- [ ] NchantdOfficePresentation implements PyfficePresentation
- [ ] NchantdOfficeNotebook implements PyfficeNotebook
- [ ] NchantdOfficePDF implements PyfficePDF
- [ ] Additional document types...

### Core Features
- [x] Document-based productivity application
- [x] Tab-based interface (TODOs, Notes, Calendar, Concerns)
- [x] NchantdStore integration (SQL/NoSQL via SQuiRL)
- [x] YAML configuration via condor
- [x] Rich logging via ogma
- [x] Widget composition from nchantrs.widgets

### Vector Search (v0.3.0)
- [x] Embedding generation (sentence-transformers)
- [x] Similarity search (cosine similarity)
- [x] Semantic search (natural language queries)
- [x] Hybrid search (keyword + vector)
- [x] FAISS indexing with numpy fallback
- [x] Document embedding storage

### API & External Data (v0.3.0)
- [x] apig.py - Robust HTTP client with retry/caching
- [x] worldbridge.py - Web2/Web3 data integration
- [x] elv1r4 integration ready (web3/blockchain)
- [x] API key management

### Optional Features
- [ ] NchantdAgent package (GlainMixin + sentinel)
- [ ] API authentication via pycurity

---

## Dependencies

| Package | Version | Status |
|---------|---------|--------|
| nchantrs | ≥0.3.0 | ✅ Required |
| pyffice | latest | ✅ Required |
| condor | latest | ✅ Required |
| ogma | latest | ✅ Required |
| subtrix | latest | ✅ Required |
| micromole | latest | ✅ Required |
| squirl | latest | ✅ Required |
| pycurity | latest | ✅ Optional |
| apig | latest | ✅ Optional |
| worldbridgeserver | latest | ✅ Optional |
| elv1r4 | latest | ✅ Optional |
| sentence-transformers | latest | ✅ Optional (vector search) |
| faiss-cpu | latest | ✅ Optional (vector search) |

---

## Testing

| Category | Status |
|----------|--------|
| Core tests | ⏳ Pending |
| Vector search tests | ⏳ Pending |
| API client tests | ⏳ Pending |
| WorldBridge tests | ⏳ Pending |
| Widget tests | ⏳ Pending |
| Integration tests | ⏳ Pending |

---

## Files

| File | Description |
|------|-------------|
| `nchantdoffice/models.py` | NchantdOfficeStore, CloakModel, TabSetModel |
| `nchantdoffice/nchantdoffice.py` | Main application class |
| `nchantdoffice/views.py` | View classes |
| `nchantdoffice/utilities/vector_search.py` | Vector search mixin |
| `nchantdoffice/utilities/apig.py` | API client (NEW) |
| `nchantdoffice/utilities/worldbridge.py` | Web2/Web3 data (NEW) |
| `nchantdoffice/widgets/` | Custom widgets |
| `nchantdoffice/dialogs/` | Dialog classes |

---

## UI Features Status

### Tab Drag-and-Drop
| Feature | Implementation | Status |
|---------|---------------|--------|
| Center app tab dragging | nchantrs `NchantdTabSet.start_drag()` | ✅ EXISTS |
| Tab reordering within tabset | `move_tab()` method | ✅ EXISTS |
| Tab dragging between panes | MIME data with source_widget | ✅ EXISTS |
| Drag visual feedback | `create_drag_pixmap()` | ✅ EXISTS |

### Tree Drag-and-Drop
| Feature | Implementation | Status |
|---------|---------------|--------|
| Tree node drag-and-drop | QAbstractItemView.DragDrop mode | ✅ EXISTS |
| Tab-to-tree drag handler | `NchantdOfficeApplicationTree._handle_tab_drop()` | ✅ EXISTS |
| Node creation from dropped tab | `_create_node_from_tab()` | ✅ EXISTS |

### Right Pane / Toolbox
| Feature | Implementation | Status |
|---------|---------------|--------|
| Right pane tabset | `panes["right"]` | ✅ EXISTS |
| Toolbox loading | `load_toolbox()` in tabset | ✅ EXISTS |
| Tab-specific toolbox | Per-tab `toolbox_config` | ✅ EXISTS |
| Search in documents | Document search widgets | ✅ EXISTS |

### Still Needed
| Priority | Feature | Status |
|----------|---------|--------|
| P0 | Right-click context menus | ✅ DONE (context_manager.py + mixins) |
| P1 | Enhanced right toolbox search | 🟡 PARTIAL |
| P1 | Additional toolbox drawer items | 🟡 PARTIAL |

---

## Utility Modules

| Module | Purpose |
|--------|---------|
| `utilities/apig.py` | HTTP client with retry, caching, rate limiting |
| `utilities/worldbridge.py` | Web2 (HTTP) + Web3 (blockchain) data access |
| `utilities/vector_search.py` | Vector embeddings and semantic search |
| `utilities/cache.py` | Memoization and caching |
| `utilities/config.py` | YAML configuration |
| `utilities/links.py` | Link/affiliate management |
| `utilities/lazy.py` | Lazy loading for widgets |
| `utilities/parallel.py` | Parallel loading and performance monitoring |

---

*Last updated: 2026-03-04*
*Aligned with nchantrs v0.3.0*
