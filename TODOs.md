# nchantdoffice TODO List

## ✅ Completed Items

| ID | Description | Status | Commit |
|----|-------------|--------|--------|
| 1 | Node selection after install - default to Home node | ✅ Complete | `1d28cd8f` |
| 2 | Restore last selected node on successive runs, fallback to Home | ✅ Complete | `0c6c293` |
| 3 | Fix main document toolbar for all document types | ⚠️ Unverified | commit `710cf01` not in current repo (possibly in wiped history) |
| 4 | Implement context menu using NchantdMenu build system | ⚠️ Unverified | commit `710cf01` not in current repo (possibly in wiped history) |
| 5 | Add drag and drop system for tree nodes | ⚠️ Unverified | commit `8f484ec` not in current repo (possibly in wiped history) |
| 6 | **C3** — Fix `register_document()` widget registration refactor | ✅ Complete | `39efdf7` |
| 7 | **presentation** document module — initial implementation | ✅ Complete | `5de9ec9` |
| 8 | Update `fix document paths` (document path resolution) | ✅ Complete | `86e244f` |
| 9 | Dependency cleanup — remove unused packages (cairosvg, solidpython, etc.) | ✅ Complete | `4f5b804`, `da48f23`, `fa5b437` |
| 10 | **CLI Commands** — Implement all 9 high-priority CLI commands (new, open, export, save, list, info, search, validate, repair) | ✅ Complete | `898d699` |
| 10 | **CLI Commands** — Implement all 9 high-priority CLI commands (new, open, export, save, list, info, search, validate, repair) | ✅ Complete | `898d699` |
| 10 | **CLI Commands** — Implement all 9 high-priority CLI commands (new, open, export, save, list, info, search, validate, repair) | ✅ Complete | `898d699` |

---

## 📌 Code-Level TODOs Located (cross-checked against TODO markers in source)

Found via `grep -rn "TODO\|FIXME\|XXX" --include="*.py"` — 30 markers across 4 files. All are accounted for in the priority tables below (C1–C8, H, M, L buckets). No orphan TODOs.

Files with markers:
- `widgets/trees.py` — 5 markers (lines 89, 208, 296, 321, 343)
- `nchantdoffice.py` — 19 markers (lines 75, 246, 261, 292, 546, 607, 839, 974, 1006, 1145, 1317, 1325, 1387, 1600, 1892 + duplicates)
- `widgets/controls/nchantdprompt.py` — 1 marker (line 162)
- `widgets/references.py` — 3 markers (lines 148, 158 × 3)

---


---

## 📊 Pyffice Gap Analysis - Document Type Coverage

### Overview
- **pyffice**: 33 document types, 15 missing in nchantdoffice
- **nchantdoffice**: Only 6 document types implemented, **27 types missing**

### nchantdoffice Document Types (✅ Implemented)

| Document Type | File | Status | pyffice Source |
|--------------|------|--------|----------------|
| charts | `charts/` | ✅ Functional | `pyffice/documents/charts/` |
| contacts | `contacts/` | ✅ Functional | `pyffice/documents/contacts/` |
| databases | `databases/` | ✅ Functional | `pyffice/documents/databases/` |
| diagrams | `diagrams/` | ✅ Functional | `pyffice/documents/diagrams/` |
| email | `email/` | ✅ Functional | `pyffice/documents/email/` |
| images | `images/` | ✅ Functional | `pyffice/documents/images/` |

---

### Missing Document Types (❌ Not Implemented)

#### 🔴 Critical Priority (High-Value, Complex)

| Document Type | pyffice Source | Priority | Notes |
|--------------|----------------|----------|-------|
| **presentation** | `pyffice/documents/presentation/` | 🔴 P1 | PPTX, ODP support - core office feature |
| **spreadsheet** | `pyffice/documents/matrix/` | 🔴 P1 | Matrix operations + spreadsheet - core feature |
| **projects** | `pyffice/documents/projects/` | 🔴 P1 | PAXN project management - major feature |
| **text** | `pyffice/documents/text/` | 🔴 P1 | Bibliographies + text messages - core feature |
| **ebook** | `pyffice/documents/ebook/` | 🔴 P1 | EPUB, AZW, MOBI support |
| **audio** | `pyffice/documents/audio/` | 🔴 P1 | Audio playback and management |
| **video** | `pyffice/documents/video/` | 🔴 P1 | Video playback with FFmpeg |

#### 🟠 High Priority (Common Office Use)

