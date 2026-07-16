# TODOs

Generated: 2026-07-13
HEAD: b70a0c4
Total markers: ~280 (27 descriptive + ~248 stub methods)

## Descriptive TODOs (actionable items)

### models.py
- Line 575: does this need to be moved to the app set of tables
- Line 885: need to refactor how the widget is added to the database using the app_document_type registry
- Line 1185: implement view then pull data from it
- Line 1255: change this so that a tab code, images and tables
- Line 1340: Implement session parsing
- Line 1366: add import of things like notion and evernote in the future
- Line 1396: Implement this method when the required 'document' object is available.
- Line 1466: increment version

### catalogs.py
- Line 293: add search bar to layout...with filter capabilities

### config/accounts.py
- Line 170: get user name from account api
- Line 180: connect to service and get details
- Line 207: implement a larger button graphic
- Line 364: Implement actual server sync

### config/help.py
- Line 79: need to implement a download of pdf files and then load an index that can navigate through them

### config/settings.py
- Line 245: possiblly only allow pro users to turn off
- Line 289: pull from database combine sequence with name...
- Line 290: change right selector to a position changer

### config/sources.py
- Line 76: build in additional controls for size ["full", "%10"]
- Line 82: implement config changes to make the pane standout
- Line 114: get apikey from pycurity and populate using an obscured version
- Line 128: add a visibliity switch at the end of the entry box
- Line 139: create a new NchantdOfficeWebBrowser Document
- Line 154: replace obscured key with real key

### controls/toolbars.py
- Line 156: need to figure out how to look up the widget from the document types table
- Line 160: Switch to MultiInstance
- Line 238: if there are multiple notes then the position will need to increment

### controls/toolboxes.py
- Line 191: implement search panes
- Line 192: correct spacing of Node Configuration Drawer to tighten up the Node Pane and Tab Pane
- Line 325: implement loading new nchantd office instance
- Line 377: implement loading new nchantd office instance

### analytics/analytics.py
- Line 33: Integrate Orange3

### analytics/charts.py
- Line 60: need to get list of sources
- Line 94: get a list of where the chart is used/connected
- Line 193: send over data from the document to populate the chart

### atnrg/prompts.py
- Line 89: unsure how to integrate this at the moment
- Line 272: need a pane to allow setting of days to keep chat history
- Line 293: show either a connection available or create connection to handle apis for the model

### panes/charts.py
- Line 169: implement this as button group
- Line 194: BorderConfigBar was a copy of text config and needs to be updated to apply to border styles

### panes/documents.py
- Line 121: add tag tracking

### panes/forms.py
- Line 124: change always asked to a asked rate spinbox really should be part of the survey and not the form itself

### panes/new.py
- Line 189: how to integrate various formats across tools for specific tool types like a local file to open excel
- Line 198: develop the widget_code override based on unique options selections

### panes/search.py
- Line 123: add tag tracking

## Stub Methods (awaiting implementation)

### documents/workbooks/matricies.py
- 46 stub methods (# TODO: implement method)

### documents/media/sketches.py
- 34 stub methods (# TODO: implement method)

### documents/media/scripts.py
- 29 stub methods (# TODO: implement method)

### documents/media/images.py
- 25 stub methods (# TODO: implement method)

### documents/documents.py
- 24 stub methods (# TODO: implement method)

### documents/managers/calendars.py
- 21 stub methods (# TODO: implement method)

### documents/analytics/charts.py
- 18 stub methods (# TODO: implement method)

### documents/managers/filesystems.py
- 18 stub methods (# TODO: implement method)

### documents/media/forms.py
- 15 stub methods (# TODO: implement method)

### config/settings.py
- 12 stub methods (# TODO: implement method)

### documents/atnrg/browsers.py
- 12 stub methods (# TODO: implement method)

### documents/media/pdfs.py
- 6 stub methods (# TODO: implement method)

### documents/workbooks/notebooks.py
- 5 stub methods (# TODO: implement method)

### catalogs.py
- 4 stub methods (# TODO: implement method)

### documents/atnrg/prompts.py
- 3 stub methods (# TODO: implement method)

### documents/atnrg/contacts.py
- 1 stub method (# TODO: implement method)

---
Total: 27 descriptive TODOs + ~248 stub methods = ~280 total markers
