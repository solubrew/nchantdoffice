# TODAY is 2026-08-03:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.


## Issues Found:



## Bugs:
ore pointer" Mouse id=2 seat=30002 caps=Position|Scroll|Hover buttonCount=32))>
2026-08-10 16:26:52,727 - nchantrs.widgets.widgets                  549: INFO     - Left Click
2026-08-10 16:26:52,832 - nchantdoffice.widgets.documents.media.images  930: INFO     - [images] cmd_run_palette_scan failed: 'PyfficeColorPalette' object has no attribute 'extract_palette'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/images.py", line 927, in cmd_run_palette_scan
    palette = PyfficeColorPalette(cfg).extract_palette(path)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'PyfficeColorPalette' object has no attribute 'extract_palette'
2026-08-10 16:26:54,559 - nchantrs.widgets.widgets                  499: INFO     - Focus Out
2026-08-10 16:26:54,559 - nchantrs.widgets.widgets                  494: INFO     - Focus In
2026-08-10 16:26:54,560 - nchantrs.widgets.widgets                  529: INFO     - Mouse Press Event
2026-08-10 16:26:54,560 - nchantrs.widgets.widgets                  548: INFO     - Left Click <PySide6.QtGui.QMouseEvent(MouseButtonPress LeftButton pos=18,8 scn=479,15 gbl=2399,73 dev=QInputDevice(QPointingDevice("Virtual core pointer" Mouse id=2 seat=30002 caps=Position|Scroll|Hover buttonCount=32))>
2026-08-10 16:26:54,560 - nchantrs.widgets.widgets                  549: INFO     - Left Click
2026-08-10 16:26:54,696 - nchantdoffice.widgets.documents.media.images  930: INFO     - [images] cmd_run_palette_scan failed: 'PyfficeColorPalette' object has no attribute 'extract_palette'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/images.py", line 927, in cmd_run_palette_scan
    palette = PyfficeColorPalette(cfg).extract_palette(path)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'PyfficeColorPalette' object has no attribute 'extract_palette'