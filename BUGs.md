







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




2026-07-31 21:30:11,356 - nchantrs.widgets.widgets                 1038: INFO     - Load Widget Config {'NchantdWidget': {'dstruct': {'database': {'objects': None}}}, 'RegisteredWidgets': {'<(CHART)>': None, '<(CUSTOM)>': "need a method for telling the widget where to read the data from widgetdata:\n  path: group000.label000\n  entry: 'Summary'\n  layer: data #format, formula, data\ngroup000.textbox000\n", '<(DOCEDIT)>': 'nchantrs.widgets.editors.NchantdDocEditor', '<(LABEL)>': 'nchantrs.widgets.annotations.NchantdLabel', '<(SCRATCHEDIT)>': 'nchantrs.widgets.editors.NchantdScratchEditor', '<(TEXTBOX)>': 'nchantrs.widgets.editors.NchantdEntryBox'}, 'expandCFG': {'fonts': {'default': {'font': 'Times', 'size': 12, 'style': 'regular'}}, 'styles': {'default': None}}, 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager': {}, 'tab': {'data': None, 'data_str': None, 'did': '024694d6-f14b-435b-a130-f86a7e4e447f', 'syntax': None, 'name': 'Affiliate Manager', 'position': 2, 'document_type': None, 'readonly': 0, 'editable': 1, 'visible': 1, 'moveable': 1, 'tid': '06a6cee9-0cd1-757a-8000-6b4eb942dba7', 'pid': '066a7cf6-5aca-79a2-8000-f4b5405a0427', 'widget': 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager', 'widgdata': '{}', 'version': None, 'tab_type': 'custom_widget', 'location': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}}, 'file_path': '', 'widget': 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager', 'tid': '06a6cee9-0cd1-757a-8000-6b4eb942dba7', 'document': {'data': None, 'data_str': None, 'did': '024694d6-f14b-435b-a130-f86a7e4e447f', 'syntax': None, 'name': 'Affiliate Manager', 'position': 2, 'document_type': None, 'readonly': 0, 'editable': 1, 'visible': 1, 'moveable': 1, 'tid': '06a6cee9-0cd1-757a-8000-6b4eb942dba7', 'pid': '066a7cf6-5aca-79a2-8000-f4b5405a0427', 'widget': 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager', 'widgdata': '{}', 'version': None, 'tab_type': 'custom_widget', 'location': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}}, 'apps': ['nchantrs', 'nchantdoffice'], 'app': 'nchantdoffice', 'pos': 'center'}
2026-07-31 21:30:11,356 - nchantrs.widgets.widgets                 1044: INFO     - nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager
Master passphrase: 
2026-07-31 21:30:50,122 - pycurity.pykey                            548: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
2026-07-31 21:30:50,124 - pycurity.pykey                            548: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
2026-07-31 21:30:50,124 - pycurity.pykey                            548: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
2026-07-31 21:30:50,125 - pycurity.pykey                            548: INFO     - Connecting to /home/solubrew/.local/share/pycurity/secure_store.db
2026-07-31 21:30:50,125 - nchantdoffice.widgets.config.referral_panel  335: INFO     - [referral_panel] PyKeyStore.get(affiliate_id) failed: 'No key found for service: affiliate_id'
2026-07-31 21:30:50,125 - nchantdoffice.utilities.referral          105: INFO     - ReferralCode created: value='NB-Z5C-1WFD'
2026-07-31 21:30:55,189 - nchantdoffice.utilities.referral          312: WARNING  - [referral_api] GET https://nchantdoffice.com/api/affiliate/earnings failed: HTTPSConnectionPool(host='nchantdoffice.com', port=443): Max retries exceeded with url: /api/affiliate/earnings (Caused by ConnectTimeoutError(<HTTPSConnection(host='nchantdoffice.com', port=443) at 0x7ce700c83980>, 'Connection to nchantdoffice.com timed out. (connect timeout=5.0)'))
2026-07-31 21:30:55,189 - nchantdoffice.widgets.config.referral_panel  447: INFO     - [referral_panel] using local fallback dashboard
2026-07-31 21:30:55,209 - squirl.orgnql.sonql                      2845: WARNING  - SQLT Read Failed due to no such column: position_int using this cmd SELECT [app_action_PK], [code_group_txt], [lookup_code_txt], [name_txt], [description_ltxt], [UUID], [icon_txt], [short_cut_txt], [tip_txt], [advanced_tip_txt], [widget_txt], [parameters_dict] FROM "app_action"  WHERE app_action.code_group_txt = 'base' ORDER BY position_int
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/widgets.py", line 149, in on_tab_focus
    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4093, in load_tab
    super().load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 244, in load_tab
    self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab), tabset, tab))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4129, in load_widget
    tabW.initWidget()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 147, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/config/referral_panel.py", line 95, in initView
    cfg = super().initView()
          ^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 1018, in initView
    super().initView(cfg)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 140, in initView
    self.init_toolbar(cfg)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 449, in init_toolbar
    self.document_toolbar = NchantdButtonBar(self, cfg).initWidget(buttons)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 124, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 90, in initView
    action_cfg = kahndor.Instruct(lookup(self.app, action)).override(self.config)
                                  ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/utilities/utils.py", line 115, in lookup
    raise Exception(f"Action Lookup Config is Empty {cfg}")
