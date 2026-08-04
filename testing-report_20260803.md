# TODAY is 2026-08-03:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.


## Issues Found:
    - NchantdOfficeCalculator still doesn't pickup input from number pad or number row....buttons only respond to clicks
    - browser still not saving and restoring url traversal history
    - new node button on nchantdofficedocumenttoolbar should default to a popup that asks the user to input a name for the node
    - new tab button on nchantdofficedocumenttoolbar should default to a popup that asks the user to input a name for the tab
    - NchantdOfficeDocumentCatalog bottom pane is disapearing after a tab is created from using the accept button in the pane
    - NchantdOfficeImage doesn't respect Application slider between the center and rightside panes in the main app once the image has been sized it will force the right side to a small size and can't be moved back to the left
        - after it is tripped teh right side stays narrow for all documents need to control the right side pane size

## Bugs:



2026-08-03 17:57:46,400 - nchantrs.widgets.widgets                  484: INFO     - Left Click <PySide6.QtGui.QMouseEvent(MouseButtonPress LeftButton pos=497,561 scn=803,561 gbl=2723,619 dev=QInputDevice(QPointingDevice("Virtual core pointer" Mouse id=2 seat=30002 caps=Position|Scroll|Hover buttonCount=32))>
2026-08-03 17:57:46,400 - nchantrs.widgets.widgets                  485: INFO     - Left Click
2026-08-03 17:57:48,171 - nchantrs.widgets.widgets                  430: INFO     - Focus In
2026-08-03 17:57:48,171 - nchantrs.widgets.widgets                  465: INFO     - Mouse Press Event
2026-08-03 17:57:48,171 - nchantrs.widgets.widgets                  484: INFO     - Left Click <PySide6.QtGui.QMouseEvent(MouseButtonPress LeftButton pos=32,15 scn=1511,906 gbl=3431,964 dev=QInputDevice(QPointingDevice("Virtual core pointer" Mouse id=2 seat=30002 caps=Position|Scroll|Hover buttonCount=32))>
2026-08-03 17:57:48,171 - nchantrs.widgets.widgets                  485: INFO     - Left Click
2026-08-03 17:57:48,284 - nchantrs.widgets.widgets                  435: INFO     - Focus Out
2026-08-03 17:57:48,284 - nchantrs.widgets.widgets                  430: INFO     - Focus In
2026-08-03 17:57:48,289 - nchantdoffice.models                     3165: INFO     - Get View Link json_pub None None None None
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/buttons.py", line 159, in <lambda>
    self.clicked.connect(lambda checked: self.on_click(checked, handler, params))
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/buttons.py", line 151, in on_click
    handler(signal, params)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/panes/new.py", line 84, in accept
    super().accept()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/panes/catalogs.py", line 116, in accept
    self.add_feature('center')
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/panes/new.py", line 119, in add_document
    content["unit"]["original_path"] = self.app.model.get_link(code)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 1616, in get_link
    link = self.store.get_view_link(name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3166, in get_view_link
    df = self.get_links(name, description, type_, tag, url, db)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/models.py", line 546, in get_links
    cfg = self._build_filter_config([('EQUAL', 'name_txt', name), ('LIKE', 'description_ltxt', description), ('EQUAL', 'type_txt', type_), ('EQUAL', 'tag_txt', tag), ('LIKE', 'url_ltxt', url)])
          ^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NchantdOfficeStore' object has no attribute '_build_filter_config'. Did you mean: '_build_tag_config'?
2026-08-03 17:57:50,878 - nchantrs.widgets.widgets                  430: INFO     - Focus In
