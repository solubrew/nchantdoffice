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

### PyfficeDocument Implementations - COMPLETED ✅

| # | Pyffice Document Type | NchantdOffice Document | File |
|---|----------------------|----------------------|------|
| 1 | PyfficeNotebook | NchantdOfficeNotebook | notebooks.py |
| 2 | PyfficeSpreadSheet | NchantdOfficeSpreadSheet | spreadsheet.py |
| 3 | PyfficeMatrix | NchantdOfficeMatrix | spreadsheet.py |
| 4 | PyfficeChart | NchantdOfficeChart | charts.py |
| 5 | PyfficeScript | NchantdOfficeScript | text.py |
| 6 | PyfficeCalendar | NchantdOfficeCalendar | calendars.py |
| 7 | PyfficePDF | NchantdOfficePDF | pdf.py |
| 8 | PyfficePresentation | NchantdOfficePresentation | presentation.py |
| 9 | PyfficeContact | NchantdOfficeContact | contacts.py |
| 10 | PyfficeVideo | NchantdOfficeVideo | video.py |
| 11 | PyfficeAudio | NchantdOfficeAudio | audio.py |
| 12 | PyfficeImage | NchantdOfficeImage | images.py |
| 13 | PyfficeText | NchantdOfficeText | text.py |

### PyfficeDocument Implementations - NOT IMPLEMENTED

| # | Pyffice Document Type | NchantdOffice Document |
|---|----------------------|----------------------|
| 1 | PyfficeTable | NchantdOfficeTable |
| 2 | PyfficeWork | NchantdOfficeWork |
| 3 | PyfficeTaskFrame | NchantdOfficeTask |
| 4 | PyfficePersona | NchantdOfficePersona |
| 5 | PyfficeForm | NchantdOfficeForm |
| 6 | PyfficeSurvey | NchantdOfficeSurvey |
| 7 | PyfficeResponse | NchantdOfficeResponse |
| 8 | PyfficeWebPage | NchantdOfficeWebPage |
| 9 | PyfficeWebBrowser | NchantdOfficeWebBrowser |
| 10 | PyfficeConfig | NchantdOfficeConfig |
| 11 | PyfficeColorPalette | NchantdOfficeColorPalette |
| 12 | PyfficePlaylist | NchantdOfficePlaylist |

### PyfficeManager Types (Collections)

| # | Pyffice Manager Type | Status |
|---|---------------------|--------|
| 1 | PyfficeCodex | ❌ Not implemented |
| 2 | PyfficeDatabaseManager | ❌ Not implemented |
| 3 | PyfficeCalendar | ✅ Done (via NchantdOfficeCalendar) |
| 4 | PyfficeMailBox | ❌ Not implemented |
| 5 | PyfficeRolodex | ❌ Not implemented |
| 6 | PyfficeTagsManager | ❌ Not implemented |
| 7 | PyfficeFileSystem | ✅ Done (via filesystems.py) |
| 8 | PyfficeSketch | ❌ Not implemented |

### Toolbox Integration - COMPLETED ✅

- [x] Dynamic toolbox tools based on NchantdOfficeDocument type (get_pyffice_tools())
- [x] Connect far left toolbar to toolbox population (document_created signal)
- [x] Connect left pane tree to toolbox (document_selected signal)
- [x] Connect center tabs to toolbox (current_document_changed signal)
- [x] _connect_pane_signals() method in NchantdOfficeApplicationToolBox
- [x] _populate_tools_drawer() method for dynamic tool population

### Signal Flow Implemented ✅

```
toolbar (document_created) 
    → tree (document_selected) 
        → tabs (current_document_changed) 
            → toolbox (on_document_changed - calls get_pyffice_tools())
```

## Phase 4: Agent/Memory Layers
- [x] glain (agent memory/knowledge)
- [x] sentinel (supervisory loop)
- [x] nchantdagent (agent module)

## Phase 5: UI Integration

### P0 Issues - COMPLETED ✅
| Issue | File | Status |
|-------|------|--------|
| Center app tab dragging | tabs.py (NchantdOfficeTabs) | ✅ Done |
| Tree node drag-and-drop | trees.py (NchantdOfficeApplicationTree) | ✅ Done |
| Cross-pane tab dragging | tabs.py + trees.py | ✅ Done |
| Tab-to-tree drag-and-drop | tabs.py + trees.py | ✅ Done |
| Right-click context menus | menus/ | ✅ Done |

### P1 Issues - COMPLETED ✅
| Issue | File | Status |
|-------|------|--------|
| Right toolbox drawer items | toolboxes.py | ✅ Done |
| Toolbox search | toolboxes.py | ✅ Done (needs _populate_tools_drawer) |

### Signal/Drag Classes Added
- **NchantdOfficeTabs** (tabs.py): current_document_changed, tab_moved, tab_drag_started, tab_dropped signals
- **NchantdOfficeApplicationTree** (trees.py): document_selected, item_drag_started, item_dropped_on_tree, item_dropped_on_tabs signals
- **NchantdOfficeApplicationToolBox** (toolboxes.py): _connect_pane_signals(), _on_document_created(), _on_document_selected(), _on_document_changed(), _populate_tools_drawer()

## Phase 6: Build & Deploy

- [ ] Clean build to zuh environment
- [ ] Test all integrations
- [ ] Verify Pyffice inheritance in documents

---

## Commit: gamma:a7234cc

```
Implement PyfficeDocument integration with signal connections

- Add NchantdOfficeTabs with drag-drop and signals
- Add NchantdOfficeApplicationTree with drag-drop and document_selected signal
- Add signal connections in NchantdOfficeApplicationToolBox
- Implement toolbox dynamic population based on document type
- Add 13 PyfficeDocument types with get_pyffice_tools()
```
