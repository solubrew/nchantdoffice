2026-07-27 14:09:44,544 - nchantdoffice.widgets.documents.media.scripts  134: INFO     - [scripts] initModel failed: 'NoneType' object has no attribute 'get'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/scripts.py", line 130, in initModel
    self.document.load_document()
  File "/mnt/iverse/SB/3_Functions/Projects/Pyffice/3_Work/1_DELTA/pyffice/pyffice/script/script.py", line 264, in load_document
    self.set_pages(document.get("data", {}).get("pages", {}))
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'get'
2026-07-27 14:09:44,565 - nchantdoffice.widgets.documents.media.scripts  229: INFO     - Content {}
2026-07-27 14:09:44,565 - nchantdoffice.widgets.documents.media.scripts  254: INFO     - Initialize View
2026-07-27 14:09:44,565 - nchantdoffice.widgets.tabs                 62: INFO     - [tabs] NchantdOfficeTab.i