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
|----|------|------|-------------|
| H1 | dialogs/documents.py | 241 | Excel file integration (local file to open excel) | 🔴 TODO |
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
| H22 | mixins/widgets.py | - | **No Right Click Context Menu** - contextMenuEvent not properly connected | ✅ Fixed | `9843a94` |
| H23 | widgets/nodes.py | - | **Tab Duplication Issue** - When creating new tabs, old views are duplicated instead of replaced | 🔴 TODO |

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

### Phase 1: Bug Fixes (Critical) - COMPLETED ✅
1. **C1** - Fix node selection in trees.py:89 ✅
2. **C2** - Fix sibling creation in trees.py:208 ✅
3. **C3-C8** - All remaining critical bugs ✅

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
| ✅ Completed | 11 |
| 🔴 Critical Bugs | 0 (8 total: C1-C8 all fixed) |
| 🟠 High Priority | 23 |
| 🟡 Medium Priority | 17 |
| 🟢 Low Priority | 2 |
| ❌ Missing Document Types | 27 |
| **Total Active Items** | **69** |

---

## 🔧 Implementation Notes (from TODO_IMPLEMENTATION_PLAN.md)

### H21 - Toolbar Missing
**Problem**: Main Document Toolbar completely missing from PDF, Image, and other document types

**Root Cause**: `init_toolbar()` method not being called or toolbar widgets not being built

**Fix Plan**:
1. Check if `NchantdOfficeDocumentMixin.init_toolbar()` is being called for all document types
2. Ensure toolbar data exists in database (nchantd_menu/nchantd_menu_item tables)
3. Add toolbar to all document type classes that inherit from NchantdOfficeDocumentMixin

### H22 - No Right Click Context Menu
**Problem**: No right-click functionality at all

**Root Cause**: 
- Warning: "No app model available for context menu" - widget doesn't have proper app reference
- `contextMenuEvent` not properly connected

**Fix Plan**:
1. Ensure all document widgets have proper `app` reference set
2. Fix `NchantdWidgetMixin.contextMenuEvent` to load menus from database
3. Verify `NchantdMenu` build system is working
4. Test that right-click triggers menu display

### H23 - Tab Duplication Issue
**Problem**: When creating new tabs, old views are duplicated instead of replaced

**Investigation**:
1. Check `updateTabs()` in nodes.py - verify it clears before building
2. Check `buildTabSet()` - ensure it's replacing not appending
3. Verify model/instance references are unique per tab

---

*Last Updated: 2026-06-28*
*Critical bugs C1-C8 fully resolved*
