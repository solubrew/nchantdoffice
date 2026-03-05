# AXN: NchantdOffice Integration Plan

## Project: app_nchantdoffice

## Phase 1: Internal Project Dependencies
- [x] nchantrs (storage, security, API)
- [x] pyffice (document widgets)
- [x] condor (config)
- [x] pycurity (security)
- [x] micromole + squirl (data)

## Phase 2: Network/External Layers
- [x] apig (REST API)
- [x] worldbridgeserver (Web2/Web3)
- [x] elv1r4 (Web3 integration)

## Phase 3: Document Model Integration (Pyffice)

### PyfficeDocument Implementations - COMPLETED

| # | Pyffice Document Type | Pyffice Module | NchantdOffice Document | Status |
|---|----------------------|----------------|----------------------|--------|
| 1 | PyfficeNotebook | notebooks/notebooks.py | NchantdOfficeNotebook | ✅ Done |
| 2 | PyfficeSpreadSheet | spreadsheet/spreadsheet.py | NchantdOfficeSpreadSheet | ✅ Done |
| 3 | PyfficeMatrix | spreadsheet/spreadsheet.py | NchantdOfficeMatrix | ✅ Done |
| 4 | PyfficeChart | charts/charts.py | NchantdOfficeChart | ✅ Done |
| 5 | PyfficeScript | text/text.py | NchantdOfficeScript | ✅ Done |
| 6 | PyfficeCalendar | calendars/calendars.py | NchantdOfficeCalendar | ✅ Done |
| 7 | PyfficePDF | images/pdfs.py | NchantdOfficePDF | ✅ Done |

### PyfficeDocument Implementations - NOT IMPLEMENTED

| # | Pyffice Document Type | Pyffice Module | NchantdOffice Document |
|---|----------------------|----------------|----------------------|
| 1 | PyfficeTable | databases/table.py | NchantdOfficeTable |
| 2 | PyfficePresentation | presentation/presentation.py | NchantdOfficePresentation |
| 3 | PyfficeText | items/text.py | NchantdOfficeText |
| 4 | PyfficeImage | images/images.py | NchantdOfficeImage |
| 5 | PyfficeVideo | video/video.py | NchantdOfficeVideo |
| 6 | PyfficeAudio | audio/audio.py | NchantdOfficeAudio |
| 7 | PyfficeContact | contacts/contacts.py | NchantdOfficeContact |
| 8 | PyfficeWork | items/tasks.py | NchantdOfficeWork |
| 9 | PyfficeTaskFrame | items/tasks.py | NchantdOfficeTask |
| 10 | PyfficePersona | items/persona.py | NchantdOfficePersona |
| 11 | PyfficeForm | forms/forms.py | NchantdOfficeForm |
| 12 | PyfficeSurvey | forms/surveys.py | NchantdOfficeSurvey |
| 13 | PyfficeResponse | forms/surveys.py | NchantdOfficeResponse |
| 14 | PyfficeWebPage | web/web.py | NchantdOfficeWebPage |
| 15 | PyfficeWebBrowser | web/web.py | NchantdOfficeWebBrowser |
| 16 | PyfficeConfig | config/config.py | NchantdOfficeConfig |
| 17 | PyfficeColorPalette | items/colors.py | NchantdOfficeColorPalette |
| 18 | PyfficePlaylist | workflows/playlists.py | NchantdOfficePlaylist |

### PyfficeManager Types (Collections)

| # | Pyffice Manager Type | Pyffice Module | Status |
|---|---------------------|----------------|--------|
| 1 | PyfficeCodex | pyffice.py | ❌ Not implemented |
| 2 | PyfficeDatabaseManager | databases/databases.py | ❌ Not implemented |
| 3 | PyfficeCalendar | calendars/calendars.py | ✅ Done (via NchantdOfficeCalendar) |
| 4 | PyfficeMailBox | email/email.py | ❌ Not implemented |
| 5 | PyfficeRolodex | contacts/contacts.py | ❌ Not implemented |
| 6 | PyfficeTagsManager | tags/manager.py | ❌ Not implemented |
| 7 | PyfficeFileSystem | filesystems/filesystems.py | ✅ Done (via filesystems.py) |
| 8 | PyfficeSketch | diagrams/diagrams.py | ❌ Not implemented |

### Toolbox Integration - COMPLETED

- [x] Dynamic toolbox tools based on NchantdOfficeDocument type
- [x] Connect far left toolbar to toolbox population (document_created signal)
- [x] Connect left pane tree to toolbox (document_selected signal)
- [x] Connect center tabs to toolbox (current_document_changed signal)

### Signal Flow Implemented

```
toolbar (document_created) 
    → tree (document_selected) 
        → tabs (current_document_changed) 
            → toolbox (on_document_changed - calls get_pyffice_tools())
```

### Implementation Details

| File | Component | Implementation |
|------|-----------|----------------|
| `widgets/controls/toolbars.py` | NchantdNewDocumentToolBar | document_created signal |
| `widgets/trees.py` | NchantdOfficeApplicationTree | document_selected signal |
| `widgets/tabs.py` | NchantdOfficeTabSet | current_document_changed signal |
| `widgets/controls/toolboxes.py` | NchantdOfficeApplicationToolBox | on_document_changed(), on_document_created(), get_pyffice_tools() |
| `views.py` | NchantdOfficeCloakView | _connect_pane_signals() |
| `widgets/documents/documents.py` | NchantdOfficeDocument | inherits PyfficeDocument |
| `widgets/documents/text.py` | NchantdOfficeScript | inherits PyfficeScript + get_pyffice_tools() |

## Phase 4: Agent/Memory Layers
- [x] glain (agent memory/knowledge)
- [x] sentinel (supervisory loop)
- [x] nchantdagent (agent module)

## Phase 5: UI Integration

### P0 Issues - COMPLETED
| Issue | Status |
|-------|--------|
| Center app tab dragging | ✅ Implemented in tabs.py |
| Tree node drag-and-drop | ✅ Implemented in trees.py |
| Cross-pane tab dragging | ✅ Implemented in tabs.py + trees.py |
| Tab-to-tree drag-and-drop | ✅ Implemented in tabs.py + trees.py |
| Right-click context menus | ✅ Implemented via context_manager.py |

### P1 Issues - COMPLETED
| Issue | Status |
|-------|--------|
| Right toolbox search | ✅ Implemented in toolboxes.py (_init_search, search_toolbox) |
| Right toolbox drawer items | ✅ Implemented (node, tabs, tools drawers) |

### Signal Connections - COMPLETED
```
toolbar (document_created) 
    → tree (document_selected) 
        → tabs (current_document_changed) 
            → toolbox (on_document_changed - calls get_pyffice_tools())
```

### Implementation Verification

| File | Component | Verified |
|------|-----------|----------|
| widgets/tabs.py | Tab drag-drop | ✅ Lines 67-159 |
| widgets/trees.py | Tree drag-drop | ✅ Lines 107-215 |
| widgets/controls/toolboxes.py | Toolbox search | ✅ Lines 59-148 |
| views.py | Signal connections | ✅ _connect_pane_signals() |
| widgets/documents/documents.py | PyfficeDocument | ✅ Line ~280 |
| widgets/documents/text.py | get_pyffice_tools | ✅ Lines 42-52 |

## Phase 6: Build & Deploy

- [x] All P0/P1 issues implemented
- [ ] Clean build to zuh environment
- [ ] Test all integrations
- [ ] Verify Pyffice inheritance in documents