| Document Type | pyffice Source | Priority | Notes |
|--------------|----------------|----------|-------|
| **analytics** | `pyffice/documents/analytics/` | 🟠 P2 | DataSet, DataView analytics |
| **cad** | `pyffice/documents/cad/` | 🟠 P2 | 15 files: DXF, DWG, STL, STEP, OBJ, FBX |
| **calendars** | `pyffice/documents/calendars/` | 🟠 P2 | Event management system |
| **forms** | `pyffice/documents/forms/` | 🟠 P2 | Form and survey builder |
| **container** | `pyffice/documents/container/` | 🟠 P2 | Zip, Tar, RAR, 7zip archives |
| **web** | `pyffice/documents/web/` | 🟠 P2 | Browser, scraping, URL utilities |

#### 🟡 Medium Priority (Specialized)

| Document Type | pyffice Source | Priority | Notes |
|--------------|----------------|----------|-------|
| **data** | `pyffice/documents/data/` | 🟡 P3 | CSV, JSON, XML, YAML handlers |
| **config** | `pyffice/documents/config/` | 🟡 P3 | TOML support, policies |
| **filesystems** | `pyffice/documents/filesystems/` | 🟡 P3 | Virtual FS abstraction |
| **notebooks** | `pyffice/documents/notebooks/` | 🟡 P3 | Jupyter notebook support |
| **reports** | `pyffice/documents/reports/` | 🟡 P3 | Report generation |
| **socials** | `pyffice/documents/socials/` | 🟡 P3 | Messages + social integration |
| **updates** | `pyffice/documents/updates/` | 🟡 P3 | PyfficeUpdate system |

#### 🟢 Lower Priority (Niche/Advanced)

| Document Type | pyffice Source | Priority | Notes |
|--------------|----------------|----------|-------|
| **script** | `pyffice/documents/script/` | 🟢 P4 | Script document execution |
| **skills** | `pyffice/documents/skills/` | 🟢 P4 | Skill framework |
| **tags** | `pyffice/documents/tags/` | 🟢 P4 | Tagging, ratings, references |
| **workflows** | `pyffice/documents/workflows/` | 🟢 P4 | Alarms + formula automation |
| **media** | `pyffice/documents/media/` | 🟢 P4 | Media consolidation (audio, video, HEIC, raw) |
| **ports** | `pyffice/documents/ports/` | 🟢 P4 | Port architecture |

---

## 📋 Implementation Plan

### Phase 1: Core Office Features (Week 1-2)
1. **presentation** - PPTX/ODP viewer/editor
2. **spreadsheet** - Matrix/spreadsheet support  
3. **text** - Rich text editor
4. **ebook** - EPUB/AZW/MOBI reader

### Phase 2: Media & Communication (Week 3-4)
5. **audio** - Audio playback
6. **video** - Video playback
7. **email** - Already present, enhance IMAP/SMTP

### Phase 3: Data & Analysis (Week 5-6)
8. **analytics** - DataSet/DataView
9. **data** - CSV/JSON/XML/YAML handlers
10. **charts** - Already present, enhance
11. **forms** - Form builder

### Phase 4: Specialized Features (Week 7-8)
12. **cad** - CAD file support
13. **calendars** - Event management
14. **web** - Browser integration
15. **container** - Archive handling

### Phase 5: Advanced Features (Week 9+)
16. **projects** - PAXN project management
17. **reports** - Report generation
18. **workflows** - Automation
19. Remaining types...

---

## 🔴 Critical Priority (Bugs/Issues)

| ID | Priority | Location | Description |
|----|----------|----------|-------------|
| C1 | 🔴 P1 | `nchantdoffice/widgets/trees.py:88` | TODO #2 selection issue - node selection not working correctly in certain situations |
| C2 | 🔴 P1 | `nchantdoffice/widgets/trees.py:207` | Sibling creation issue in certain situations - cannot create siblings properly |
| C3 | 🔴 P1 | `nchantdoffice/nchantdoffice.py:839` | Widget database registration refactor needed |
| C4 | 🔴 P1 | `nchantdoffice/nchantdoffice.py:973` | Tree routing issue |
| C5 | 🔴 P2 | `nchantdoffice/nchantdoffice.py:1316` | Document object not available |
| C6 | 🔴 P2 | `nchantrs/widgets/controls/nchantdprompt.py:161` | Nchantd Prompt override issue |
| C7 | 🔴 P2 | `nchantrs/nodes.py:250` | Initial loading data duplicates - data loaded multiple times |
| C8 | 🔴 P2 | `nchantrs/nodes.py:123` | Tag tracking issue across multiple nchantd*.py files |

---

## 🟠 High Priority (Core Features)

