2026-07-31 21:30:11,356 - nchantrs.widgets.widgets                 1038: INFO  
  \- Load Widget Config {'NchantdWidget': {'dstruct': {'database': {'objects':
None}}}, 'RegisteredWidgets': {'<(CHART)>': None, '<(CUSTOM)>': "need a method
for telling the widget where to read the data from widgetdata:\\n  path:
group000.label000\\n  entry: 'Summary'\\n  layer: data #format, formula,
data\\ngroup000.textbox000\\n", '<(DOCEDIT)>':
'nchantrs.widgets.editors.NchantdDocEditor', '<(LABEL)>':
'nchantrs.widgets.annotations.NchantdLabel', '<(SCRATCHEDIT)>':
'nchantrs.widgets.editors.NchantdScratchEditor', '<(TEXTBOX)>':
'nchantrs.widgets.editors.NchantdEntryBox'}, 'expandCFG': {'fonts': {'default':
{'font': 'Times', 'size': 12, 'style': 'regular'}}, 'styles': {'default':
None}}, 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager':
{}, 'tab': {'data': None, 'data_str': None, 'did':
'024694d6-f14b-435b-a130-f86a7e4e447f', 'syntax': None, 'name': 'Affiliate
Manager', 'position': 2, 'document_type': None, 'readonly': 0, 'editable': 1,
'visible': 1, 'moveable': 1, 'tid': '06a6cee9-0cd1-757a-8000-6b4eb942dba7',
'pid': '066a7cf6-5aca-79a2-8000-f4b5405a0427', 'widget':
'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager',
'widgdata': '{}', 'version': None, 'tab_type': 'custom_widget', 'location':
None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon':
None, 'modon': None}}, 'file_path': '', 'widget':
'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager', 'tid':
'06a6cee9-0cd1-757a-8000-6b4eb942dba7', 'document': {'data': None, 'data_str':
None, 'did': '024694d6-f14b-435b-a130-f86a7e4e447f', 'syntax': None, 'name':
'Affiliate Manager', 'position': 2, 'document_type': None, 'readonly': 0,
'editable': 1, 'visible': 1, 'moveable': 1, 'tid':
'06a6cee9-0cd1-757a-8000-6b4eb942dba7', 'pid':
'066a7cf6-5aca-79a2-8000-f4b5405a0427', 'widget':
'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager',
'widgdata': '{}', 'version': None, 'tab_type': 'custom_widget', 'location':
None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon':
None, 'modon': None}}, 'apps': ['nchantrs', 'nchantdoffice'], 'app':
'nchantdoffice', 'pos': 'center'} 2026-07-31 21:30:11,356 -
nchantrs.widgets.widgets                 1044: INFO     -
nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager Master
passphrase: 2026-07-31 21:30:50,122 - pycurity.pykey                           
548: INFO     - Connecting to
/home/solubrew/.local/share/pycurity/secure_store.db 2026-07-31 21:30:50,124 -
pycurity.pykey                            548: INFO     - Connecting to
/home/solubrew/.local/share/pycurity/secure_store.db 2026-07-31 21:30:50,124 -
pycurity.pykey                            548: INFO     - Connecting to
/home/solubrew/.local/share/pycurity/secure_store.db 2026-07-31 21:30:50,125 -
pycurity.pykey                            548: INFO     - Connecting to
/home/solubrew/.local/share/pycurity/secure_store.db 2026-07-31 21:30:50,125 -
nchantdoffice.widgets.config.referral_panel  335: INFO     - \[referral_panel]
PyKeyStore.get(affiliate_id) failed: 'No key found for service: affiliate_id'
2026-07-31 21:30:50,125 - nchantdoffice.utilities.referral          105: INFO  
  \- ReferralCode created: value='NB-Z5C-1WFD' 2026-07-31 21:30:55,189 -
nchantdoffice.utilities.referral          312: WARNING  - \[referral_api] GET 
<https://nchantdoffice.com/api/affiliate/earnings> failed:
HTTPSConnectionPool(host='nchantdoffice.com', port=443): Max retries exceeded
with url: /api/affiliate/earnings (Caused by
ConnectTimeoutError(\<HTTPSConnection(host='nchantdoffice.com', port=443) at
0x7ce700c83980>, 'Connection to nchantdoffice.com timed out. (connect
timeout=5.0)')) 2026-07-31 21:30:55,189 -
nchantdoffice.widgets.config.referral_panel  447: INFO     - \[referral_panel]
using local fallback dashboard 2026-07-31 21:30:55,209 - squirl.orgnql.sonql   
                  2845: WARNING  - SQLT Read Failed due to no such column:
position_int using this cmd SELECT \[app_action_PK], \[code_group_txt],
\[lookup_code_txt], \[name_txt], \[description_ltxt], \[UUID], \[icon_txt],
\[short_cut_txt], \[tip_txt], \[advanced_tip_txt], \[widget_txt],
\[parameters_dict] FROM "app_action"  WHERE app_action.code_group_txt = 'base'
ORDER BY position_int Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/widgets.py", line 149, in on_tab_focus
self.model.load_tab(self.model.tabsdata\[tabn], tabn, self.pane_position) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 4093, in load_tab super().load_tab(tab, tabn,
tabset, active_tab_position) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 244, in load_tab
self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab),
tabset, tab)) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 4129, in load_widget tabW.initWidget() File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 147, in initWidget
self.initView() File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/config/referral_panel.py", line 95, in initView cfg =
super().initView() ^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 1018, in initView
super().initView(cfg) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 140, in initView
self.init_toolbar(cfg) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 449, in init_toolbar
self.document_toolbar = NchantdButtonBar(self, cfg).initWidget(buttons)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 124, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 90, in
initView action_cfg = kahndor.Instruct(lookup(self.app,
action)).override(self.config) ^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/utilities/utils.py", line 115, in lookup raise
Exception(f"Action Lookup Config is Empty {cfg}") Exception: Action Lookup
Config is Empty {} 2026-07-31 21:30:55,316 - nchantrs.widgets.widgets          
       414: INFO     - Focus Out