Exception: Action Lookup Config is Empty {}
2026-07-31 21:30:55,316 - nchantrs.widgets.widgets                  414: INFO     - Focus Out


n': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}}, 'apps': ['nchantrs', 'nchantdoffice'], 'app': 'nchantdoffice', 'pos': 'center'}
2026-07-31 00:58:08,458 - nchantrs.widgets.widgets                 1044: INFO     - nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager
2026-07-31 00:58:08,468 - nchantdoffice.utilities.referral          105: INFO     - ReferralCode created: value='NB-Z5C-1WFD'
2026-07-31 00:58:13,579 - nchantdoffice.utilities.referral          312: WARNING  - [referral_api] GET https://nchantdoffice.com/api/affiliate/earnings failed: HTTPSConnectionPool(host='nchantdoffice.com', port=443): Max retries exceeded with url: /api/affiliate/earnings (Caused by ConnectTimeoutError(<HTTPSConnection(host='nchantdoffice.com', port=443) at 0x7e0d5b6cdb50>, 'Connection to nchantdoffice.com timed out. (connect timeout=5.0)'))
2026-07-31 00:58:13,580 - nchantdoffice.widgets.config.referral_panel  355: INFO     - [referral_panel] using local fallback dashboard
2026-07-31 00:58:13,604 - squirl.orgnql.conql                       143: INFO     - Cache cleanup completed
2026-07-31 00:58:13,609 - squirl.orgnql.sonql                      2845: WARNING  - SQLT Read Failed due to no such column: position_int using this cmd SELECT [app_action_PK], [code_group_txt], [lookup_code_txt], [name_txt], [description_ltxt], [UUID], [icon_txt], [short_cut_txt], [tip_txt], [advanced_tip_txt], [widget_txt], [parameters_dict] FROM "app_action"  WHERE app_action.code_group_txt = 'base' ORDER BY position_int
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/widgets.py", line 149, in on_tab_focus
    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3867, in load_tab
    super().load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 244, in load_tab
    self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab), tabset, tab))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3903, in load_widget
    tabW.initWidget()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 147, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/config/referral_panel.py", line 95, in initView
    cfg = super().initView()
          ^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 975, in initView
    super().initView(cfg)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 140, in initView
    self.init_toolbar(cfg)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 406, in init_toolbar
    self.document_toolbar = NchantdButtonBar(self, cfg).initWidget(buttons)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 124, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 90, in initView
    action_cfg = kahndor.Instruct(lookup(self.app, action)).override(self.config)
                                  ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/utilities/utils.py", line 115, in lookup
    raise Exception(f"Action Lookup Config is Empty {cfg}")
Exception: Action Lookup Config is Empty {}


2026-07-31 00:35:28,896 - nchantdoffice.widgets.config.settings     211: INFO     - [settings] _initialize_doc_type_selector failed: 'NchantdDropDown' object has no attribute 'currentText'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/config/settings.py", line 207, in _initialize_doc_type_selector
    initial = self.doc_type_selector.currentText() if hasattr(self, "doc_type_selector") else options[0]
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NchantdDropDown' object has no attribute 'currentText'
2026-07-31 00:35:33,094 - nchantrs.widgets.widgets                  414: INFO     - Focus Out




