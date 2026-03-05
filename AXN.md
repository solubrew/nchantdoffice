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

| # | Pyffice Document Type | NchantdOffice Document | File | Status |
|---|----------------------|----------------------|------|--------|
| 1 | PyfficeNotebook | NchantdOfficeNotebook | notebooks.py | ✅ Done |
| 2 | PyfficeSpreadSheet | NchantdOfficeSpreadSheet | spreadsheet.py | ✅ Done |
| 3 | PyfficeMatrix | NchantdOfficeMatrix | spreadsheet.py | ✅ Done |
| 4 | PyfficeChart | NchantdOfficeChart | charts.py | ✅ Done |
| 5 | PyfficeScript | NchantdOfficeScript | text.py | ✅ Done |
| 6 | PyfficeText | NchantdOfficeText | text.py | ✅ Done |
| 7 | PyfficeCalendar | NchantdOfficeCalendar | calendars.py | ✅ Done |
| 8 | PyfficePDF | NchantdOfficePDF | pdf.py | ✅ Done |
| 9 | PyfficePresentation | NchantdOfficePresentation | presentation.py | ✅ Done |
| 10 | PyfficeVideo | NchantdOfficeVideo | video.py | ✅ Done |
| 11 | PyfficeAudio | NchantdOfficeAudio | audio.py | ✅ Done |
| 12 | PyfficeContact | NchantdOfficeContact | contacts.py | ✅ Done |

### PyfficeDocument Implementations - NOT IMPLEMENTED

| # | Pyffice Document Type | NchantdOffice Document |
|---|----------------------|----------------------|
| 1 | PyfficeTable | NchantdOfficeTable |
| 2 | PyfficeImage | NchantdOfficeImage |
| 3 | PyfficeWork | NchantdOfficeWork |
| 4 | PyfficeTaskFrame | NchantdOfficeTask |
| 5 | PyfficePersona | NchantdOfficePersona |
| 6 | PyfficeForm | NchantdOfficeForm |
| 7 | PyfficeSurvey | NchantdOfficeSurvey |
| 8 | PyfficeResponse | NchantdOfficeResponse |
| 9 | PyfficeWebPage | NchantdOfficeWebPage |
| 10 | PyfficeWebBrowser | NchantdOfficeWebBrowser |
| 11 | PyfficeConfig | NchantdOfficeConfig |
| 12 | PyfficeColorPalette | NchantdOfficeColorPalette |
| 13 | PyfficePlaylist | NchantdOfficePlaylist |

### PyfficeManager Types (Collections)

| # | Pyffice Manager Type | Status |
|---|---------------------|--------|
| 1 | PyfficeCodex | ❌ Not implemented |
| 2 | PyfficeDatabaseManager | ❌ Not implemented |
| 3 | PyfficeCalendar | ✅ Done |
| 4 | PyfficeMailBox | ❌ Not implemented |
| 5 | PyfficeRolodex | ❌ Not implemented |
| 6 | PyfficeTagsManager | ❌ Not implemented |
| 7 | PyfficeFileSystem | ✅ Done |
| 8 | PyfficeSketch | ❌ Not implemented |

### Toolbox Integration - COMPLETED ✅

- [x] Dynamic toolbox tools based on NchantdOfficeDocument type
- [x] Connect far left toolbar to toolbox population (document_created signal)
- [x] Connect left pane tree to toolbox (document_selected signal)
- [x] Connect center tabs to toolbox (current_document_changed signal)
- [x] Toolbox search functionality implemented

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

## Phase 5: UI Integration - COMPLETED ✅

### P0 Issues
| Issue | Status | File |
|-------|--------|------|
| Center app tab dragging | ✅ Done | widgets/tabs.py |
| Tree node drag-and-drop | ✅ Done | widgets/trees.py |
| Cross-pane tab dragging | ✅ Done | widgets/tabs.py + trees.py |
| Tab-to-tree drag-and-drop | ✅ Done | widgets/tabs.py + trees.py |
| Right-click context menus | ✅ Done | menus/context_manager.py |

### P1 Issues
| Issue | Status |
|-------|--------|
| Right toolbox search | ✅ Done |
| Right toolbox drawer items | ✅ Done |

## Phase 6: Build & Deploy

- [ ] Clean build to zuh environment
- [ ] Test all integrations
- [ ] Verify Pyffice inheritance in documents
