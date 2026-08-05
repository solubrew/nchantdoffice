# TODAY is 2026-08-03:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.

## Issues Found:
- NchantdLabeledCheckbox is collapsing the displayed label to only show the center of the text.
- make a passphrase popup field instead of triggering the getpass cli logic
    2026-08-04 11:43:30,107 - pyffice.document                         1338: INFO     - 
    [PyfficeDocument] File Path None
    Master passphrase: 
    2026-08-04 11:43:56,254 - pycurity.pykey                            548: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
    2026-08-04 11:43:56,257 - pycurity.pykey                            548: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
    2026-08-04 11:43:56,258 - pycurity.pykey                            548: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
    2026-08-04 11:43:56,260 - pycurity.pykey                            548: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
    2026-08-04 11:43:56,261 - nchantdoffice.widgets.config.referral_panel  347: INFO     - [referral_panel] PyKeyStore.get(affiliate_id) failed: 'No key found for service: affiliate_id'
    2026-08-04 11:43:56,261 - nchantdoffice.utilities.referral          105: INFO     - ReferralCode created: value='NB-Z5C-1WFD'
- Need to implement NchantdOfficePalette document into the NchantdOfficeImage document toolbar should launch the palette toolbox drawer where the palette document is displayed with a list of colors and percentage usage in the image

## Bugs:


2026-08-04 11:44:01,329 - nchantdoffice.widgets.tabs                 62: INFO     - [tabs] NchantdOfficeTab.initView cfg_provided=True
2026-08-04 11:44:01,343 - squirl.orgnql.sonql                      2887: WARNING  - SQLT Read Failed due to no such column: position_int using this cmd SELECT [app_action_PK], [code_group_txt], [lookup_code_txt], [name_txt], [description_ltxt], [UUID], [icon_txt], [short_cut_txt], [tip_txt], [advanced_tip_txt], [widget_txt], [parameters_dict] FROM "app_action"  WHERE app_action.code_group_txt = 'base' ORDER BY position_int
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/widgets.py", line 149, in on_tab_focus
    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4050, in load_tab
    super().load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 166, in load_tab
    self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab), tabset, tab))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4086, in load_widget
    tabW.initWidget()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 859, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/config/referral_panel.py", line 109, in initView
    super().initView(cfg)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 843, in initView
    super().initView(cfg)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 140, in initView
    self.init_toolbar(cfg)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 915, in init_toolbar
    super().init_toolbar(cfg)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 448, in init_toolbar
    self.document_toolbar = NchantdButtonBar(self, cfg).initWidget(buttons)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 98, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 65, in initView
    action_cfg = kahndor.Instruct(lookup(self.app, action)).override(self.config)
                                  ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/utilities/utils.py", line 96, in lookup
    raise Exception(f'Action {action} Lookup Config is Empty {cfg}')
Exception: Action show_pane_left Lookup Config is Empty {}