js: The resource https://ground.news/_next/static/chunks/328bfdd80a1e8090.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it has an appropriate `as` value and it is preloaded intentionally.
2026-07-29 00:07:30,989 - nchantdoffice.widgets.documents.managers.calendars  728: INFO     - Calendar unit changed to: 
2026-07-29 00:07:30,989 - nchantdoffice.widgets.documents.managers.calendars  728: INFO     - Calendar unit changed to: 
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/media/editors/selectors.py", line 133, in on_index_change
    self.handler(index, self.itemText(index))
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/managers/calendars.py", line 715, in cmd_on_change_scope
    self.set_scope(scope)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/managers/calendars.py", line 963, in set_scope
    self.calendar = NchantdCalendar(self, cfg).initWidget()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/calendars.py", line 108, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/calendars.py", line 85, in initView
    self.calendar = NchantdMonthCalendar(self, cfg).initWidget()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/months.py", line 114, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/months.py", line 68, in initView
    super().initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/tabsets.py", line 105, in initView
    super().initView(cfg)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 921, in initView
    super().initView(cfg)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 206, in initView
    self.initialize_context_menu()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 216, in initialize_context_menu
    menu_name = self.context_menu_name
                ^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NchantdMonthCalendar' object has no attribute 'context_menu_name'





js: The resource https://ground.news/_next/static/chunks/328bfdd80a1e8090.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it has an appropriate `as` value and it is preloaded intentionally.
2026-07-29 00:07:09,748 - nchantrs.widgets.tables.tables            578: INFO     - Size 640 480
2026-07-29 00:07:09,749 - nchantrs.widgets.tables.tables            580: INFO     - Size [58, 160]
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/media/editors/selectors.py", line 133, in on_index_change
    self.handler(index, self.itemText(index))
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/managers/calendars.py", line 715, in cmd_on_change_scope
    self.set_scope(scope)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/managers/calendars.py", line 963, in set_scope
    self.calendar = NchantdCalendar(self, cfg).initWidget()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/calendars.py", line 108, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/calendars.py", line 91, in initView
    self.calendar = NchantdYearCalendar(self, cfg).initWidget()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 105, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 89, in initView
    self.month_tables[i] = NchantdGrid(self, cfg).initWidget()
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 604, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 592, in initView
    grid_layout.addWidget(cell, row, col)
TypeError: 'PySide6.QtWidgets.QGridLayout.addWidget' called with wrong argument types:
  PySide6.QtWidgets.QGridLayout.addWidget(NchantdCell, int, int)
Supported signatures:
  PySide6.QtWidgets.QGridLayout.addWidget(w: PySide6.QtWidgets.QWidget, /)
  PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row: int, column: int, /, alignment: PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))
  PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row: int, column: int, rowSpan: int, columnSpan: int, /, alignment: PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))



', 'MIT'], ['email_validator', '2.2.0', 'The Unlicense (Unlicense)']
2026-07-28 23:56:12,370 - nchantrs.widgets.tables.tables            298: INFO     - Num Columns 40
2026-07-28 23:56:12,370 - nchantrs.widgets.tables.tables            300: INFO     - Columns None
2026-07-28 23:56:12,370 - nchantrs.widgets.tables.tables            131: WARNING  - calc roman numerals
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/workbooks/matricies.py", line 1701, in on_cell_changed
    address = f"{chr(65 + item.column())}{item.row() + 1}"
                          ^^^^^^^^^^^^^
TypeError: 'NoneType' object is not callable
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/workbooks/matricies.py", line 1701, in on_cell_changed
    address = f"{chr(65 + item.column())}{item.row() + 1}"
                          ^^^^^^^^^^^^^
TypeError: 'NoneType' object is not callable
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/workbooks/matricies.py", line 1701, in on_cell_changed
    address = f"{chr(65 + item.column())}{item.row() + 1}"
                          ^^^^^^^^^^^^^




