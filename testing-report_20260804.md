# TODAY is 2026-08-03:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.

## Issues Found:
- journal still not reloading content
- 


- FIXED - NchantdLabeledCheckbox is collapsing the displayed label to only show the center of the text.
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
    
    - popup for master passphrase works but the Affiliate tab breaks 

    2026-08-04 18:16:07,944 - pycurity.pykey                            587: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
    2026-08-04 18:16:07,945 - nchantdoffice.widgets.config.referral_panel  357: INFO     - [referral_panel] PyKeyStore.get(affiliate_id) failed: 'No key found for service: affiliate_id'
    2026-08-04 18:16:07,945 - nchantdoffice.utilities.referral          105: INFO     - ReferralCode created: value='NB-Z5C-1WFD'
    2026-08-04 18:16:12,988 - nchantdoffice.utilities.referral          312: WARNING  - [referral_api] GET https://nchantdoffice.com/api/affiliate/earnings failed: HTTPSConnectionPool(host='nchantdoffice.com', port=443): Max retries exceeded with url: /api/affiliate/earnings (Caused by ConnectTimeoutError(<HTTPSConnection(host='nchantdoffice.com', port=443) at 0x7205701d74a0>, 'Connection to nchantdoffice.com timed out. (connect timeout=5.0)'))
    2026-08-04 18:16:12,988 - nchantdoffice.widgets.config.referral_panel  488: INFO     - [referral_panel] using local fallback dashboard
    2026-08-04 18:16:12,988 - nchantdoffice.widgets.tabs                 62: INFO     - [tabs] NchantdOfficeTab.initView cfg_provided=True
    2026-08-04 18:16:13,282 - nchantdoffice.widgets.documents.documents  460: INFO     - Toolbox Config dict_keys([50])
    2026-08-04 18:16:13,282 - nchantdoffice.widgets.documents.documents  552: INFO     - Save Content type=dict keys=['file_path', 'location', 'internal']
    2026-08-04 18:16:13,282 - nchantdoffice.widgets.documents.documents  556: INFO     - Save Path None
    2026-08-04 18:16:13,282 - nchantdoffice.widgets.documents.documents  568: INFO     - Save PID 066a7cf6-5aca-79a2-8000-f4b5405a0427
    2026-08-04 18:16:13,282 - nchantdoffice.widgets.documents.documents  572: INFO     - Save Pos 0
    2026-08-04 18:16:13,282 - nchantdoffice.widgets.documents.documents  573: INFO     - Save DID 06a7264a-069e-7582-8000-db6d6b37fa2e
    2026-08-04 18:16:13,282 - pyffice.document                          346: INFO     - Increment Version 0
    2026-08-04 18:16:13,282 - pyffice.config.config                      98: WARNING  - PyfficeConfig.save: no path available
    2026-08-04 18:16:13,283 - nchantdoffice.models                     2672: INFO     - PAYLOAD {'did': '06a7264a-069e-7582-8000-db6d6b37fa2e', 'meta_data': {'schema_version': [1, 0, 0]}, 'data': {'content': {'config': <kahndor.kahndor.Instruct object at 0x72053e9e7a60>}, 'document_type': 'slide', 'path': None, 'schema_version': [1, 0, 0]}, 'pyffice_compat': {'normalizer': 'additive-canonical', 'package': '0.1.0', 'schema_version': [1, 0, 0]}}
    2026-08-04 18:16:13,283 - squirl.squirl                             421: INFO     - Writing data to db
    2026-08-04 18:16:13,284 - nchantdoffice.models                      441: INFO     - document {'did': '06a7264a-069e-7582-8000-db6d6b37fa2e', 'meta_data': {'schema_version': [1, 0, 0]}, 'data': {'content': {'config': <kahndor.kahndor.Instruct object at 0x72053e9e7a60>}, 'document_type': 'slide', 'path': None, 'schema_version': [1, 0, 0]}, 'pyffice_compat': {'normalizer': 'additive-canonical', 'package': '0.1.0', 'schema_version': [1, 0, 0]}}
    2026-08-04 18:16:13,284 - nchantdoffice.models                      442: INFO     - document type <class 'dict'>
    2026-08-04 18:16:13,284 - nchantdoffice.models                      447: INFO     - Content {'content': {'config': <kahndor.kahndor.Instruct object at 0x72053e9e7a60>}, 'document_type': 'slide', 'path': None, 'schema_version': [1, 0, 0]}
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
      File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 854, in initWidget
        self.initView()
      File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/config/referral_panel.py", line 109, in initView
        super().initView(cfg)
      File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 843, in initView
        self.populate_data()
      File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 991, in populate_data
        self.save()
      File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 1006, in save
        super().save()
      File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 605, in save
        self.app.model.store_document(self.document)
      File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 2677, in store_document
        self.add_document_content(doc_payload, version=pydoc.version)
      File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 448, in add_document_content
        logma.info(f"Dumped Content {j.dumps(content)}")
                                     ^^^^^^^^^^^^^^^^
      File "/usr/lib/python3.12/json/__init__.py", line 231, in dumps
        return _default_encoder.encode(obj)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/lib/python3.12/json/encoder.py", line 200, in encode
        chunks = self.iterencode(o, _one_shot=True)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/lib/python3.12/json/encoder.py", line 258, in iterencode
        return _iterencode(o, 0)
               ^^^^^^^^^^^^^^^^^
      File "/usr/lib/python3.12/json/encoder.py", line 180, in default
        raise TypeError(f'Object of type {o.__class__.__name__} '
    TypeError: Object of type Instruct is not JSON serializable
    2026-08-04 18:16:13,403 - nchantrs.widgets.widgets                  435: INFO     - Focus Out




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



