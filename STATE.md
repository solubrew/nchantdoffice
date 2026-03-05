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

### Core Dependencies

| Project | Integration | Location | Purpose |
|---------|-------------|----------|---------|
| **nchantrs** | Inheritance | `nchantrs.models.models.NchantdStore` | Core storage layer |
| **nchantrs.widgets** | Composition | `nchantrs.widgets.*` | UI widget components |
| **micromole** | Via NchantdStore | `micromole.micromole.MicroMole` | Data collection (RSS feeds) |
| **squirl** | Via NchantdStore | `squirl.squirl.SQuiRL` | Database queries (SQL/NoSQL) |
| **condor** | Config | `condor.condor` | YAML configuration management |
| **pycurity** | Via nchantrs | `nchantrs.pycurity` | Security/encryption (optional) |
| **apig** | Via nchantrs/worldbridge | `nchantrs.apig` | REST API client (optional) |
| **pyffice** | Composition | `pyffice.pyffice.PyfficeCodex` | Document handling (Excel, PDF, etc.) |

### NchantdOffice Layer Additions

| Project | Purpose | Status |
|---------|---------|--------|
| **worldbridgeserver** | Web2 (HTTP) + Web3 (blockchain) data | ✅ Integrated |
| **Vector Search** | Semantic search with embeddings | ✅ Added |
| **GlainMixin** | Agent memory (optional NchantdAgent) | ✅ Available |

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
├── [OPTIONAL] NchantdAgent Package
│   ├── GlainMixin (context memory)
│   ├── sentinel (monitoring/health)
│   └── agent components
│
└── nchantrs (core framework)
    ├── pycurity (security)
    ├── apig (API layer)
    ├── micromole + squirl (data storage)
    └── condor (configuration)
```

---

## Implemented Features

### Core Features
- [x] Document-based productivity application
- [x] Tab-based interface (TODOs, Notes, Calendar, Concerns)
- [x] NchantdStore integration (SQL/NoSQL via SQuiRL)
- [x] YAML configuration via condor
- [x] Widget composition from nchantrs.widgets

### Vector Search (v0.3.0)
- [x] Embedding generation (sentence-transformers)
- [x] Similarity search (cosine similarity)
- [x] Semantic search (natural language queries)
- [x] Hybrid search (keyword + vector)
- [x] FAISS indexing with numpy fallback
- [x] Document embedding storage

### Optional Features
- [ ] NchantdAgent package (GlainMixin + sentinel)
- [ ] WorldBridge integration for web2/web3 data
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
| pycurity | latest | ✅ Optional |
| sentence-transformers | latest | ✅ Optional (vector search) |
| faiss-cpu | latest | ✅ Optional (vector search) |

---

## Testing

| Category | Status |
|----------|--------|
| Core tests | ⏳ Pending |
| Vector search tests | ⏳ Pending |
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
| `nchantdoffice/widgets/` | Custom widgets |
| `nchantdoffice/dialogs/` | Dialog classes |

---

*Last updated: 2026-03-04*
*Aligned with nchantrs v0.3.0*