ne}}, 'file_path': '', 'widget': 'nchantrs.widgets.calendars.years.NchantdYearCalendar', 'tid': '06a69701-b37d-7970-8000-debb2606a30e', 'document': {'data': None, 'data_str': None, 'did': '06a69701-b37d-77c7-8000-f0e6de3282a4', 'syntax': None, 'name': '2026', 'position': 0, 'document_type': None, 'readonly': 0, 'editable': 1, 'visible': 1, 'moveable': 1, 'tid': '06a69701-b37d-7970-8000-debb2606a30e', 'pid': '06a69701-b343-732f-8000-93abb6533a35', 'widget': 'nchantrs.widgets.calendars.years.NchantdYearCalendar', 'widgdata': '{}', 'version': None, 'tab_type': 'year', 'location': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}}, 'apps': ['nchantrs', 'nchantdoffice'], 'app': 'nchantdoffice', 'pos': 'center'}
2026-07-28 23:20:00,931 - nchantrs.widgets.widgets                 1034: INFO     - nchantrs.widgets.calendars.years.NchantdYearCalendar
2026-07-28 23:20:00,938 - nchantrs.widgets.tables.tables            578: INFO     - Size 640 480
2026-07-28 23:20:00,938 - nchantrs.widgets.tables.tables            580: INFO     - Size [58, 160]
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/views/treeviews.py", line 193, in onLeftClick
    self.set_current_node(signal)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/views/treeviews.py", line 275, in set_current_node
    node.updateTabs("center")
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/items/nodes.py", line 551, in updateTabs
    self.app.view.panes[view].model.buildTabSet(self, view)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3133, in buildTabSet
    self.load_tab_set(tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3230, in load_tab_set
    self.load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3344, in load_tab
    super().load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 237, in load_tab
    self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab), tabset, tab))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3380, in load_widget
    tabW.initWidget()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 105, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 89, in initView
    self.month_tables[i] = NchantdGrid(self, cfg).initWidget()
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 604, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 592, in initView
    grid_layout.addWidget(cell, row, col)
TypeError: 'PySide6.QtWidgets.QGridLayout.addWidget' called with wrong argument types:
  PySide6.QtWidgets.QGridLayout.addWidget(NchantdCell, int, int)
Supported signatures:
  PySide6.QtWidgets.QGridLayout.addWidget(w: PySide6.QtWidgets.QWidget, /)
  PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row: int, column: int, /, alignment: PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))
  PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row: int, column: int, rowSpan: int, columnSpan: int, /, alignment: PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/views/treeviews.py", line 195, in onLeftClick
    self.set_current_node(signal)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/views/treeviews.py", line 275, in set_current_node
    node.updateTabs("center")
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/items/nodes.py", line 551, in updateTabs
    self.app.view.panes[view].model.buildTabSet(self, view)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3133, in buildTabSet
    self.load_tab_set(tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3230, in load_tab_set
    self.load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3344, in load_tab
    super().load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 237, in load_tab
    self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab), tabset, tab))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3380, in load_widget
    tabW.initWidget()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 105, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 89, in initView
    self.month_tables[i] = NchantdGrid(self, cfg).initWidget()
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 604, in initWidget
    self.initView()
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 592, in initView
    grid_layout.addWidget(cell, row, col)
TypeError: 'PySide6.QtWidgets.QGridLayout.addWidget' called with wrong argument types:
  PySide6.QtWidgets.QGridLayout.addWidget(NchantdCell, int, int)
Supported signatures:
  PySide6.QtWidgets.QGridLayout.addWidget(w: PySide6.QtWidgets.QWidget, /)
  PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row: int, column: int, /, alignment: PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))
  PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row: int, column: int, rowSpan: int, columnSpan: int, /, alignment: PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))







