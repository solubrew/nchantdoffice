











2026-07-27 13:41:59,844 - nchantdoffice.widgets.tabs                 52: INFO     - [tabs] NchantdOfficeTab.initModel cfg_provided=False
2026-07-27 13:41:59,851 - pyffice.document                          497: WARNING  - Document {'PyfficeDocument': {'template': {'did': None, 'name': None, 'description': None, 'path': None, 'location': None, 'syntax': None, 'encoding': None, 'tags': None, 'context': None, 'hash': None, 'version': '0.0.1.0.1.0', 'metadata': {'author': None, 'editors': None, 'document_type': None, 'compatibility': None, 'creon_dttm': None, 'modon_dttm': None, 'policy': None}, 'data': {'content': None, 'changes': None}}}, 'PyfficeDocumentManager': {'template': {'did': None, 'name': None, 'description': None, 'path': None, 'location': None, 'syntax': None, 'encoding': None, 'tags': None, 'context': None, 'hash': None, 'version': '0.0.1.0.1.0', 'metadata': {'author': None, 'editors': None, 'document_type': None, 'creon_dttm': None, 'modon_dttm': None}, 'data': {'documents': None}}}, 'PyfficeUnit': {'template': {'did': None, 'name': None, 'description': None, 'path': None, 'location': None, 'syntax': None, 'encoding': None, 'tags': None, 'context': None, 'hash': None, 'version': '0.0.1.0.1.0', 'metadata': {'author': None, 'editors': None, 'unit_type': None, 'creon_dttm': None, 'modon_dttm': None}, 'unit': None}}, 'template': {'did': None, 'name': None, 'description': None, 'path': None, 'location': None, 'syntax': None, 'encoding': None, 'tags': None, 'context': None, 'hash': None, 'version': '0.0.1.0.1.0', 'metadata': {'author': None, 'editors': None, 'document_type': None, 'creon_dttm': None, 'modon_dttm': None}, 'data': {'content': {'file_path': None, 'bytes': None, 'full_text': None}, 'pages': {'0': {'entries': {'0': {'did': None, 'unit': {'value': None}}}, 'objects': {'headers': None, 'body': None, 'footers': None}}}}}, 'file_formats': {'word': ['.docx', '.dotx'], 'css': ['.css', '.qss'], 'plaintext': ['.txt', '.log', '.bat'], 'python': ['.py'], 'xml': ['.xml'], 'javascript': ['.js'], 'c': ['.c', '.h', '.cpp', '.hpp'], 'java': ['.java'], 'json': ['.json'], 'yaml': ['.yaml', '.yml'], 'r': ['.r'], 'toml': ['.toml', '.ini', '.cfg', '.conf'], 'markdown': ['.md'], 'bash': ['.sh'], 'html': ['.html'], 'sql': ['.sql']}, 'document': {'data': None, 'data_str': None, 'did': '06a6777c-d0a5-7d6c-8000-a29690d7c566', 'syntax': nan, 'name': 'nchantdscript 7c566', 'position': 6, 'document_type': nan, 'readonly': 0, 'editable': 1, 'visible': 1, 'moveable': 1, 'tid': '06a6777c-d0ea-7c5f-8000-7731f591d8a9', 'pid': '067ca837-17f6-74e7-8000-f7de9b7927f1', 'widget': 'nchantdoffice.widgets.documents.media.scripts.NchantdOfficeScript', 'widgdata': '{"file_type": "script", "google_drive_bit": 1, "local_drive_bit": 1, "import": 0}', 'version': None, 'tab_type': 'add_script_document_nchantdscript', 'location': None, 'encoding': nan, 'tags': nan, 'hash': nan, 'meta_data': {'creon': nan, 'modon': nan}}, 'codex': <pyffice.pyffice.PyfficeCodex object at 0x770eb8a9c7a0>, 'data': None, 'data_str': None, 'did': '06a6777c-d0a5-7d6c-8000-a29690d7c566', 'syntax': nan, 'name': 'nchantdscript 7c566', 'position': 6, 'document_type': nan, 'readonly': 0, 'editable': 1, 'visible': 1, 'moveable': 1, 'tid': '06a6777c-d0ea-7c5f-8000-7731f591d8a9', 'pid': '067ca837-17f6-74e7-8000-f7de9b7927f1', 'widget': 'nchantdoffice.widgets.documents.media.scripts.NchantdOfficeScript', 'widgdata': '{"file_type": "script", "google_drive_bit": 1, "local_drive_bit": 1, "import": 0}', 'version': None, 'tab_type': 'add_script_document_nchantdscript', 'location': None, 'encoding': nan, 'tags': nan, 'hash': nan, 'meta_data': {'creon': nan, 'modon': nan}}
2026-07-27 13:41:59,851 - nchantdoffice.widgets.documents.media.scripts  134: INFO     - [scripts] initModel failed: 'NoneType' object has no attribute 'get'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/scripts.py", line 130, in initModel
    self.document.load_document()
  File "/mnt/iverse/SB/3_Functions/Projects/Pyffice/3_Work/1_DELTA/pyffice/pyffice/script/script.py", line 264, in load_document
    self.set_pages(document.get("data", {}).get("pages", {}))
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'get'
2026-07-27 13:41:59,861 - nchantdoffice.widgets.documents.media.scripts  231: INFO     - Content {}
2026-07-27 13:41:59,861 - nchantdoffice.widgets.documents.media.scripts  256: INFO     - Initialize View
2026-07-27 13:41:59,861 - nchantdoffice.widgets.tabs                 62: INFO     - [tabs] NchantdOfficeTab.initView cfg_provided=True
2026-07-27 13:42:00,374 - nchantdoffice.widgets.documents.documents  365: INFO     - Toolbox Config dict_keys([50, 100, 200, 300, 400])
2026-07-27 13:42:00,381 - nchantdoffice.widgets.documents.media.scripts  258: INFO     - View Initialized
2026-07-27 13:42:00,382 - nchantdoffice.widgets.documents.media.scripts 1121: INFO     - Populating Document
2026-07-27 13:42:00,382 - nchantdoffice.widgets.documents.media.scripts 1159: INFO     - Text: 
2026-07-27 13:42:00,382 - nchantdoffice.widgets.documents.media.scripts 1160: INFO     - Type: <class 'str'>
2026-07-27 13:42:00,382 - nchantdoffice.widgets.documents.media.scripts 1167: INFO     - Document Format: nan
2026-07-27 13:42:00,382 - nchantdoffice.widgets.documents.media.scripts 1168: INFO     - Syntax nan
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/widgets.py", line 149, in on_tab_focus
    #   1) insertTab at an index <= the current index increments Qt's
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 2950, in load_tab
    by ``on_tab_focus`` / ``set_focus`` the first time a tab receives focus.
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 237, in load_tab
    self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab), tabset, tab))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 2986, in load_widget
    logma.info(f"[tabset] open_web_tab requested url={url_str}")
        ^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/scripts.py", line 271, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/scripts.py", line 265, in initView
    self.populate_document()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/scripts.py", line 1275, in populate_document
    raise Exception(f"unknown syntax {self.document.syntax}")
Exception: unknown syntax nan
