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
| 7 | **C4** — Tree routing issue (models.py:975) | ✅ Complete | - |
| 8 | **C5** — Document object not available (models.py:1327) | ✅ Complete | - |
| 9 | **C6** — Nchantd Prompt override issue (atnrg/prompts.py:161) | ✅ Complete | - |
| 10 | **C7** — Initial loading data duplicates (catalogs.py:250) | ✅ Complete | - |
| 11 | **C8** — Tag tracking issue (references.py) | ✅ Complete | - |
| 12 | **H22** — Context Menu (right-click) | ✅ Fixed | `9843a94` |
| 13 | **H23** — Tab Duplication Issue | ✅ Not a Problem | User confirmed |
| 14 | **Web Browser** — Settings Panel, Privacy Controls, Download Manager | ✅ Complete | `d3c4a76` |
- implement caching for menus - completed

## New TODOs: (Need review and integration into overall development plan)
- reduce startup time
- Fix tab selection that causes surfacing of the catalog tab on first click. currently requires a second click to surface the correct tab
- Toolbox is not updating when switching between tabs it does update when switching between nodes
- 

---

## 📊 Document Type Coverage

### Implemented ✅ (18 types)
| Type | Status | Module |
|------|--------|--------|
| analytics | ✅ | `nchantdoffice/widgets/documents/analytics/` |
| calendars | ✅ | `nchantdoffice/widgets/documents/calendars/` |
| charts | ✅ | `nchantdoffice/widgets/documents/charts/` |
| contacts | ✅ | `nchantdoffice/widgets/documents/contacts/` |
| databases | ✅ | `nchantdoffice/widgets/documents/databases/` |
| diagrams | ✅ | `nchantdoffice/widgets/documents/diagrams/` |
| email | ✅ | `nchantdoffice/widgets/documents/email/` |
| filesystems | ✅ | `nchantdoffice/widgets/documents/filesystems/` |
| forms | ✅ | `nchantdoffice/widgets/documents/forms/` |
| images | ✅ | `nchantdoffice/widgets/documents/images/` |
| journals | ✅ | `nchantdoffice/widgets/documents/journals/` |
| notebooks | ✅ | `nchantdoffice/widgets/documents/notebooks/` |
| pdfs | ✅ | `nchantdoffice/widgets/documents/pdfs/` |
| presentations | ✅ | `nchantdoffice/widgets/documents/presentations/` |
| scripts | ✅ | `nchantdoffice/widgets/documents/scripts/` |
| spreadsheets | ✅ | `nchantdoffice/widgets/documents/spreadsheets/` |
| text | ✅ | `nchantdoffice/widgets/documents/text/` |
| web | ✅ | `nchantdoffice/widgets/documents/web/` |

### Missing ❌ (23 types)
| Priority | Types |
|----------|-------|
| 🔴 P1 | ebook, projects |
| 🟠 P2 | container, cad, reports, data (partial) |
| 🟡 P3 | config, updates |
| 🟢 L1 | audio |
| 🟢 L2 | video |
| 🟢 L3 | skills |
| 🟢 L4 | tags |
| 🟢 L5 | workflows |
| 🟢 L6 | media |
| 🟢 L7 | ports |

---

## 🔴 Critical Bugs (C-Series) - ALL FIXED ✅

| ID | File | Line | Description | Status |
|----|------|------|-------------|--------|
| C1 | widgets/trees.py | 89 | Node selection signal connection | ✅ Fixed | `6e3f8a1` |
| C2 | widgets/trees.py | 208 | ~~Sibling creation issue~~ (outdated line) | ✅ Removed | - |
| C3 | nchantd.py | - | Widget database registration refactor | ✅ Fixed | `39efdf7` |
| C4 | models.py | 975 | Tree routing issue (get_node) | ✅ Fixed | - |
| C5 | models.py | 1327 | Document object not available | ✅ Fixed | - |
| C6 | atnrg/prompts.py | 161 | Nchantd Prompt override issue | ✅ Fixed | - |
| C7 | catalogs.py | 250 | Initial loading data duplicates | ✅ Fixed | - |
| C8 | references.py | - | Tag tracking issue | ✅ Fixed | - |

**All critical bugs (C1-C8) have been resolved.**

---

## 🟠 High Priority (H-Series)