2026-07-28 23:19:14,162 - nchantrs.widgets.widgets                 1028: INFO     - Load Widget Config {'NchantdWidget': {'dstruct': {'database': {'objects': None}}}, 'RegisteredWidgets': {'<(CHART)>': None, '<(CUSTOM)>': "need a method for telling the widget where to read the data from widgetdata:\n  path: group000.label000\n  entry: 'Summary'\n  layer: data #format, formula, data\ngroup000.textbox000\n", '<(DOCEDIT)>': 'nchantrs.widgets.editors.NchantdDocEditor', '<(LABEL)>': 'nchantrs.widgets.annotations.NchantdLabel', '<(SCRATCHEDIT)>': 'nchantrs.widgets.editors.NchantdScratchEditor', '<(TEXTBOX)>': 'nchantrs.widgets.editors.NchantdEntryBox'}, 'expandCFG': {'fonts': {'default': {'font': 'Times', 'size': 12, 'style': 'regular'}}, 'styles': {'default': None}}, 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager': {}, 'tab': {'data': None, 'data_str': None, 'did': '024694d6-f14b-435b-a130-f86a7e4e447f', 'syntax': None, 'name': 'Affiliate Manager', 'position': 2, 'document_type': None, 'readonly': 0, 'editable': 1, 'visible': 1, 'moveable': 1, 'tid': '06a69701-b24f-78a4-8000-076ddb717b53', 'pid': '066a7cf6-5aca-79a2-8000-f4b5405a0427', 'widget': 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager', 'widgdata': '{}', 'version': None, 'tab_type': 'custom_widget', 'location': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}}, 'file_path': '', 'widget': 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager', 'tid': '06a69701-b24f-78a4-8000-076ddb717b53', 'document': {'data': None, 'data_str': None, 'did': '024694d6-f14b-435b-a130-f86a7e4e447f', 'syntax': None, 'name': 'Affiliate Manager', 'position': 2, 'document_type': None, 'readonly': 0, 'editable': 1, 'visible': 1, 'moveable': 1, 'tid': '06a69701-b24f-78a4-8000-076ddb717b53', 'pid': '066a7cf6-5aca-79a2-8000-f4b5405a0427', 'widget': 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager', 'widgdata': '{}', 'version': None, 'tab_type': 'custom_widget', 'location': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}}, 'apps': ['nchantrs', 'nchantdoffice'], 'app': 'nchantdoffice', 'pos': 'center'}
2026-07-28 23:19:14,162 - nchantrs.widgets.widgets                 1034: INFO     - nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/widgets.py", line 149, in on_tab_focus
    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3344, in load_tab
    super().load_tab(tab, tabn, tabset, active_tab_position)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 237, in load_tab
    self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab), tabset, tab))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3380, in load_widget
    tabW.initWidget()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/documents.py", line 142, in initWidget
    self.initModel()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/config/referral_panel.py", line 82, in initModel
    self._load_or_generate_code()
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/config/referral_panel.py", line 310, in _load_or_generate_code
    getattr(self.user, "id", None)
            ^^^^^^^^^
AttributeError: 'NchantdOfficeReferralPanel' object has no attribute 'user'



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



## Status (2026-07-29)

The 5 errors recorded above (H52/H53/H55 sprint) were fixed in the
commits documented in `TODOs.md` under "H53–H55 sprint — sketch /
matrix regression + score lifts". All historical traces above are
preserved for audit reference.

Sprint 1 + Sprint 2 (2026-07-28) closed the remaining live `TODOs.md`
bugs and shipped defensive fixes. See
`TODOs.md → Sprint 1 + Sprint 2 (2026-07-28) — persistence + safety
pass` for the full commit list and the post-sprint test surface
(`45 passed, 2 skipped` as of 2026-07-29).

Eight additional crashes (timestamped 2026-07-28 23:18 → 2026-07-29
00:07) are catalogued as `T-NEW-015` through `T-NEW-022` in `TODOs.md →
## NEW TODOs → Live crashes newly surfaced in BUGs.md`. Each carries
the failing call site and the `BUGs.md` line reference. The full
list:

| ID | File:Line | Error |
|---|---|---|
| T-NEW-015 | `nchantrs.widgets.calendars.months.py:114` | Calendar `context_menu_name` AttributeError |
| T-NEW-016 | `nchantrs.widgets.tables.tables.py:592` | Calendar `QGridLayout.addWidget(NchantdCell, ...)` TypeError |
| T-NEW-017 | `nchantdoffice/widgets/documents/workbooks/matricies.py:1701` | Matrix `chr(None)` TypeError |
| T-NEW-018 | `matricies.py:1713` | Matrix `cell_ref_label` AttributeError |
| T-NEW-019 | `nchantdoffice/widgets/config/referral_panel.py:310` | ReferralPanel `self.user` AttributeError |
| T-NEW-020 | `pdfs.py:157` | PDF help `KeyError: 'document'` |
| T-NEW-021 | `nchantrs/models/tabsetmodels.py:238` | PDF help tab focus `tab_widgets[tabn]` IndexError |
| T-NEW-022 | `nchantdoffice/widgets/documents/atnrg/browsers.py:348` | Browser `store_link(tag=...)` TypeError |

No new error traces were added during Sprint 5 or Sprint 7 because
those sprints were scoped to preventive coverage (Sprint 5: `.pyof`
pickle removal + content-only logging) and import-safety lint fixes
(Sprint 7: F821 cleanup) rather than crash-log capture.