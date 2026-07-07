# nchantdoffice TODO List

*Last Updated: 2026-07-07*

## ✅ Completed Items

| ID  | Description                                                         | Commit       |
|-----|---------------------------------------------------------------------|--------------|
| 1   | Node selection after install - default to Home node                 | `1d28cd8f`   |
| 2   | Restore last selected node on successive runs                      | `0c6c293`    |
| 3   | C3 — Widget database registration refactor                          | `39efdf7`    |
| 4   | presentation document module - initial implementation                | `5de9ec9`    |
| 5   | Dependency cleanup - remove unused packages                         | `4f5b804`    |
| 6   | CLI Commands - All 9 high-priority CLI commands                    | `898d699`    |
| 7   | C4 — Tree routing issue (models.py:975)                             | —            |
| 8   | C5 — Document object not available (models.py:1327)                | —            |
| 9   | C6 — Nchantd Prompt override issue (atnrg/prompts.py:161)          | —            |
| 10  | C7 — Initial loading data duplicates (catalogs.py:250)               | —            |
| 11  | C8 — Tag tracking issue (references.py)                            | —            |
| 12  | H22 — Context Menu (right-click)                                   | `9843a94`    |
| 13  | H23 — Tab Duplication Issue                                         | —            |
| 14  | Web Browser — Settings Panel, Privacy Controls, Download Manager   | `d3c4a76`    |
| 15  | H10 — Sigil instance caching in NchantdOfficeApplicationToolBox      | `9ae4f1a`    |
| 16  | Implement caching for menus                                         | —            |

## 🚀 Performance (P-Series)

| ID  | File                                  | Line | Description                                         | Status |
|-----|---------------------------------------|------|-----------------------------------------------------|--------|
| P1  | —                                     | —    | Reduce startup time                                 | 🔴 TODO |
| P2  | menus.py                              | —    | Stop rebuilding context menu on every interaction   | 🔴 TODO |
| P3  | models.py                             | —    | Lazy loading / deferred query execution             | 🔴 TODO |
| P4  | widgets/widgets.py                    | —    | Toolbox widget rebuild on tab switch                | 🔴 TODO |
| P5  | —                                     | —    | Database index analysis and optimization             | 🟡 TODO |
| P6  | —                                     | —    | Virtual table query plan analysis                    | 🟡 TODO |
| P7  | —                                     | —    | Widget factory instantiation profiling               | 🟡 TODO |

## 📊 Document Type Coverage

### Implemented ✅ (18 types)

analytics, calendars, charts, contacts, databases, diagrams, email, filesystems, forms, images, journals, notebooks, pdfs, presentations, scripts, spreadsheets, text, web

### Missing ❌ (23 types)

| Priority | Types                                         |
|----------|-----------------------------------------------|
| 🔴 P1    | ebook, projects                               |
| 🟠 P2    | container, cad, reports, data (partial)       |
| 🟡 P3    | config, updates                               |
| 🟢 L1–L7 | audio, video, skills, tags, workflows, media, ports |

## 🔴 Critical Bugs (C-Series) — ALL FIXED ✅

| ID  | File           | Line | Description                     | Commit      |
|-----|----------------|------|---------------------------------|-------------|
| C1  | widgets/trees.py  | 89   | Node selection signal connection | `6e3f8a1`   |
| C2  | widgets/trees.py  | 208  | Sibling creation issue (outdated) | Removed     |
| C3  | nchantd.py        | —    | Widget database registration      | `39efdf7`   |
| C4  | models.py         | 975  | Tree routing issue (get_node)    | —           |
| C5  | models.py         | 1327 | Document object not available    | —           |
| C6  | atnrg/prompts.py  | 161  | Nchantd Prompt override issue     | —           |
| C7  | catalogs.py       | 250  | Initial loading data duplicates   | —           |
| C8  | references.py     | —    | Tag tracking issue               | —           |

## 🟠 High Priority (H-Series)

| ID  | File                              | Line | Description                                           | Status |
|-----|-----------------------------------|------|-------------------------------------------------------|--------|
| H1  | spreadsheets/nchantdspreadsheet.py | 240  | Excel file integration with formula preservation       | ✅ Complete |
| H2  | dialogs/documents.py              | 245  | Google Drive integration dialog                       | 🔴 TODO |
| H3  | dialogs/documents.py              | 260  | Form builder wizard launch                           | 🔴 TODO |
| H4  | dialogs/documents.py              | 292  | CSV/XLSX/TAB file handling                           | 🔴 TODO |
| H5  | models.py                         | 608  | PID definition/argument handling                      | 🔴 TODO |
| H6  | models.py                         | 1178 | Virtual table relocation                              | 🔴 TODO |
| H7  | models.py                         | 1303 | Session parsing implementation                         | 🔴 TODO |
| H8  | models.py                         | 1329 | Notion/Evernote import                               | 🔴 TODO |
| H9  | models.py                         | 1902 | Lazy loading - move to nchantrs base                  | 🔴 TODO |
| H10 | toolboxes.py                      | 326  | Loading new nchantd office instance                  | ✅ Complete |
| H11 | toolbars.py                      | 156  | Widget lookup from document types table              | 🔴 TODO |
| H12 | toolbars.py                      | 190  | Combine add_tab/add_document signatures              | 🔴 TODO |
| H13 | widgets/new.py                   | 198  | Widget code override based on unique options         | 🔴 TODO |
| H14 | widgets/new.py                   | 410  | Default pane handlers for root node                   | 🔴 TODO |
| H15 | browsers.py                      | 302  | Web scrapping functions connection                   | 🔴 TODO |
| H16 | browsers.py                      | 644  | Address Input widget (street, city, state, zip)      | 🔴 TODO |
| H17 | filesystems.py                   | 105  | Automation rules implementation                      | 🔴 TODO |
| H18 | filesystems.py                   | 703  | Actual storage configuration                         | 🔴 TODO |
| H19 | spreadsheets.py                  | 1479 | Function dialog implementation                        | 🔴 TODO |
| H20 | prompts.py                        | 422  | Configuration from user or NchantdService             | 🔴 TODO |
| H21 | mixins/documents.py              | —    | Toolbar Missing - PDF, Image doc types               | 🔴 TODO |
| H22 | mixins/widgets.py                | —    | No Right Click Context Menu                          | ✅ Fixed `9843a94` |
| H23 | widgets/nodes.py                 | —    | Tab Duplication Issue                                | ✅ Not a Problem |
| H24 | widgets/widgets.py               | 123  | Toolbox drawer/widget not updating on tab switch      | 🔴 TODO |
| H25 | widgets/widgets.py               | 123  | Tab selection surfaces catalog tab on first click    | 🔴 TODO |