n': None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon':
None, 'modon': None}}, 'apps': ['nchantrs', 'nchantdoffice'], 'app':
'nchantdoffice', 'pos': 'center'} 2026-07-31 00:58:08,458 -
nchantrs.widgets.widgets                 1044: INFO     -
nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager 2026-07-31
00:58:08,468 - nchantdoffice.utilities.referral          105: INFO     -
ReferralCode created: value='NB-Z5C-1WFD' 2026-07-31 00:58:13,579 -
nchantdoffice.utilities.referral          312: WARNING  - \[referral_api] GET 
<https://nchantdoffice.com/api/affiliate/earnings> failed:
HTTPSConnectionPool(host='nchantdoffice.com', port=443): Max retries exceeded
with url: /api/affiliate/earnings (Caused by
ConnectTimeoutError(\<HTTPSConnection(host='nchantdoffice.com', port=443) at
0x7e0d5b6cdb50>, 'Connection to nchantdoffice.com timed out. (connect
timeout=5.0)')) 2026-07-31 00:58:13,580 -
nchantdoffice.widgets.config.referral_panel  355: INFO     - \[referral_panel]
using local fallback dashboard 2026-07-31 00:58:13,604 - squirl.orgnql.conql   
                   143: INFO     - Cache cleanup completed 2026-07-31
00:58:13,609 - squirl.orgnql.sonql                      2845: WARNING  - SQLT
Read Failed due to no such column: position_int using this cmd SELECT
\[app_action_PK], \[code_group_txt], \[lookup_code_txt], \[name_txt],
\[description_ltxt], \[UUID], \[icon_txt], \[short_cut_txt], \[tip_txt],
\[advanced_tip_txt], \[widget_txt], \[parameters_dict] FROM "app_action"  WHERE
app_action.code_group_txt = 'base' ORDER BY position_int Traceback (most recent
call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/widgets.py", line 149, in on_tab_focus
self.model.load_tab(self.model.tabsdata\[tabn], tabn, self.pane_position) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3867, in load_tab super().load_tab(tab, tabn,
tabset, active_tab_position) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 244, in load_tab
self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab),
tabset, tab)) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3903, in load_widget tabW.initWidget() File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 147, in initWidget
self.initView() File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/config/referral_panel.py", line 95, in initView cfg =
super().initView() ^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 975, in initView
super().initView(cfg) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 140, in initView
self.init_toolbar(cfg) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 406, in init_toolbar
self.document_toolbar = NchantdButtonBar(self, cfg).initWidget(buttons)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 124, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/controls/toolbars.py", line 90, in
initView action_cfg = kahndor.Instruct(lookup(self.app,
action)).override(self.config) ^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/utilities/utils.py", line 115, in lookup raise
Exception(f"Action Lookup Config is Empty {cfg}") Exception: Action Lookup
Config is Empty {}

2026-07-31 00:35:28,896 - nchantdoffice.widgets.config.settings     211: INFO  
  \- \[settings] _initialize_doc_type_selector failed: 'NchantdDropDown' object
has no attribute 'currentText' Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/config/settings.py", line 207, in
_initialize_doc_type_selector initial = self.doc_type_selector.currentText() if
hasattr(self, "doc_type_selector") else options\[0]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ AttributeError: 'NchantdDropDown' object has
no attribute 'currentText' 2026-07-31 00:35:33,094 - nchantrs.widgets.widgets  
               414: INFO     - Focus Out

js: The resource https://ground.news/_next/static/chunks/328bfdd80a1e8090.js
was preloaded using link preload but not used within a few seconds from the
window's load event. Please make sure it has an appropriate `as` value and it is
preloaded intentionally. 2026-07-29 00:07:30,989 -
nchantdoffice.widgets.documents.managers.calendars  728: INFO     - Calendar
unit changed to: 2026-07-29 00:07:30,989 -
nchantdoffice.widgets.documents.managers.calendars  728: INFO     - Calendar
unit changed to: Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/media/editors/selectors.py", line 133,
in on_index_change self.handler(index, self.itemText(index)) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/managers/calendars.py", line 715, in
cmd_on_change_scope self.set_scope(scope) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/managers/calendars.py", line 963, in set_scope
self.calendar = NchantdCalendar(self, cfg).initWidget()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/calendars.py", line 108, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/calendars.py", line 85, in
initView self.calendar = NchantdMonthCalendar(self, cfg).initWidget()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/months.py", line 114, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/months.py", line 68, in
initView super().initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/tabsets.py", line 105, in initView
super().initView(cfg) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 921, in initView
super().initView(cfg) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 206, in initView
self.initialize_context_menu() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 216, in
initialize_context_menu menu_name = self.context_menu_name
^^^^^^^^^^^^^^^^^^^^^^ AttributeError: 'NchantdMonthCalendar' object has no
attribute 'context_menu_name'

js: The resource https://ground.news/_next/static/chunks/328bfdd80a1e8090.js
was preloaded using link preload but not used within a few seconds from the
window's load event. Please make sure it has an appropriate `as` value and it is
preloaded intentionally. 2026-07-29 00:07:09,748 -
nchantrs.widgets.tables.tables            578: INFO     - Size 640 480
2026-07-29 00:07:09,749 - nchantrs.widgets.tables.tables            580: INFO  
  \- Size \[58, 160] Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/media/editors/selectors.py", line 133,