| ID | File | Line | Description | Status |
|----|------|------|-------------|--------|
| H1 | spreadsheet/nchantdspreadsheet.py | 240 | Excel file integration with formula preservation | ✅ Complete |
| H2 | dialogs/documents.py | 245 | Google Drive integration dialog | 🔴 TODO |
| H3 | dialogs/documents.py | 260 | Form builder wizard launch | 🔴 TODO |
| H4 | dialogs/documents.py | 292 | CSV/XLSX/TAB file handling | 🔴 TODO |
| H5 | models.py | 608 | PID definition/argument handling | 🔴 TODO |
| H6 | models.py | 1146 | Virtual table relocation | 🔴 TODO |
| H7 | models.py | 1271 | Session parsing implementation | 🔴 TODO |
| H8 | models.py | 1297 | Notion/Evernote import | 🔴 TODO |
| H9 | models.py | 1902 | Lazy loading - move to nchantrs base | 🔴 TODO |
| H10 | toolboxes.py | 326, 378 | Loading new nchantd office instance | 🔴 TODO |
| H11 | toolbars.py | 156, 160 | Widget lookup from document types table, MultiInstance db switch | 🔴 TODO |
| H12 | toolbars.py | 190 | Combine add_tab/add_document signatures | 🔴 TODO |
| H13 | widgets/new.py | 198 | Widget code override based on unique options selections | 🔴 TODO |
| H14 | widgets/new.py | 410 | Default pane handlers for root node | 🔴 TODO |
| H15 | browsers.py | 302 | Web scrapping functions connection | 🔴 TODO |
| H16 | browsers.py | 671,681,691,701 | Address Input widget (street, city, state, zip) | 🔴 TODO |
| H17 | filesystems.py | 105, 217 | Automation rules implementation | 🔴 TODO |
| H18 | filesystems.py | 703 | Actual storage configuration | 🔴 TODO |
| H19 | spreadsheets.py | 304 | Function dialog implementation | 🔴 TODO |
| H20 | prompts.py | 422 | Configuration from user or NchantdService | 🔴 TODO |
| H21 | mixins/documents.py | - | **Toolbar Missing** - Main Document Toolbar missing from PDF, Image document types | 🔴 TODO |
| H22 | mixins/widgets.py | - | **No Right Click Context Menu** | ✅ Fixed | `9843a94` |
| H23 | widgets/nodes.py | - | **Tab Duplication Issue** | ✅ Not a Problem | User confirmed |

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

## 🟢 Low Priority (L-Series)

| ID | Priority | File | Line | Description |
|----|----------|------|------|-------------|
| L1 | 🟢 L1 | widgets/new.py | 189 | Cross-tool file format integration |
| L2 | 🟢 L2 | widgets/new.py | 193 | Google Drive browser/API connection |
| L3 | 🟢 L3 | - | - | Audio playback support |
| L4 | 🟢 L4 | - | - | Video playback support |
| L5 | 🟢 L5 | - | - | Skills management module |
| L6 | 🟢 L6 | - | - | Tags system module |
| L7 | 🟢 L7 | - | - | Workflows automation |
| L8 | 🟢 L8 | - | - | Media management |
| L9 | 🟢 L9 | - | - | Port management |

---

## 📋 Implementation Phases

### Phase 1: Bug Fixes (Critical) - COMPLETED ✅
1. **C1-C8** - All critical bugs resolved ✅
2. **H22** - Context Menu fixed ✅
3. **H23** - Tab Duplication confirmed not a problem ✅

### Phase 2: Core Document Types (P1) - 2 remaining
1. **ebook** - EPUB/AZW/MOBI reader 🔴
2. **projects** - PAXN project management 🔴

### Phase 3: Productivity Features (P2)
1. **container** - Archive handling
2. **cad** - CAD file support
3. **reports** - Report generation
4. **data** - CSV/JSON/XML/YAML handlers (partial)

### Phase 4: Data & Advanced (P3)
1. **config** - TOML support, policies
2. **updates** - Update management

### Phase 5: Low Priority (L-Series)
1. **audio** - Audio playback
2. **video** - Video playback with FFmpeg
3. **skills** - Skills management
4. **tags** - Tags system
5. **workflows** - Workflows automation
6. **media** - Media management
7. **ports** - Port management

---

## 📊 Summary

| Category | Count |
|----------|-------|
| ✅ Completed | 14 |
| 🔴 Critical Bugs | 0 (C1-C8 all fixed) |
| 🟠 High Priority | 21 (18 pending, 3 done) |
| 🟡 Medium Priority | 17 |
| 🟢 Low Priority | 9 |
| ✅ Document Types | 18 implemented |
| ❌ Missing Document Types | 23 |
| **Total Active Items** | **68** |

---

## 🔧 Implementation Notes

### H21 - Toolbar Missing
**Problem**: Main Document Toolbar missing from PDF, Image document types

**Root Cause**: `init_toolbar()` method not being called or toolbar widgets not being built

**Fix Plan**:
1. Check if `NchantdOfficeDocumentMixin.init_toolbar()` is called for all document types
2. Ensure toolbar data exists in database (nchantd_menu/nchantd_menu_item tables)
3. Add toolbar to all document type classes that inherit from NchantdOfficeDocumentMixin

### Web Browser Features (COMPLETED ✅)
- **URL Inspection (Drawer 100)** - URL, domain, subdomain, params, whois ✅
- **Settings Panel (Drawer 200)** - Privacy controls, home page settings ✅
- **Download Manager (Drawer 300)** - Open Downloads folder in FileSystem tab ✅

---

*Last Updated: 2026-06-28*
*Critical bugs C1-C8 fully resolved*
*Web Browser feature set complete*
