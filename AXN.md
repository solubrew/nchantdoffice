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
  - [x] Table (table.py)
  - [x] Spreadsheet (spreadsheet.py)
  - [x] Matrix (spreadsheet.py)
  - [x] Chart (charts.py)
  - [x] Analytics (analytics/)
  - [x] Notebook (notebooks.py)
  - [x] PDF (pdf.py)
  - [x] Calendar (calendars.py)
  - [x] Video/Audio/Image (media/)
  - [x] Playlist (playlist.py)
  - [x] Persona (persona.py)
  - [x] Contact (contacts.py)
  - [x] Work (work.py)
  - [x] Bibliography (bibliography.py)
  - [x] WebBrowser (webbrowser.py)
  - [x] WebPage (webpage.py)
  - [x] Config (config.py)
  - [x] ColorPalette (colorpalette.py)
  - [x] FileSystem (filesystems.py)
  - [x] Form (forms.py)
  - [x] Survey (surveys.py)
  - [x] Message (messages.py)
- [x] DOCUMENT_TYPES registry with factory function
- [x] All documents have get_pyffice_tools() method

## Phase 4: Signal/Slot Architecture ✅ COMPLETE
- [x] document_created signal (toolbars.py - NchantdNewDocumentToolBar)
- [x] document_selected signal (trees.py - NchantdOfficeApplicationTree)
- [x] current_document_changed signal (tabs.py - NchantdOfficeTabs)
- [x] tab_moved signal (tabs.py)
- [x] tab_drag_started signal (tabs.py)
- [x] tab_dropped signal (tabs.py)
- [x] item_drag_started signal (trees.py)
- [x] item_dropped_on_tabs signal (trees.py)
- [x] get_pyffice_tools() method in all documents
- [x] _connect_pane_signals() in toolboxes.py

## Phase 5: UI Integration ✅ COMPLETE
- [x] Tab dragging (tabs.py - _setup_drag_drop(), mousePressEvent, mouseMoveEvent, dragEnterEvent, dropEvent)
- [x] Tree node dragging (trees.py - mousePressEvent, mouseMoveEvent, dragEnterEvent, dropEvent)
- [x] Cross-pane drag-drop (tabs.py + trees.py - handles application/x-nchantd-tab and application/x-nchantd-tree-item)
- [x] Toolbox search (toolboxes.py - init_search(), _perform_search(), _clear_search())
- [x] Context menus (menus/context_manager.py)

## Phase 6: Build & Deploy
- [ ] Clean build to zuh env
- [ ] Test all integrations
- [ ] Verify Pyffice inheritance works correctly