in on_index_change self.handler(index, self.itemText(index)) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/managers/calendars.py", line 715, in
cmd_on_change_scope self.set_scope(scope) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/managers/calendars.py", line 963, in set_scope
self.calendar = NchantdCalendar(self, cfg).initWidget()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/calendars.py", line 108, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/calendars.py", line 91, in
initView self.calendar = NchantdYearCalendar(self, cfg).initWidget()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 105, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 89, in
initView self.month_tables\[i] = NchantdGrid(self, cfg).initWidget()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 604, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 592, in
initView grid_layout.addWidget(cell, row, col) TypeError:
'PySide6.QtWidgets.QGridLayout.addWidget' called with wrong argument types:
PySide6.QtWidgets.QGridLayout.addWidget(NchantdCell, int, int) Supported
signatures: PySide6.QtWidgets.QGridLayout.addWidget(w:
PySide6.QtWidgets.QWidget, /) PySide6.QtWidgets.QGridLayout.addWidget(arg__1:
PySide6.QtWidgets.QWidget, row: int, column: int, /, alignment:
PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))
PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row:
int, column: int, rowSpan: int, columnSpan: int, /, alignment:
PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))

', 'MIT'], ['email_validator', '2.2.0', 'The Unlicense (Unlicense)'] 2026-07-28
23:56:12,370 - nchantrs.widgets.tables.tables            298: INFO     - Num
Columns 40 2026-07-28 23:56:12,370 - nchantrs.widgets.tables.tables           
300: INFO     - Columns None 2026-07-28 23:56:12,370 -
nchantrs.widgets.tables.tables            131: WARNING  - calc roman numerals
Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/workbooks/matricies.py", line 1701, in
on_cell_changed address = f"{chr(65 + item.column())}{item.row() + 1}"
^^^^^^^^^^^^^ TypeError: 'NoneType' object is not callable Traceback (most
recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/workbooks/matricies.py", line 1701, in
on_cell_changed address = f"{chr(65 + item.column())}{item.row() + 1}"
^^^^^^^^^^^^^ TypeError: 'NoneType' object is not callable Traceback (most
recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/workbooks/matricies.py", line 1701, in
on_cell_changed address = f"{chr(65 + item.column())}{item.row() + 1}"
^^^^^^^^^^^^^

ne}}, 'file_path': '', 'widget':
'nchantrs.widgets.calendars.years.NchantdYearCalendar', 'tid':
'06a69701-b37d-7970-8000-debb2606a30e', 'document': {'data': None, 'data_str':
None, 'did': '06a69701-b37d-77c7-8000-f0e6de3282a4', 'syntax': None, 'name':
'2026', 'position': 0, 'document_type': None, 'readonly': 0, 'editable': 1,
'visible': 1, 'moveable': 1, 'tid': '06a69701-b37d-7970-8000-debb2606a30e',
'pid': '06a69701-b343-732f-8000-93abb6533a35', 'widget':
'nchantrs.widgets.calendars.years.NchantdYearCalendar', 'widgdata': '{}',
'version': None, 'tab_type': 'year', 'location': None, 'encoding': None,
'tags': None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}},
'apps': ['nchantrs', 'nchantdoffice'], 'app': 'nchantdoffice', 'pos': 'center'}
2026-07-28 23:20:00,931 - nchantrs.widgets.widgets                 1034: INFO  
  \- nchantrs.widgets.calendars.years.NchantdYearCalendar 2026-07-28
23:20:00,938 - nchantrs.widgets.tables.tables            578: INFO     - Size
640 480 2026-07-28 23:20:00,938 - nchantrs.widgets.tables.tables           
580: INFO     - Size \[58, 160] Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/views/treeviews.py", line 193, in onLeftClick
self.set_current_node(signal) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/views/treeviews.py", line 275, in
set_current_node node.updateTabs("center") File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/items/nodes.py", line 551, in
updateTabs self.app.view.panes\[view].model.buildTabSet(self, view) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3133, in buildTabSet self.load_tab_set(tabset,
active_tab_position) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3230, in load_tab_set self.load_tab(tab, tabn,
tabset, active_tab_position) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3344, in load_tab super().load_tab(tab, tabn,
tabset, active_tab_position) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 237, in load_tab
self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab),
tabset, tab)) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3380, in load_widget tabW.initWidget() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 105, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 89, in
initView self.month_tables\[i] = NchantdGrid(self, cfg).initWidget()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 604, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 592, in
initView grid_layout.addWidget(cell, row, col) TypeError:
'PySide6.QtWidgets.QGridLayout.addWidget' called with wrong argument types:
PySide6.QtWidgets.QGridLayout.addWidget(NchantdCell, int, int) Supported
signatures: PySide6.QtWidgets.QGridLayout.addWidget(w:
PySide6.QtWidgets.QWidget, /) PySide6.QtWidgets.QGridLayout.addWidget(arg__1:
PySide6.QtWidgets.QWidget, row: int, column: int, /, alignment:
PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))
PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row:
int, column: int, rowSpan: int, columnSpan: int, /, alignment:
PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))

During handling of the above exception, another exception occurred:

Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/views/treeviews.py", line 195, in onLeftClick
self.set_current_node(signal) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/views/treeviews.py", line 275, in
set_current_node node.updateTabs("center") File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/items/nodes.py", line 551, in
updateTabs self.app.view.panes\[view].model.buildTabSet(self, view) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3133, in buildTabSet self.load_tab_set(tabset,
active_tab_position) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3230, in load_tab_set self.load_tab(tab, tabn,
tabset, active_tab_position) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3344, in load_tab super().load_tab(tab, tabn,
tabset, active_tab_position) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 237, in load_tab
self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab),
tabset, tab)) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3380, in load_widget tabW.initWidget() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 105, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/calendars/years.py", line 89, in
initView self.month_tables\[i] = NchantdGrid(self, cfg).initWidget()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 604, in
initWidget self.initView() File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/tables/tables.py", line 592, in
initView grid_layout.addWidget(cell, row, col) TypeError:
'PySide6.QtWidgets.QGridLayout.addWidget' called with wrong argument types:
PySide6.QtWidgets.QGridLayout.addWidget(NchantdCell, int, int) Supported
signatures: PySide6.QtWidgets.QGridLayout.addWidget(w:
PySide6.QtWidgets.QWidget, /) PySide6.QtWidgets.QGridLayout.addWidget(arg__1:
PySide6.QtWidgets.QWidget, row: int, column: int, /, alignment:
PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))
PySide6.QtWidgets.QGridLayout.addWidget(arg__1: PySide6.QtWidgets.QWidget, row:
int, column: int, rowSpan: int, columnSpan: int, /, alignment:
PySide6.QtCore.Qt.AlignmentFlag = Default(Qt.Alignment))

