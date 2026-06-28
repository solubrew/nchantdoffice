# nchantdoffice TODO List

## ✅ Completed Items

| ID | Description | Status | Commit |
|----|-------------|--------|--------|
| 1 | Node selection after install - default to Home node | ✅ Complete | `1d28cd8f` |
| 2 | Restore last selected node on successive runs | ✅ Complete | `0c6c293` |
| 3 | **C3** — Widget database registration refactor | ✅ Complete | `39efdf7` |
| 4 | **presentation** document module - initial implementation | ✅ Complete | `5de9ec9` |
| 5 | Dependency cleanup - remove unused packages | ✅ Complete | `4f5b804`, `da48f23`, `fa5b437` |
| 6 | **CLI Commands** - All 9 high-priority CLI commands | ✅ Complete | `898d699` |

---

## 📊 Document Type Coverage

### Implemented ✅ (6 + 1)
| Type | Status | Notes |
|------|--------|-------|
| charts | ✅ | Functional |
| contacts | ✅ | Functional |
| databases | ✅ | Functional |
| diagrams | ✅ | Functional |
| email | ✅ | Functional |
| images | ✅ | Functional |
| presentation | ✅ | Initial impl done |
| **spreadsheet** | ✅ | `workbooks/matricies.py` - `NchantdOfficeMatrix` |

### Missing ❌ (27 types)
| Priority | Types |
|----------|-------|
| 🔴 P1 | text, ebook, audio, video, projects, analytics |
| 🟠 P2 | calendars, forms, container, web, cad |
| 🟡 P3 | data, config, filesystems, notebooks, reports, socials, updates |
| 🟢 P4 | script, skills, tags, workflows, media, ports |

---

## 🔴 Critical Bugs (C-Series)

| ID | File | Line | Description | Status |
|----|------|------|-------------|--------|
| C1 | widgets/trees.py | 89 | Node selection signal connection | ✅ Fixed | `6e3f8a1` |
| C2 | widgets/trees.py | 208 | ~~Sibling creation issue~~ (outdated line) | ✅ Removed | - |
| C4 | models.py | 975 | Tree routing issue | 🔴 TODO |
| C5 | models.py | 1327 | Document object not available | 🟠 TODO |
| C6 | atnrg/prompts.py | 161 | Nchantd Prompt override issue | 🟠 TODO |
| C7 | catalogs.py | 250 | Initial loading data duplicates | 🟠 TODO |
| C8 | references.py | - | Tag tracking issue | 🟠 TODO |

---

## 🟠 High Priority (H-Series)

| ID | File | Line | Description |
|----|------|------|-------------|
| H1 | dialogs/documents.py | 241 | Excel file integration (local file to open excel) |
| H2 | dialogs/documents.py | 245 | Google Drive integration dialog |
| H3 | dialogs/documents.py | 260 | Form builder wizard launch |
| H4 | dialogs/documents.py | 292 | CSV/XLSX/TAB file handling |
| H5 | models.py | 608 | PID definition/argument handling |
| H6 | models.py | 1146 | Virtual table relocation |
| H7 | models.py | 1271 | Session parsing implementation |
| H8 | models.py | 1297 | Notion/Evernote import |
| H9 | models.py | 1902 | Lazy loading - move to nchantrs base |
| H10 | toolboxes.py | 326, 378 | Loading new nchantd office instance |
| H11 | toolbars.py | 156, 160 | Widget lookup from document types table, MultiInstance db switch |
| H12 | toolbars.py | 190 | Combine add_tab/add_document signatures |
| H13 | widgets/new.py | 198 | Widget code override based on unique options selections |
| H14 | widgets/new.py | 410 | Default pane handlers for root node |
| H15 | browsers.py | 302 | Web scrapping functions connection |
| H16 | browsers.py | 671,681,691,701 | Address Input widget (street, city, state, zip) |
| H17 | filesystems.py | 105, 217 | Automation rules implementation |
| H18 | filesystems.py | 703 | Actual storage configuration |
| H19 | spreadsheets.py | 304 | Function dialog implementation |
| H20 | prompts.py | 422 | Configuration from user or NchantdService |

---

## 🟡 Medium Priority (M-Series)

| ID | File | Line | Description |
|----|------|------|-------------|
| M1 | models.py | 547 | App tables relocation question |
| M2 | models.py | 1007 | Date format conversion |
| M3 | models.py | 1186 | Tab code, images and tables arrangement |
| M4 | models.py | 1335 | External notifications approval check |
| M5 | models.py | 1397 | Version increment logic |
| M6 | models.py | 1610 | Version handling |
| M7 | utilities/utilities.py | 77 | Widget database lookup from database |
| M8 | utilities/links.py | 40 | Link table connection to link_affiliate |
| M9 | wizards/wizards.py | 62 | Journal document creation timing |
| M10 | toolbars.py | 238 | Multiple notes position increment |
| M11 | widgets/widgets.py | 123 | Unexpected state at this point |
| M12 | widgets/forms.py | 124 | Always asked rate spinbox in survey vs form |
| M13 | widgets/search.py | 123 | Tag tracking |
| M14 | widgets/documents.py | 121 | Tag tracking |
| M15 | browsers.py | 811 | Buttons in drawer handling |
| M16 | documents.py | 150, 159 | Flip icon |
| M17 | links.py | - | TODO: get link table where connection to the link_affiliate table |

---

## 🟢 Lower Priority (L-Series)

| ID | File | Line | Description |
|----|------|------|-------------|
| L1 | widgets/new.py | 189 | Cross-tool file format integration |
| L2 | widgets/new.py | 193 | Google Drive browser/API connection |

---

## 📋 Implementation Phases

### Phase 1: Bug Fixes (Critical)
1. **C1** - Fix node selection in trees.py:89
2. **C2** - Fix sibling creation in trees.py:208
3. **C4** - Fix tree routing in models.py:975

### Phase 2: Core Document Types
1. **text** - Rich text editor with bibliography support
2. **ebook** - EPUB/AZW/MOBI reader
3. **audio** - Audio playback
4. **video** - Video playback with FFmpeg
5. **projects** - PAXN project management
6. **analytics** - DataSet/DataView

### Phase 3: Productivity Features
1. **calendars** - Event management
2. **forms** - Form/survey builder
3. **container** - Archive handling
4. **web** - Browser integration

### Phase 4: Data & Advanced
1. **data** - CSV/JSON/XML/YAML handlers
2. **config** - TOML support, policies
3. **cad** - CAD file support
4. **reports** - Report generation

---

## 📊 Summary

| Category | Count |
|----------|-------|
| ✅ Completed | 6 |
| 🔴 Critical Bugs | 4 (1 done: C3) |
| 🟠 High Priority | 20 |
| 🟡 Medium Priority | 17 |
| 🟢 Low Priority | 2 |
| ❌ Missing Document Types | 27 |
| **Total Active Items** | **70** |

---

*Last Updated: 2026-06-28*
