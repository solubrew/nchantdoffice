




, 'tab_type': 'custom_widget', 'location': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}}
2026-07-28 23:18:07,946 - nchantdoffice.widgets.tabs                 42: INFO     - [tabs] NchantdOfficeTab.__init__ parent=NchantdOfficeHelpDocs
2026-07-28 23:18:07,949 - nchantdoffice.widgets.tabs                 52: INFO     - [tabs] NchantdOfficeTab.initModel cfg_provided=False
2026-07-28 23:18:07,953 - nchantdoffice.widgets.config.help         118: INFO     - [help] initView: reader build failed: 'document'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/config/help.py", line 115, in initView
    self.reader = NchantdOfficePDF(self, {}).initWidget()
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/pdfs.py", line 192, in initWidget
    self.initModel()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/pdfs.py", line 157, in initModel
    logma.json(self.config.dikt["document"])
               ~~~~~~~~~~~~~~~~^^^^^^^^^^^^
KeyError: 'document'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/widgets.py", line 149, in on_tab_focus
    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3344, in load_tab
    super().load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 238, in load_tab
    self.tab_widgets[tabn].dummy = False
    ~~~~~~~~~~~~~~~~^^^^^^
IndexError: list index out of range
2026-07-28 23:18:11,296 - nchantrs.widgets.widgets                  414: INFO     - Focus Out




2026-07-28 22:52:27,642 - nchantrs.widgets.widgets                  446: INFO     - Mouse Press Event
2026-07-28 22:52:27,642 - nchantrs.widgets.widgets                  466: INFO     - Left Click <PySide6.QtGui.QMouseEvent(MouseButtonPress LeftButton pos=295,292 scn=641,361 gbl=641,387 dev=QInputDevice(QPointingDevice("Virtual core pointer" Mouse id=2 seat=30002 caps=Position|Scroll|Hover buttonCount=32))>
2026-07-28 22:52:27,642 - nchantrs.widgets.widgets                  467: INFO     - Left Click
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/workbooks/matricies.py", line 1713, in on_selection_changed
    self.cell_ref_label.setText(address)
    ^^^^^^^^^^^^^^^^^^^
AttributeError: 'NchantdOfficeMatrix' object has no attribute 'cell_ref_label'






2026-07-27 19:45:49,937 - nchantdoffice.models                      391: INFO     - Dumped Content {"content": {"file_path": "/home/solubrew/Downloads/ssrn-4668072.pdf"}, "path": "/home/solubrew/Downloads/ssrn-4668072.pdf"}
2026-07-27 19:45:49,937 - nchantdoffice.models                      394: INFO     - Encoded Dictionary b'eyJjb250ZW50IjogeyJmaWxlX3BhdGgiOiAiL2hvbWUvc29sdWJyZXcvRG93bmxvYWRzL3Nzcm4tNDY2ODA3Mi5wZGYifSwgInBhdGgiOiAiL2hvbWUvc29sdWJyZXcvRG93bmxvYWRzL3Nzcm4tNDY2ODA3Mi5wZGYifQ=='
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/buttons.py", line 177, in <lambda>
    self.clicked.connect(lambda checked: self.on_click(checked, handler, params))
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/buttons.py", line 169, in on_click
    handler(signal, params)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 222, in cmd_save_tab
    self.save()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/pdfs.py", line 372, in save
    super().save()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 776, in save
    super().save()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 457, in save
    self.app.model.store_document(self.document)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 1985, in store_document
    self.add_document_content(pydoc.to_dict(), version=pydoc.version)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 433, in add_document_content
    self.store.store_doc_media_content(payload)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 2767, in store_doc_media_content
    int(content["version"]) + 1,
    ^^^^^^^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: '1.0.1.0'


le_type": "sketch", "google_drive_bit": 0, "local_drive_bit": 0, "import": 0}', 'version': None, 'tab_type': 'add_sketch_document_nchantdsketch', 'location': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}}, 'apps': ['nchantrs', 'nchantdoffice'], 'app': 'nchantdoffice', 'pos': 'center'}
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/widgets.py", line 163, in on_tab_focus
    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3072, in load_tab
    super().load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 237, in load_tab
    self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab), tabset, tab))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3106, in load_widget
    tabW = super().load_widget(cfg, tabset, document, tab_type)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 263, in load_widget
    tabW = loadWidget(self.parent, cfg)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 1057, in loadWidget
    registered_widget = lookupWidget(list(cfg.keys())[0])
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 1065, in lookupWidget
    return kahndor.Instruct(pxcfg).select("RegisteredWidgets").dikt[key]
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^
KeyError: 'NchantdWidget'
2026-07-27 19:45:13,889 - nchantrs.widgets.browsers.browsers        336: INFO     - URL Changed: PySide6.QtCore.QUrl('https://duckduckgo.com/')
2026-07-27 19:45:13,890 - nchantrs.widgets.browsers.browsers        348: INFO     - Failed to track link: NchantdCloakModel.store_link() got an unexpected keyword argument 'tag'



## Status (2026-07-28)

The 5 errors recorded above (H52/H53/H55 sprint) were fixed in the
commits documented in `TODOs.md` under "H53–H55 sprint — sketch /
matrix regression + score lifts". All historical traces above are
preserved for audit reference.

Sprint 1 + Sprint 2 (2026-07-28) closed the remaining live `TODOs.md`
bugs and shipped defensive fixes. See
`TODOs.md → Sprint 1 + Sprint 2 (2026-07-28) — persistence + safety
pass` for the full commit list and the post-sprint test surface
(26 passed, 2 skipped).

No new error traces were added during Sprint 1 + Sprint 2 because the
fixes were scoped to preventive coverage rather than crash-log
capture.