2026-07-28 23:19:14,162 - nchantrs.widgets.widgets                 1028: INFO  
  \- Load Widget Config {'NchantdWidget': {'dstruct': {'database': {'objects':
None}}}, 'RegisteredWidgets': {'<(CHART)>': None, '<(CUSTOM)>': "need a method
for telling the widget where to read the data from widgetdata:\\n  path:
group000.label000\\n  entry: 'Summary'\\n  layer: data #format, formula,
data\\ngroup000.textbox000\\n", '<(DOCEDIT)>':
'nchantrs.widgets.editors.NchantdDocEditor', '<(LABEL)>':
'nchantrs.widgets.annotations.NchantdLabel', '<(SCRATCHEDIT)>':
'nchantrs.widgets.editors.NchantdScratchEditor', '<(TEXTBOX)>':
'nchantrs.widgets.editors.NchantdEntryBox'}, 'expandCFG': {'fonts': {'default':
{'font': 'Times', 'size': 12, 'style': 'regular'}}, 'styles': {'default':
None}}, 'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager':
{}, 'tab': {'data': None, 'data_str': None, 'did':
'024694d6-f14b-435b-a130-f86a7e4e447f', 'syntax': None, 'name': 'Affiliate
Manager', 'position': 2, 'document_type': None, 'readonly': 0, 'editable': 1,
'visible': 1, 'moveable': 1, 'tid': '06a69701-b24f-78a4-8000-076ddb717b53',
'pid': '066a7cf6-5aca-79a2-8000-f4b5405a0427', 'widget':
'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager',
'widgdata': '{}', 'version': None, 'tab_type': 'custom_widget', 'location':
None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon':
None, 'modon': None}}, 'file_path': '', 'widget':
'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager', 'tid':
'06a69701-b24f-78a4-8000-076ddb717b53', 'document': {'data': None, 'data_str':
None, 'did': '024694d6-f14b-435b-a130-f86a7e4e447f', 'syntax': None, 'name':
'Affiliate Manager', 'position': 2, 'document_type': None, 'readonly': 0,
'editable': 1, 'visible': 1, 'moveable': 1, 'tid':
'06a69701-b24f-78a4-8000-076ddb717b53', 'pid':
'066a7cf6-5aca-79a2-8000-f4b5405a0427', 'widget':
'nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager',
'widgdata': '{}', 'version': None, 'tab_type': 'custom_widget', 'location':
None, 'encoding': None, 'tags': None, 'hash': None, 'meta_data': {'creon':
None, 'modon': None}}, 'apps': ['nchantrs', 'nchantdoffice'], 'app':
'nchantdoffice', 'pos': 'center'} 2026-07-28 23:19:14,162 -
nchantrs.widgets.widgets                 1034: INFO     -
nchantdoffice.widgets.config.settings.NchantdOfficeAffiliateManager Traceback
(most recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/widgets.py", line 149, in on_tab_focus
self.model.load_tab(self.model.tabsdata\[tabn], tabn, self.pane_position) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3344, in load_tab super().load_tab(tab, tabn,
tabset, active_tab_position) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 237, in load_tab
self.tab_widgets.insert(tabn, self.load_widget(self.parse_widget_data(tab),
tabset, tab)) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3380, in load_widget tabW.initWidget() File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/documents.py", line 142, in initWidget
self.initModel() File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/config/referral_panel.py", line 82, in initModel
self._load_or_generate_code() File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/config/referral_panel.py", line 310, in
_load_or_generate_code getattr(self.user, "id", None) ^^^^^^^^^ AttributeError:
'NchantdOfficeReferralPanel' object has no attribute 'user'

, 'tab_type': 'custom_widget', 'location': None, 'encoding': None, 'tags':
None, 'hash': None, 'meta_data': {'creon': None, 'modon': None}} 2026-07-28
23:18:07,946 - nchantdoffice.widgets.tabs                 42: INFO     -
\[tabs] NchantdOfficeTab._init_ parent=NchantdOfficeHelpDocs 2026-07-28
23:18:07,949 - nchantdoffice.widgets.tabs                 52: INFO     -
\[tabs] NchantdOfficeTab.initModel cfg_provided=False 2026-07-28 23:18:07,953 -
nchantdoffice.widgets.config.help         118: INFO     - \[help] initView:
reader build failed: 'document' Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/config/help.py", line 115, in initView self.reader =
NchantdOfficePDF(self, {}).initWidget() ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/media/pdfs.py", line 192, in initWidget
self.initModel() File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/media/pdfs.py", line 157, in initModel
logma.json(self.config.dikt["document"]) ~~~~~~~~~~~~~~~~^^^^^^^^^^^^ KeyError:
'document' Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/widgets.py", line 149, in on_tab_focus
self.model.load_tab(self.model.tabsdata\[tabn], tabn, self.pane_position) File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/models.py", line 3344, in load_tab super().load_tab(tab, tabn,
tabset, active_tab_position) File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/models/tabsetmodels.py", line 238, in load_tab
self.tab_widgets\[tabn].dummy = False ~~~~~~~~~~~~~~~~^^^^^^ IndexError: list
index out of range 2026-07-28 23:18:11,296 - nchantrs.widgets.widgets          
       414: INFO     - Focus Out