| ID | Location | Description |
|----|----------|-------------|
| H1 | `nchantdoffice/nchantdoffice.py` | Implement document creation |
| H2 | `nchantdoffice/nchantdoffice.py` | Implement document opening |
| H3 | `nchantdoffice/nchantdoffice.py` | Implement export functionality |
| H4 | `nchantdoffice/nchantdoffice.py` | Implement save functionality |
| H5 | `nchantdoffice/nchantdoffice.py` | Implement list functionality |
| H6 | `nchantdoffice/nchantdoffice.py` | Implement info display |
| H7 | `nchantdoffice/nchantdoffice.py` | Implement search functionality |
| H8 | `nchantdoffice/nchantdoffice.py` | Implement validation |
| H9 | `nchantdoffice/nchantdoffice.py` | Implement repair functionality |
| H10 | `nchantdoffice/nchantdoffice.py:1144` | Virtual table relocation |
| H11 | `nchantdoffice/nchantdoffice.py:1891` | Lazy loading - move to nchantrs base |
| H12 | `nchantrs/nodes.py:410` | Default pane handlers for root node |

---

## 🟡 Medium Priority (Enhancements)

| ID | Location | Description |
|----|----------|-------------|
| M1 | `nchantdoffice/nchantdoffice.py:245` | Google Drive integration dialog |
| M2 | `nchantdoffice/nchantdoffice.py:260` | Form builder wizard - currently commented out |
| M3 | `nchantdoffice/nchantdoffice.py:545` | App tables relocation |
| M4 | `nchantdoffice/nchantdoffice.py:606` | PID definition/argument handling |
| M5 | `nchantdoffice/nchantdoffice.py:1005` | Date format conversion |
| M6 | `nchantdoffice/nchantdoffice.py:1324` | External notifications approval |
| M7 | `nchantdoffice/nchantdoffice.py:1386` | Version increment logic |
| M8 | `nchantdoffice/nchantdoffice.py:1599` | Version handling |
| M9 | `nchantdoffice/nchantdwidget.py:77` | Widget database lookup |
| M10 | `nchantdoffice/nchantdimage.py:677,687,697,707` | Address input widget |
| M11 | `nchantdoffice/nchantdchat.py:105,217` | Automation rules |
| M12 | `nchantdoffice/widgets/trees.py` | Tab duplication issue in nodes.py |

---

## 🟢 Low Priority (Nice to Have)

| ID | Location | Description |
|----|----------|-------------|
| L1 | `nchantdoffice/nchantdoffice.py:292` | CSV/XLSX/TAB file handling |
| L2 | `nchantdoffice/nchantdoffice.py` | Additional file format support |
| L3 | | Performance optimization opportunities |
| L4 | | UI/UX polish and improvements |

---

## 📊 Summary by Category

| Category | Count |
|----------|-------|
| ✅ Completed | 9 |
| ✅ Implemented (Document Types) | 6 (+ 1 in progress: presentation) |
| ❌ Missing (Document Types) | 27 |
| 🔴 Critical Bugs | 8 (1 done: C3) |
| 🟠 High Priority Features | 12 |
| 🟡 Medium Priority | 12 |
| 🟢 Low Priority | 4 |
| **Total Catalogued** | **78** |

---

## 🎯 Recommended Next Actions

### Immediate (This Week)
1. **Fix C1** - Node selection issue in trees.py:88
2. **Fix C2** - Sibling creation issue in trees.py:207
3. ~~**Start presentation** - Use pyffice/documents/presentation/ as base~~ ✅ **DONE** (`5de9ec9`) — landed as initial implementation; follow-up work may remain

### Soon (Next 2 Weeks)
4. Implement **presentation** document type
5. Implement **spreadsheet** document type  
6. Implement **text** document type

### Later (This Month)
7. Audio/video playback integration
8. Enhanced email support
9. Form builder wizard

---

## 📁 pyffice Source Files for Missing Types

```
pyffice/documents/
├── analytics/       → source: pyffice/documents/analytics/sources.py
├── audio/          → source: pyffice/documents/audio/audio.py
├── cad/            → source: pyffice/documents/cad/ (15 files)
├── calendars/      → source: pyffice/documents/calendars/
├── container/      → source: pyffice/documents/container/
├── data/           → source: pyffice/documents/data/
├── ebook/          → source: pyffice/documents/ebook/
├── forms/          → source: pyffice/documents/forms/forms.py
├── filesystems/    → source: pyffice/documents/filesystems/filesystems.py
├── media/          → source: pyffice/documents/media/
├── notebooks/      → source: pyffice/documents/notebooks/notebooks.py
├── ports/          → source: pyffice/documents/ports/
├── presentation/   → source: pyffice/documents/presentation/
├── projects/       → source: pyffice/documents/projects/
├── reports/        → source: pyffice/documents/reports/reports.py
├── script/         → source: pyffice/documents/script/script.py
├── skills/         → source: pyffice/documents/skills/skills.py
├── socials/        → source: pyffice/documents/socials/
├── tags/           → source: pyffice/documents/tags/
├── text/           → source: pyffice/documents/text/
├── updates/        → source: pyffice/documents/updates/updates.py
├── video/          → source: pyffice/documents/video/video.py
└── web/            → source: pyffice/documents/web/
```

---

*Last Updated: 2026-06-26*