## 🟡 Medium Priority (M-Series)

| ID  | File                   | Line | Description                                          |
|-----|------------------------|------|------------------------------------------------------|
| M1  | models.py              | 546  | App tables relocation question                        |
| M2  | models.py              | 1007 | Date format conversion                                |
| M3  | models.py              | 1218 | Tab code, images and tables arrangement               |
| M4  | models.py              | 1359 | External notifications approval check                  |
| M5  | models.py              | 1429 | Version increment logic                               |
| M6  | models.py              | 1642 | Version handling                                      |
| M7  | utilities/utilities.py | 77   | Widget database lookup from database                  |
| M8  | utilities/links.py     | 40   | Link table connection to link_affiliate              |
| M9  | wizards/wizards.py    | 62   | Journal document creation timing                      |
| M10 | toolbars.py            | 238  | Multiple notes position increment                     |
| M11 | widgets/widgets.py     | 123  | Unexpected state at this point (see H24/H25)         |
| M12 | widgets/forms.py       | 124  | Always asked rate spinbox in survey vs form           |
| M13 | widgets/search.py      | 123  | Tag tracking                                          |
| M14 | widgets/documents.py   | 121  | Tag tracking                                          |
| M15 | browsers.py            | 784  | Buttons in drawer handling                            |
| M16 | documents.py           | 157  | Flip icon                                             |
| M17 | links.py               | —    | Link table connection to link_affiliate               |

## 🟢 Low Priority (L-Series)

| ID  | Priority | File         | Line | Description                            |
|-----|----------|--------------|------|----------------------------------------|
| L1  | 🟢 L1    | widgets/new.py | 189  | Cross-tool file format integration      |
| L2  | 🟢 L2    | widgets/new.py | 193  | Google Drive browser/API connection     |
| L3  | 🟢 L3    | —            | —    | Audio playback support                  |
| L4  | 🟢 L4    | —            | —    | Video playback support                  |
| L5  | 🟢 L5    | —            | —    | Skills management module                |
| L6  | 🟢 L6    | —            | —    | Tags system module                      |
| L7  | 🟢 L7    | —            | —    | Workflows automation                    |
| L8  | 🟢 L8    | —            | —    | Media management                        |
| L9  | 🟢 L9    | —            | —    | Port management                         |

## 📋 Implementation Phases

### Phase 1: Bug Fixes (Critical) — COMPLETED ✅
C1–C8 all resolved. H22 Context Menu fixed. H23 confirmed not a problem.

### Phase 2: Core Document Types (P1) — 2 remaining
1. **ebook** — EPUB/AZW/MOBI reader 🔴
2. **projects** — PAXN project management 🔴

### Phase 3: Productivity Features (P2) — 4 items
container, cad, reports, data (partial)

### Phase 4: Data & Advanced (P3)
config, updates

### Phase 5: Low Priority (L-Series)
audio, video, skills, tags, workflows, media, ports

## 🔧 Implementation Notes

### H21 — Toolbar Missing
Main Document Toolbar missing from PDF and Image document types.
Fix: ensure `NchantdOfficeDocumentMixin.init_toolbar()` is called for all document types and toolbar data exists in database (nchantd_menu/nchantd_menu_item tables).

### H24/H25 — Toolbox & Tab Selection
`widgets/widgets.py:123` — When switching tabs, the toolbox drawer/widget does not update, and the catalog tab surfaces on the first click instead of the intended tab.

### Web Browser Features — COMPLETED ✅
- URL Inspection (Drawer 100) — URL, domain, subdomain, params, whois ✅
- Settings Panel (Drawer 200) — Privacy controls, home page settings ✅
- Download Manager (Drawer 300) — Open Downloads folder in FileSystem tab ✅

## 📊 Summary

| Category              | Count       |
|-----------------------|-------------|
| ✅ Completed          | 16          |
| 🔴 Critical Bugs      | 0 (C1–C8)   |
| 🟠 High Priority      | 21 (19 TODO) |
| 🟡 Medium Priority    | 17          |
| 🟢 Low Priority       | 9           |
| 🚀 Performance        | 7           |
| ✅ Document Types     | 18          |
| ❌ Missing Types      | 23          |
| **Total Active Items** | **71**      |
