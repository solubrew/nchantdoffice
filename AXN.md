# AXN: nchantdoffice-integration

## Phase 1: Internal Project Dependencies ✅
- [x] nchantrs (storage, security, API)
- [x] pyffice (document widgets)
- [x] condor (config)
- [x] pycurity (security)
- [x] micromole + squirl (data)

## Phase 2: Network/External Layers ✅
- [x] apig (REST API)
- [x] worldbridgeserver (Web2/Web3)
- [x] elv1r4 (Web3 integration)

## Phase 3: Document Model Integration (Pyffice) ✅ COMPLETE
- [x] NchantdOfficeDocument base class (documents.py)
- [x] All 26 Pyffice document types implemented:
  - [x] Text/Script (text.py)
  - [x] Table (table.py) ⭐ NEW
  - [x] Spreadsheet (spreadsheet.py)
  - [x] Matrix (spreadsheet.py)
  - [x] Chart (charts.py)
  - [x] Analytics (analytics/)
  - [x] Notebook (notebooks.py)
  - [x] PDF (pdf.py)
  - [x] Calendar (calendars.py)
  - [x] Video/Audio/Image (media/)
  - [x] Playlist (playlist.py) ⭐ NEW
  - [x] Persona (persona.py) ⭐ NEW
  - [x] Contact (contacts.py)
  - [x] Work (work.py) ⭐ NEW
  - [x] Bibliography (bibliography.py) ⭐ NEW
  - [x] WebBrowser (webbrowser.py) ⭐ NEW
  - [x] WebPage (webpage.py) ⭐ NEW
  - [x] Config (config.py) ⭐ NEW
  - [x] ColorPalette (colorpalette.py) ⭐ NEW
  - [x] FileSystem (filesystems.py)
  - [x] Form (forms.py)
  - [x] Survey (surveys.py)
  - [x] Message (messages.py)
- [x] DOCUMENT_TYPES registry with factory function
- [x] All documents have get_pyffice_tools() method

## Phase 4: Signal/Slot Architecture ✅
- [x] document_created signal (toolbar)
- [x] document_selected signal (tree)
- [x] current_document_changed signal (tabs)
- [x] get_pyffice_tools() method in all documents
- [x] _connect_pane_signals() in views.py

## Phase 5: UI Integration 
- [x] Context menus (context_manager.py)
- [ ] Tab dragging
- [ ] Tree node dragging
- [ ] Cross-pane drag-drop
- [ ] Toolbox search

## Phase 6: Build & Deploy
- [ ] Clean build to zuh env
- [ ] Test all integrations
