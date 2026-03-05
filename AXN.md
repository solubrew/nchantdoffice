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

### PyfficeDocument Implementations Required

| # | Pyffice Document Type | Pyffice Module | NchantdOffice Document | Status |
|---|----------------------|----------------|----------------------|--------|
| 1 | PyfficeNotebook | notebooks/notebooks.py | NchantdOfficeNotebook | ❌ |
| 2 | PyfficeTable | databases/table.py | NchantdOfficeTable | ❌ |
| 3 | PyfficeSpreadSheet | spreadsheet/spreadsheet.py | NchantdOfficeSpreadsheet | ❌ |
| 4 | PyfficeMatrix | spreadsheet/spreadsheet.py | NchantdOfficeMatrix | ❌ |
| 5 | PyfficeChart | charts/charts.py | NchantdOfficeChart | ❌ |
| 6 | PyfficePresentation | presentation/presentation.py | NchantdOfficePresentation | ❌ |
| 7 | PyfficeScript | text/text.py | NchantdOfficeScript | ❌ |
| 8 | PyfficeText | items/text.py | NchantdOfficeText | ❌ |
| 9 | PyfficePDF | images/pdfs.py | NchantdOfficePDF | ❌ |
| 10 | PyfficeImage | images/images.py | NchantdOfficeImage | ❌ |
| 11 | PyfficeVideo | video/video.py | NchantdOfficeVideo | ❌ |
| 12 | PyfficeAudio | audio/audio.py | NchantdOfficeAudio | ❌ |
| 13 | PyfficeContact | contacts/contacts.py | NchantdOfficeContact | ❌ |
| 14 | PyfficeWork | items/tasks.py | NchantdOfficeWork | ❌ |
| 15 | PyfficeTaskFrame | items/tasks.py | NchantdOfficeTask | ❌ |
| 16 | PyfficePersona | items/persona.py | NchantdOfficePersona | ❌ |
| 17 | PyfficeForm | forms/forms.py | NchantdOfficeForm | ❌ |
| 18 | PyfficeSurvey | forms/surveys.py | NchantdOfficeSurvey | ❌ |
| 19 | PyfficeResponse | forms/surveys.py | NchantdOfficeResponse | ❌ |
| 20 | PyfficeWebPage | web/web.py | NchantdOfficeWebPage | ❌ |
| 21 | PyfficeWebBrowser | web/web.py | NchantdOfficeWebBrowser | ❌ |
| 22 | PyfficeConfig | config/config.py | NchantdOfficeConfig | ❌ |
| 23 | PyfficeColorPalette | items/colors.py | NchantdOfficeColorPalette | ❌ |
| 24 | PyfficePlaylist | workflows/playlists.py | NchantdOfficePlaylist | ❌ |

### PyfficeManager Types (Collections)

| # | Pyffice Manager Type | Pyffice Module | Status |
|---|---------------------|----------------|--------|
| 1 | PyfficeCodex | pyffice.py | ❌ |
| 2 | PyfficeDatabaseManager | databases/databases.py | ❌ |
| 3 | PyfficeCalendar | calendars/calendars.py | ❌ |
| 4 | PyfficeMailBox | email/email.py | ❌ |
| 5 | PyfficeRolodex | contacts/contacts.py | ❌ |
| 6 | PyfficeTagsManager | tags/manager.py | ❌ |
| 7 | PyfficeFileSystem | filesystems/filesystems.py | ❌ |
| 8 | PyfficeSketch | diagrams/diagrams.py | ❌ |

### Implementation Pattern

```python
# Each NchantdOffice document should inherit from PyfficeDocument
# Example: NchantdOfficeScript implements PyfficeScript

from pyffice.document import PyfficeDocument
from pyffice.text.text import PyfficeScript

class NchantdOfficeScript(NchantdOfficeDocument, PyfficeScript):
    """Script document - implements PyfficeScript"""
    pass
```

### Toolbox Integration (per document type)
- [ ] Dynamic toolbox tools based on NchantdOfficeDocument type
- [ ] Connect far left toolbar to toolbox population
- [ ] Connect + Default tab catalog to toolbox population

## Phase 4: Agent/Memory Layers
- [x] glain (agent memory/knowledge)
- [x] sentinel (supervisory loop)
- [x] nchantdagent (agent module)

## Phase 5: UI Integration

### P0 Issues
| Issue | Status |
|-------|--------|
| Center app tab dragging | ❌ |
| Tree node drag-and-drop | ❌ |
| Cross-pane tab dragging | ❌ |
| Tab-to-tree drag-and-drop | ❌ |
| Right-click context menus | 🔶 Partial |

### P1 Issues
| Issue | Status |
|-------|--------|
| Right toolbox search | ❌ |
| Right toolbox drawer items | 🔶 Partial |

## Phase 6: Build & Deploy

- [ ] Clean build to zuh environment
- [ ] Test all integrations
- [ ] Verify Pyffice inheritance in documents