2026-07-28 22:52:27,642 - nchantrs.widgets.widgets                  446: INFO  
  \- Mouse Press Event 2026-07-28 22:52:27,642 - nchantrs.widgets.widgets       
          466: INFO     - Left Click
\<PySide6.QtGui.QMouseEvent(MouseButtonPress LeftButton pos=295,292 scn=641,361
gbl=641,387 dev=QInputDevice(QPointingDevice("Virtual core pointer" Mouse id=2
seat=30002 caps=Position|Scroll|Hover buttonCount=32))> 2026-07-28 22:52:27,642
\- nchantrs.widgets.widgets                  467: INFO     - Left Click
Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/
chantdoffice/widgets/documents/workbooks/matricies.py", line 1713, in
on_selection_changed self.cell_ref_label.setText(address) ^^^^^^^^^^^^^^^^^^^
AttributeError: 'NchantdOfficeMatrix' object has no attribute 'cell_ref_label'

2026-07-27 19:45:49,937 - nchantdoffice.models                      391: INFO  
  \- Dumped Content {"content": {"file_path":
"/home/solubrew/Downloads/ssrn-4668072.pdf"}, "path":
"/home/solubrew/Downloads/ssrn-4668072.pdf"} 2026-07-27 19:45:49,937 -
nchantdoffice.models                      394: INFO     - Encoded Dictionary
b'eyJjb250ZW50IjogeyJmaWxlX3BhdGgiOiAiL2hvbWUvc29sdWJyZXcvRG93bmxvYWRzL3Nzcm4tND
2ODA3Mi5wZGYifSwgInBhdGgiOiAiL2hvbWUvc29sdWJyZXcvRG93bmxvYWRzL3Nzcm4tNDY2ODA3Mi5
ZGYifQ==' Traceback (most recent call last): File
"/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNc
antrs/1_DELTA/nchantrs/nchantrs/widgets/controls/buttons.py", line 177, in     
               

                       

##  `TODOs.md`  

`TODOs.md`  `TODOs.md → Sprint 1 + Sprint 2 (2026-07-28) — persistence + safety
pass` `45 passed, 2 skipped`

 `T-NEW-015T-NEW-022`

## `BUGs.md` 


||                                                           |                                       |
||-----------------------------------------------------------|---------------------------------------|
||`nchantrs.widgets.calendars.months.py:114`                 |`context_menu_name`                    |
||`nchantrs.widgets.tables.tables.py:592`                    |`QGridLayout.addWidget(NchantdCell, ...)`|
||`nchantdoffice/widgets/documents/workbooks/matricies.py:1701`|`chr(None)`                            |
||`matricies.py:1713`                                        |`cell_ref_label`                       |
||`nchantdoffice/widgets/config/referral_panel.py:310`       |`self.user`                            |
||`pdfs.py:157`                                              |`KeyError: 'document'`                 |
||`nchantrs/models/tabsetmodels.py:238`                      |`tab_widgets\[tabn]`                   |
||`nchantdoffice/widgets/documents/atnrg/browsers.py:348`    |`store_link(tag=...)`                  |

 |`.pyof`  

 ---

 ## [Unreleased] — 2026-08-25

 #### Card: DESK T-NEW-051 — fix(license): tolerate dict prefs + fail-soft bootstrap on offline

 Fix two production crashes observed in `testing-report_20260825.md`:

 1. **`startup_refresh: could not write entitlement_stale=True to preferences_db: 'dict' object has no attribute 'set'`** — the production caller in `nchantdoffice/views.py` wires `preferences_db=self.config.dikt["preferences"]` (a plain dict), but `_set_stale` was calling the PreferencesDB-style `.set(key, value)` API. Now duck-types via `hasattr(preferences_db, "set")` and falls back to subscript assignment for plain dicts.

 2. **Desktop boot crash on offline / DNS failure (`Cannot connect to host api.nchantdoffice.com:443 [Name or service not known]`)** — the first-launch bootstrap path caught `aiohttp.ClientConnectorDNSError` (subclass of `OSError`) under a generic `except Exception` and **re-raised**, propagating out of `NchantdOfficeCloakView.__init__` and killing the desktop. Now splits the except clause: transient `(asyncio.TimeoutError, OSError)` returns `{action: "skipped", reason: "offline"}` and persists `entitlement_stale=True` so the next launch retries; only real `BootstrapError` (4xx/5xx from server) still raises.

 Same fail-soft treatment applied to the bootstrap-fallback-after-`RefreshRevokedError` path.

 - `nchantdoffice/license/startup_refresh.py` — duck-type `_set_stale`; split bootstrap except clauses; update docstrings.
 - `tests/license/test_startup_refresh.py` — 3 new regression tests pinning down the exact symptoms from the testing report (dict-prefs, offline-bootstrap, combined end-to-end). All green: `tests/license/test_startup_refresh.py` 11 passed.

 **Validation:** 11/11 startup_refresh tests green, 55/55 license module green, full suite shows the same 33 pre-existing unrelated failures as before the patch (909 → 912 passed = +3 new tests; no new failures).

---

#### Card: DESK T-NEW-052 — refactor(urls): route every nchantdoffice.com reference through YAML config

Move every hardcoded `nchantdoffice.com` / `api.nchantdoffice.com` URL in the desktop to a single YAML-driven resolver so the operator can switch between production and internal docker without code edits.

**New module:** `nchantdoffice/utilities/urls.py` — typed accessors (`urls.server_base_url()`, `urls.affiliate_api_base()`, `urls.home_page()`, `urls.upgrade_compare_url()`, etc.) layered over:
  1. Hardcoded fallback dict (shipped with package).
  2. Bundled YAML `nchantdoffice/utilities/_data_/urls.yaml` (production defaults).
  3. XDG user config `urls:` block (per-deploy overrides).

12 URL keys covering API endpoints (license bootstrap/refresh/claim, affiliate, feature-gates, updates, sync) and marketing deep-links (homepage, compare, registration, whats_new, affiliate_marketing, share landing, marketing base for ad CTAs).

**Call sites updated (15 files):**
- License: `views.py`, `widgets/config/accounts.py`
- Affiliate/referral: `utilities/referral.py`, `utilities/links.py`, `widgets/config/referral_panel.py`
- Updates/sync/feature-gates: `updates/checker.py`, `sync/applier.py`, `utilities/feature_gates.py`
- UI surfaces: `widgets/documents/atnrg/browsers.py`, `widgets/documents/atnrg/pages.py`, `widgets/advertisements.py`, `utilities/upgrades.py`, `utilities/config.py`, `widgets/documents/atnrg/_data_/pages.yaml`
- Config schema: `utilities/user_config.py` (added `urls:` block docs + dev-mode example pointing at `192.168.1.67`)

**Tests:** New `tests/utilities/test_urls_config.py` with 11 tests covering bundled defaults, XDG overrides, unknown-key warnings, trailing-slash normalisation, and a regression-guard test that walks every `.py` file in `nchantdoffice/` via AST to assert no caller still hardcodes the production hostname. All green.

**Validation:** 11/11 urls tests green, 66/66 license+utilities tests green, full suite shows same 33 pre-existing failures as before the patch (no new regressions).

**To switch to internal docker:** operator edits `~/.config/nchantdoffice/config.yaml` and sets the `urls:` block per the example in `utilities/user_config.py` — no code change required.

---

#### Card: DESK T-NEW-053 — feat(urls): run-mode launch profile (dev=internal docker, prod=cloud)

Launch-time URL profile selector. The operator picks a complete URL set at startup — no config file editing required.

**New module surface (`nchantdoffice/utilities/urls.py`):**
- `DEV_URLS` table — 12 internal-host URLs (`http://192.168.1.67:8081` for the API, `:8080` for the marketing site).
- `PROD_URLS` table — empty (the resolver uses bundled defaults).
- `get_run_mode() -> str` — current mode (default `"prod"`).
- `set_run_mode("dev" | "prod")` — flips the active profile, invalidates the resolver cache. Idempotent. Invalid values raise `ValueError`.

**Resolver layering updated:** run-mode profile sits between XDG user overrides and the explicit per-call kwarg, so a `run-mode: dev` launch wholesale redirects every URL surface (license bootstrap, embedded browser homepage, account tab in Settings, upgrade prompts, ad CTAs) at the internal docker.

**Launch entrypoint wired (`cmds/runNchantdOffice.py`):**
- `_parse_run_mode(args, cfg)` reads run-mode from (highest first):
  1. `cfg["run-mode"]` (primary — what `nchantment()` callers pass)
  2. `--run-mode=dev` / `--run-mode prod` CLI flag
  3. `NCHANTDOFFICE_RUN_MODE` env var (escape hatch for test harnesses)
  4. Default `"prod"`
- Calls `urls.set_run_mode(...)` BEFORE any URL accessor, so the very first call returns the right value.
- Backward compat: legacy `cfg["website_override"]` still works — when present but `run-mode` unset, run-mode infers to `"dev"` so existing launch scripts don't break.

**Tests:** 6 new run-mode tests in `tests/utilities/test_urls_config.py` (defaults to prod, set-to-dev flips every accessor, set-back-to-prod reverts, invalid value raises, idempotent, cache invalidation). All 21 urls tests + 76 license+utilities tests pass.

**Operator workflow:**
```python
# Production / end-user launch
cfg = {"run-mode": "prod"}     # default; explicit for clarity
nchantment("NchantdOffice", args, app, cfg, wizard)

# Operator's LAN docker launch
cfg = {"run-mode": "dev"}
nchantment("NchantdOffice", args, app, cfg, wizard)

# OR via CLI flag (no code change at call site):
python cmds/runNchantdOffice.py --run-mode=dev
```

Both modes ship the same binary — no rebuild required to flip environments.

---

#### Card: DESK T-NEW-054 — fix(license): swallow BootstrapError on first-launch bootstrap (was crashing on docker 404)

Live launch regression (2026-08-25 18:11:41) — operator launched with `run-mode: dev` against `http://192.168.1.67:8081` (the LAN docker stack). The docker AppBuilder returned **HTTP 404** with HTML "Page not found" for the `/api/desktop/install-bootstrap` endpoint (the endpoint blueprint hadn't been deployed yet — operator is mid-setup). The desktop then crashed at boot with:

```
nchantdoffice.license.remote.BootstrapError:
  install-bootstrap returned HTTP 404: '<!DOCTYPE html>...'
```

T-NEW-051 only swallowed `(asyncio.TimeoutError, OSError)` on the bootstrap path; `BootstrapError` (the 4xx/5xx result) was caught by a broad `except Exception` and **re-raised**, propagating out of `NchantdOfficeCloakView.__init__`.

**Fix:** broaden the except clause to include `BootstrapError`. Same fail-soft treatment as the network-error path — log, persist `stale=True`, return `{action: "skipped", reason: "offline"}`. The desktop boots in free-tier mode; the next launch retries when the operator has finished setting up the docker endpoint.

Same fix applied to the bootstrap-fallback-after-`RefreshRevokedError` path (the other place the same bug lurked).

**Tests:** 2 new tests in `tests/license/test_startup_refresh.py` (`test_first_launch_bootstrap_404_returns_skipped_offline`, `test_first_launch_bootstrap_500_returns_skipped_offline`). 13/13 startup_refresh tests + 78/78 license+utilities tests pass.

**Trade-off:** no longer distinguishes "real auth failure" (operator typo'd credentials) from "endpoint missing". Both surface as offline + retry-next-time. Acceptable because the operator sees a clear log message naming the actual error, and the entitlement cache's stale-check still drives a retry on next launch.

---

#### Card: DESK T-NEW-056 — refactor(urls): collapse dev profile to single port (LAN deploy uses one Flask port)

The DESK T-NEW-053 dev profile split API and marketing across
two ports (`8081` for the API, `8080` for the marketing site).
That was a wrong assumption: the nchantdoffice_com Flask app
serves BOTH `/api/desktop/*` and `/`, `/registration`, etc. on
a single port (the LAN deploy `cluster-up.lan.sh` binds Flask
port 5000 to host port 8081). Splitting them left the desktop
hitting `192.168.1.67:8080` (which wasn't running) for the
marketing pages.

**Fix:** both DEV_API_BASE and DEV_WEB_BASE now resolve to
`http://192.168.1.67:8081`. The constants `DEV_INTERNAL_HOST`
and `DEV_INTERNAL_PORT` are the single source of truth; if the
operator's LAN deploy uses a different port they edit those
two constants (no env vars per the T-NEW-070 directive).

**Tests:** updated `test_set_run_mode_to_dev_flips_all_accessors`
and `test_update_affiliate_links_dev_url_constructs_correctly` to
expect the new single-port dev URLs. 80/80 license+utilities
tests pass.

Also demoted the `requests.exceptions.RequestException` (DNS,
connection refused, etc.) log level in `links.py::APIClient.get`
from ERROR to WARNING: when `run-mode: dev` is active and the
operator is mid-setup on a docker stack that hasn't deployed
the affiliate service yet, "connection refused" is expected
state, not a bug. `HTTPError` (4xx/5xx from a reachable server)
stays at ERROR because that IS actionable. `Timeout` was
already WARNING.

---

#### Card: DESK T-NEW-057 — fix(links): use x-api-key header + read api_key from InstallStore (401 fix)

Live launch regression (2026-08-25 18:39) after the operator
brought up the LAN cluster. The desktop's affiliate sync hit:

```
GET http://192.168.1.67:8081/api/affiliate/links/
→ 401 Unauthorized
```

Two bugs in the same code path:

1. `APIClient.__init__` was setting `Authorization: Bearer
   <api_key>` — the FAB-User auth convention. The
   server's `@require_desktop_api_key` decorator reads
   `request.headers.get("x-api-key")` and ignores the
   `Authorization` header. The two are visually similar in
   the browser dev tools but the server treats them as
   distinct.

2. `update_affiliate_links` was constructing
   `APIClient(API_URL)` with no api_key, so the call had
   no credentials at all. The install's api_key lives in
   `InstallStore` (populated by the install bootstrap) and
   the affiliate sync wasn't reading it.

**Fix:** `APIClient` now sets `x-api-key: <key>` (not
Authorization). `update_affiliate_links` lazy-imports
`InstallStore` and passes `record.get("api_key")` to the
client. If the install hasn't bootstrapped yet (api_key is
None), the call still runs (no header set) and gets a 401,
which the outer try/except logs and swallows. The desktop
keeps 0 affiliates instead of crashing.

**Tests:** 5 new tests in `tests/utilities/test_links_url.py`
covering: x-api-key header (not Bearer), no-auth sends no
auth header, 401 returns zeros (not crash), end-to-end api_key
flows from InstallStore to x-api-key header, and the
no-api_key-yet pre-bootstrap path. 85/85 license+utilities
tests pass.

**Cross-repo note:** the server's
`@require_desktop_api_key` in `app/apis/updates.py:93` is
unchanged — it was correct, the desktop was wrong.

---

#### Card: DESK T-NEW-058 — fix(links): skip affiliate sync until install has an api_key (sequencing fix)

The operator reported that the affiliate sync fired IMMEDIATELY
after `Nchantment Initialized` with no api_key yet — returning
401. The bootstrap (`startup_refresh.refresh_if_needed`) runs
synchronously in `NchantdOfficeCloakView.__init__`, but the
model init (which calls `update_affiliate_links`) can fire
before the bootstrap's HTTP call has completed. Sending a
network call without credentials is wasted bandwidth and a
noisy 401.

**Fix:** `update_affiliate_links` now checks
`InstallStore().get_or_create()["api_key"]` upfront. If
`api_key` is None (fresh install, install bootstrap returned
4xx/5xx and was swallowed fail-soft, or `install.bin` is
missing), the function returns zeros immediately and logs a
clear `INFO` line naming the install_id and the bootstrap
path. The next launch will retry once the bootstrap has
minted an api_key.

**Debug logging added (also DESK T-NEW-058):**

- `[startup_refresh] BEGIN: install_id=… api_key_present=True/False entitlement_cached=…`
  — single banner that tells the operator whether the
  install is bootstrapped at function entry
- `[startup_refresh] bootstrap OK: minted api_key='nk_test_…' (saved to InstallStore)`
  — fired on successful first-launch bootstrap, so the
  operator can confirm the key is on file
- `[links] update_affiliate_links: using api_key for install_id=… against <url>`
  — confirms the api_key was sourced from InstallStore and
  which server the call is heading to
- `[links] skip affiliate sync: no api_key in InstallStore yet (install_id=…)`
  — explains WHY the affiliate call is silent (correlates
  with the bootstrap banner)

**Tests:** 1 updated test (the "no api_key → still make the
call" test was inverted to "no api_key → skip the call
entirely"). 85/85 license+utilities tests pass. The
regression-guard test uses an `AssertionError` mock so any
future code that re-introduces a network call in the skip
path will fail loudly.

---

#### Card: DESK T-NEW-055 — fix(links): stop doubling the affiliate API URL path

Live launch regression (2026-08-25 18:18:15) — after the operator moved to `run-mode: dev`, the affiliate sync path hit:

```
HTTPConnectionPool(host='192.168.1.67', port=8080):
  /api/affiliate/links/affiliate/links/
```

That's a **doubled path**: `affiliate_api_base` already ends in `/api/affiliate`, then `API_URL = f"{_aab()}/links/"` appended `/links/`, then `client.get("affiliate/links/")` appended `/affiliate/links/` AGAIN.

The pre-T-NEW-052 code had the same bug (it hardcoded `API_URL = ".../api/affiliate/links/"` then passed `"affiliate/links/"` to the client). Production masked it with a wildcard Flask route; dev mode (192.168.1.67) returned connection-refused and surfaced the bug.

**Fix:** pick one convention. `API_URL` is now just the API base (`affiliate_api_base()`, i.e. `/api/affiliate`); the resource path is the caller's job (`"links/"`). The base + path now resolves to the canonical `{affiliate_api_base}/links/` endpoint.

**Tests:** 2 new tests in `tests/utilities/test_links_url.py` (prod URL + dev URL) that mock `requests.Session.get` and capture the URL passed in. Both tests RED with the bug present, GREEN with the fix. 80/80 license+utilities tests pass.

---

#### Card: DESK T-NEW-061 — fix(ad-tab): server-driven rotation, desktop just surfaces every 5 minutes

**The problem:** DESK T-NEW-060 routed the Ad tab through
the unified URL resolver — that fixed the URL, but the
desktop was still doing ALL the rotation logic locally:
a 5-slot type registry (Tip / Substack / ProCta /
Affiliate / ProInternal), a 12-second QTimer, an
`_advance_slot()` callback that raced with the in-flight
HTTP fetches. The operator reported the application
**locking up** on launch (2026-08-25). The lockup was
the timer firing while `_load_banners` / `_load_affiliate_rotation`
were still mid-flight from a previous fetch — classic
re-entrancy deadlock.

**The new design (operator-mandated):**

- The **server** picks the ad. New endpoint
  `GET /api/ads/rotation/next` on `nchantdoffice_com`
  returns ONE ad, rotated server-side via a deterministic
  time-bucket (floor(epoch_seconds / interval_seconds) %
  len(active_ads)). Two desktops on the same LAN see the
  same ad at the same time.
- The **desktop** just surfaces the tab every 5 minutes.
  Single QTimer at 300_000 ms, fires `_fetch_and_render`
  which calls the server and renders whatever came back.
  No local slot rotation, no 5-slot type registry, no
  `_advance_slot` race. The manual Refresh button calls
  `_fetch_and_render` directly.
- The previous `PRO_INTERNAL_PROMOS` list, the
  `RotationSlot` subclasses, the `TipSlot` / `SubstackSlot`
  / `ProCtaSlot` / `AffiliateSlot` / `ProInternalSlot` are
  kept around (backward-compat for any imports) but the
  AdTab no longer uses them. All ad content is owned by
  the operator via the server's admin UI.

**Server-side endpoint** (`nchantdoffice_com`):

- `GET /api/ads/rotation/next?interval_seconds=NNN` returns
  200 + `{"ad": {...}, "as_of": "...", "bucket": N, "rotation_interval_seconds": NNN}`
- `GET /api/ads/rotation/health` returns 200 + `{"status": "ok", "count": N, "rotation_interval_seconds": 300}`
- `interval_seconds` clamps to `[60, 86400]` so a typo or
  malicious probe can't make every desktop caller spin
  through thousands of ads per second.
- Returns 204 No Content when the operator's catalog is
  empty (desktop renders its empty state).

**Desktop-side changes** (`nchantdoffice`):

- New module `nchantdoffice/widgets/ad_rotation_client.py`
  with a single `fetch_rotation_ad(server_base_url)`
  function — fail-soft, returns `None` on any error.
- `DEFAULT_INTERVAL_MS = 12000` replaced with
  `DEFAULT_SURFACE_INTERVAL_MS = 300_000` (5 minutes).
- `advertisements.yaml` key renamed from `interval_ms`
  to `surface_interval_ms` (the old key is silently
  ignored if present, so the rename is forward-compatible).
- The "Next" button in the UI is now a "Refresh" button
  (next button would imply local cycling).

**Tests:**

- Server: 10 new tests in
  `nchantdoffice_com/tests/test_ad_rotation_endpoint.py`
  (endpoint exists, 200 happy path, 204 empty state,
  response shape, deterministic per-bucket, interval
  clamping, health endpoint).
- Desktop: 8 new tests in
  `nchantdoffice/tests/utilities/test_ad_rotation_client.py`
  (200 happy path, 204 empty, connection-refused fail-soft,
  500 fail-soft, malformed response fail-soft, invalid JSON
  fail-soft, surface-interval-is-5-minutes regression
  guard, custom interval).

End-to-end smoke against the live LAN docker:
```
GET /api/ads/rotation/next?interval_seconds=60
→ {"ad": {"id": 3, "slug": "supabase-default", "title": "Supabase..."},
   "bucket": 29795174, "rotation_interval_seconds": 60}
```

85 license+utilities desktop tests + 16 nchantdoffice_com
route tests pass. The lockup cause (12-second timer racing
with HTTP fetches) is structurally removed — there are no
more concurrent fetches, only one fetch every 5 minutes.

**Operator workflow:** pull both repos, rebuild the web
image (`docker compose build web`), recreate the container
(`LAN_PORT=8081 bash /home/solubrew/docker-data/nchantdoffice/scripts/cluster-up.sh`),
restart the desktop. The Ad tab now surfaces an ad from
the LAN docker on launch and re-surfaces every 5 minutes
with whatever the server's time-bucket rotation has picked.

