# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt
import json as j

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.utilities.utils import lookup
from nchantrs.dialogs.dialogs import NchantdSigil
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantdoffice.dialogs.imports import NchantdGoogleDriveSigil
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.controls.buttons import NchantdButton
from kahndor.logma import Logma
from nchantdoffice.widgets.controls.buttons import NchantdOfficeNewDocumentAcceptButtons
from nchantdoffice.widgets.panes.new import NchantdOfficeNewDocumentPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
debug = True

# ====================================================================================================================||
pxcfg = join(here, "_data_", "documents.yaml")


class NchantdNewDocumentSigil(NchantdSigil):
    """"""

    def __init__(self, name, parent=None, cfg=None):
        """ """
        super().__init__(name, parent)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NewNchantdDocumentSigil"))
        if self.parent:
            self.config.override(parent.config)
        logma.info(f"CFG {cfg}")
        self.config.override(cfg)
        self.catalog = None
        self.file_type = self.config.dikt.get("file_type", None)
        self.action = name  # self.config.dikt.get('action', None)
        self.document_nm = None
        # logma.info(f"Name {name} {self.file_type} {self.action}")
        self.file_type = None
        self.google_available_bit = False
        self.local_available_bit = False
        self.multi_page_import = False
        self.widget = None
        self.load_google = None
        self.params = None
        self.open_file = None
        self.import_file = None
        self.open_book = None
        self.file_path = None
        self.file_path_label = None
        self.connect_gfile = None
        self.launch_button_layout = None

    def finalizeView(self):
        """"""
        logma.info(f"Finalize View")
        cfg = {
            "buttons": {
                "ok": {"handler": self.accept},
                "import_all_file": {"handler": self.import_file},
                "cancel": {"handler": self.reject},
            }
        }
        self.buttons = NchantdOfficeNewDocumentAcceptButtons(self, cfg).initWidget()
        layout = pyqt.QHBoxLayout()
        layout.addWidget(self.buttons)
        layout.setAlignment(self.getAlignment("right"))
        self.layout.addLayout(layout)

    def import_file(self):
        """"""

    def initModel(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg = {"size": None}
        super().initModel(cfg)
        self.all_items = self.app.model.get_document_types()
        self.all_items.sort_values(by=["file_type_txt", "sequence_int", "document_txt", "name_txt"], inplace=True)
        self.all_items.reset_index(drop=True, inplace=True)
        logma.info(f"Action {self.action}")
        # self.document_nm = self.action.replace("add_", "")
        # # if log:
        # #     logma.info(f"Document Name {self.document_nm}")
        # self.document = self.app.model.store.get_document(self.document_nm).to_dict(orient="records")[0]
        # # if log:
        # #     logma.info(f"Document {self.document}")
        # self.widget = self.document["widget_txt"]
        # self.params = j.loads(self.document["parameters_dict"].replace("'", '"'))
        # if int(self.document["google_available_bit"]) == 1:
        #     self.google_available_bit = True
        # if int(self.document["local_available_bit"]) == 1:
        #     self.local_available_bit = True
        return self

    def initView(self):
        """

        :param file_type:
        :return:
        """
        super().initView({"layout": "horizontal"})
        cfg = {"layout": "horizontal", "options": self.all_items["name_txt"].values.tolist()}
        self.pane = NchantdOfficeNewDocumentPane(self, cfg).initWidget()
        self.layout.addWidget(self.pane)
        # if self.file_type is None:
        #     self.file_type = "all_file"
        # self.launch_button_layout = pyqt.QHBoxLayout()
        # self.launch_button_layout.setAlignment(pyqt.Qt.AlignLeft)
        # if self.google_available_bit:
        #     self.init_google_drive_button()
        # if self.local_available_bit:
        #     self.init_local_drive_button()
        # self.layout.addLayout(self.launch_button_layout)
        # if self.multi_page_import:
        #     self.init_multi_page_import()
        return self

    def init_multi_page_import(self):
        """"""

    def init_google_drive_button(self):
        """"""
        if log:
            logma.info(f"Initialize Google Drive Button")
        gdocs = {"script": "docs", "matrix": "sheets", "image": "drive", "form": "forms", "pdf": "docs"}
        gtype = gdocs.get(self.document_nm, None)
        if gtype is None:
            raise Exception(f"Google Doc Type Not Supported {self.document_nm}")
        command = f"load_google_{gtype}"
        self.config.override({"buttons": {command: lookup(self.app, command)}})
        self.connect_gfile = NchantdButton(self, self.config.dikt["buttons"][command]).initWidget()
        self.connect_gfile.set_handler(self.open_google_drive_viewer, self.config.dikt)
        self.launch_button_layout.addWidget(self.connect_gfile)

    def init_local_drive_button(self):
        """"""
        if log:
            logma.info(f"Initialize Local Drive Button")
        # cfg = {"text": f"Open {self.file_type.upper()}", "action": f"open_{self.file_type}"}
        found = lookup(self.app, f"open_{self.file_type}")
        logma.info(f"Lookup {found}")
        self.config.override({"buttons": {f"open_{self.file_type}": lookup(self.app, f"open_{self.file_type}")}})
        self.open_file = NchantdButton(self, self.config.dikt["buttons"][f"open_{self.file_type}"]).initWidget()
        params = self.config
        self.open_file.set_handler(self.open_file_sigil, params)
        self.launch_button_layout.addWidget(self.open_file)
        if self.app.model.has_library:
            command = f"import_{self.file_type}"
            self.config.override({"buttons": {command: lookup(self.app, command)}})
            self.import_file = NchantdButton(self, self.config.dikt["buttons"][command]).initWidget()
            self.import_file.set_handler()
            self.launch_button_layout.addWidget(self.import_file)
            command = f"open_{self.file_type}"
            self.config.override({"buttons": {command: lookup(self.app, command)}})
            self.open_book = NchantdButton(self, self.config.dikt["buttons"][command]).initWidget()
            self.open_book.set_handler()
            self.launch_button_layout.addWidget(self.open_book)

    def load_document(self):
        """"""
        self.document_obj = Document.open(self.file_path)

    def open_google_drive_viewer(self, name=None, app=None, cfg=None):
        """"""
        gdrive_sigil = NchantdGoogleDriveSigil(self.parent, self.config.override(cfg))
        self.gdrive_path = gdrive_sigil.initWidget()
        if self.ok:
            self.gdrive_path.file_selected
            self.show_file_path()
            self.load_google = True

    def show_file_path(self):
        """"""
        logma.info(f"File Path {self.file_path.file_selected}")
        cfg = {"text": self.file_path.file_selected, "readonly": True}
        self.file_path_label = NchantdLabel(self, self.config.override(cfg)).initWidget()
        self.add_field(self.file_path_label)

        # if self.document_nm == "matrix":
        #     if self.file_type == "excel":
        #         document.open(self.file_path)

        # need to load the file and determine if there are multiple pages/tabs like an excel file
        # if there are then a selection list is presented for each page/tab

        self.open = True
        self.new = False
        return self

    def open_file_sigil(self, name=None, app=None, cfg=None):
        """"""
        logma.info(f"Launch Open Dialog")
        file_sigil = NchantdFileOpenSigil("open", self.parent, self.config.override(cfg))
        logma.info(f"Launch Open Dialog")
        self.file_path = file_sigil.initWidget()
        logma.info(f"File Path {self.file_path}")
        if self.file_path.file_selected:
            self.show_file_path()
            self.load_google = False

    def accept(self, action=None, app=None, params=None):
        """
        :return:
        """
        super().accept()
        super().accept_()
        self.add_tab("center")

    def add_tab(self, tabset):
        """"""
        widgdata = {}
        widgdata["doc_type"] = self.document_nm
        # cfg = {"widget": widget}
        # sigil = NewNchantdDocumentSigil(app, app.config.override(cfg)).initWidget()
        # TODO: how to integrate various formats across tools for specific tool types like a local file to open excel
        #  and a web app for google sheets...there is value to keeping that interaction native to the google sheet instead
        #  of automatically downloading and converting to a local version but how to integrate this switching
        if self.load_google:
            # TODO create a load google dialog mimic file open dialog but connect to google drive using a browser/api
            # cfg["widget"] = "nchantrs.widgets.browsers.browsers.NchantdWebApp"
            widgdata["url"] = self.file_path.file_selected
        elif self.open:
            widgdata["path"] = self.file_path.file_selected
        #        add_tab(sigil, app, widget, widgdata, doc_type, tabset)
        if self.ok:
            name = self.name.textbox.entry_data
            pid = self.app.view.panes["left"].model.current_node.nid
            self.app.view.panes[tabset].model.max_position += 1
            pos = self.app.view.panes[tabset].model.max_position
            self.app.view.panes[tabset].model.add_tab(name, pid, pos, self.widget, widgdata, self.document_nm, tabset)
            self.app.view.panes["left"].model.current_node.updateTabs(tabset)


# 		#TODO: Launch form builder wizard
# 		# options = ['ChatGPT', 'Gemini', 'LeonardoAI', 'Sora']
# 		# cfg = {'text': 'Add Form Field: ', 'options': options}
# 		# self.new_form_field = NchantdLabeledEntry(self, cfg).initWidget()
# 		# self.add_field(self.new_form_field)
# 		# options = []
# 		# cfg = {'text': 'Select Answer Type', 'options': options}
# 		# self.new_form_field_style = NchantdLabeledEntry(self, cfg).initWidget()
# 		# self.add_field(self.new_form_field_style)
# 		# cfg = {}
# 		# self.add_field_button = NchantdButton(self, cfg).initWidget()
# 		# self.add_field(self.add_field_button)
# 		# self.buttons = NchantdAcceptButtons(self, cfg).initWidget()
# 		# self.add_field(self.buttons)
# 		return self
#
# class NewNchantdMatrixSigil(NewNchantdLocalDocumentSigil):
# 	""""""
# 	def __init__(self, parent=None, cfg=None):
# 		""" """
# 		self.parent = parent
# 		self.config = kahndor.Instruct(pxcfg).select('NewNchantdMatrixSigil')
# 		if self.parent:
# 			self.config.override(parent.config)
# 		self.config.override(cfg)
# 		super().__init__('matrix', self.parent, self.config)
# 		self.import_button = None
# 		self.num_columns = None
# 		self.num_rows = None
# 		self.run_exploratory_analysis = None
# 		self.google_available_bit = True

# 			#TODO: needs to be able to handle .csv, .xlsx, .xls, .tab, etc
# 			#   not sure if that should be built into tblonql or through pyffice
# 			#   currently squirl is not designed to be application specific but more protocol specific this is loosely implemented around os
# 			#   a workbook can have mulitple tabs which complicates things as a read/write object
# 		:return:
# 		"""
# 		super().initView('matrix')
# 		self.increase_height('20%')
# 		cfg = {'text': 'Data Tools'}
# 		tools_label = NchantdLabel(self, self.config.override(cfg)).initWidget()
# 		self.layout.addWidget(tools_label)
#
# 		#do a preliminary analysis to see if the imported worksheet/book is viable as a datasource
# 		#add checkbox for edca
# 		#add checkbox for data source
#
# 		command = f'run_exploratory_analysis'
# 		self.config.override({'buttons': {command: lookup(self.app, command)}})
# 		self.run_exploratory_analysis = NchantdButton(self, self.config.dikt['buttons'][command]).initWidget()
# 		self.layout.addWidget(self.run_exploratory_analysis)
# 		return self
#
# 	def accept(self, text, app, params):
# 		""""""
# 		super().accept(text, app, params)
# 		if '.csv' == self.file_path[-4:]:
# 			self.file = tblonql.Doc(self.file_path)
# 			rdr = self.file.read()
# 			self.datao = next(rdr, None)
# 		elif '.xlsx' == self.file_path[-5:] or '.xls' == self.file_path[-4:]:
# 			self.file = WorkBook.open(self.file_path)
# 			for tab in self.file.tabs:
# 				add_tab()#for each sheet
# 		else:
# 			logma.warning(f"Unknown File Type Selected {self.file_path}")
# 			if debug:
# 				raise Exception(f"Unknown File Type Selected {self.file_path}")
#
#


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
