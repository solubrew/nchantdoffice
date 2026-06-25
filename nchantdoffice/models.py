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
from os.path import dirname, join, exists
import json as j
import datetime as dt
from dateutil import parser

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame, concat
from numpy import isnan

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from micromole.micromole import MicroMole
from nchantrs.models.tabsetmodels import NchantdTabSetModel
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.models.models import NchantdStore
from nchantrs.models.applicationmodels import NchantdModel
from nchantdoffice.utilities.links import update_affilate_links
from nchantdoffice.widgets.catalogs import NchantdOfficeDocumentsCatalog
from kahndor.logma import Logma
from pyffice.document import PyfficeDocument
from pyffice.pyffice import PyfficeCodex
from subtrix.utilities import uuid
from pycurity.pyhash import text_hashing_function, encode64
from pycurity.pyhash import decode64
from nchantdoffice.utilities.config import PyfficeApplicationConfig

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
log = False
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "models.yaml")


class NchantdOfficeInstance(object):
    """"""

    def __init__(self, cfg=None):
        """"""
        super().__init__(cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeInstance").override(cfg))


class NchantdOfficeCloakModel(NchantdCloakModel):
    """"""

    APP_NAME = "NchantdOffice"

    def __init__(self, name, instance=None, parent=None, cfg=None):
        """ """
        super().__init__(parent, None)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCloakModel").override(cfg))
        self.parent = parent
        self.store = NchantdOfficeStore(name, self)
        self.codex = PyfficeCodex()
        cfg = {}
        self.settings = PyfficeApplicationConfig(cfg)
        cfg = {}
        self.mole = MicroMole(cfg)
        self.registered_documents = {}
        self.enable_journal_focus = None
        self.enable_settings_focus = None
        self.enable_automation = None
        self.enable_datasources = None
        self.show_quick_launch_toolbar = None
        self.today = self.store.time.get_current_datetime_str()

    def initModel(self, reset=None):
        """"""
        super().initModel(reset)
        self.codex.load_document()
        docs = self.store.get_application_documents()
        self.codex.init_contacts(docs["contacts"])
        self.settings.load_document(docs["settings"])
        self.init_mole()
        return self

    def add_document(
        self, document, did, pid, pos, widget=None, widgdata=None, doc_type=None, tabset="center", db="db", tab_new=True
    ):
        """
        add_document stores a tab and creates document connected to that tab
        :param name:
        :param pid:
        :param pos:
        :param widget:
        :param widgdata:
        :param doc_type:
        :param tabset:
        :return:
        """
        logma.info(f"Add Document {document}")
        logma.info(f"Document Type {doc_type}")
        logma.info(f"Document Widget {widget}")
        if isinstance(document, PyfficeDocument):
            tab = document.to_dict()
            logma.info(f"Pyffice Document Provided {tab}")
            # tab["widget"] = lookup_widget(tab["type"])
            tab["widget"] = self.app.model.get_document_type(tab["type"]).get("widget_txt", None)
            tab["type"] = document.doc_type
            tab["pid"] = pid
            tab["position"] = pos
            tab["tabset"] = tabset
            tab["context"] = {}
            tab["version"] = 0
            tab["hash"] = ""
            tab["policy_fk"] = None
            if tab.get("content", None) is None:
                tab["content"] = tab["data"]
            tab_new = False
        else:
            tab = document
        if widget is None:  # or widget == "":
            # tab["widget"] = lookup_widget(tab["type"])
            tab["widget"] = self.app.model.get_document_type(tab["type"]).get("widget_txt", None)
        name = tab["name"]
        if widgdata is None:
            widgdata = {"name": name, "type": tab["type"], "focus": "userapp"}
        tags = ""
        context = ""
        version = 0.0
        hash_ = ""
        policy = None
        document = tab
        document["name"] = name
        document["file_name"] = tab.get("file_path", None)
        document["description"] = ""
        document["path"] = tab.get("file_path", None)
        document["location"] = tab.get("location", "internal")

        document["encoding"] = tab.get("encoding", "utf-8")
        document["tags"] = tags
        document["context"] = context
        document["version"] = version
        document["hash"] = hash_
        document["policy"] = policy
        logma.info(f"Document {document}")
        logma.info(f"Widget {widget}")
        match document["type"]:
            case "add_browser_document_nchantdbrowser":
                document["document_type"] = "browser"
                syntax = "html"
            case "browser":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_note_attachment_nchantdnote":
                document["document_type"] = "note"
                syntax = "plain-text"
            case "add_superweb_custom_nchantdprompt":
                document["document_type"] = "prompt"
                syntax = "html"
            case "add_script_document_nchantdscript":
                document["document_type"] = "script"
                syntax = "html"
            case "script":
                document["document_type"] = "script"
                syntax = "html"
            case "add_http_media_canva":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_http_media_notion":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_http_media_scenarioai":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_http_media_leonardoai":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_http_media_jsonpub":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_pdf_document_nchantdpdf":
                document["document_type"] = "pdf"
                syntax = "plain-text"
            case "add_files_document_nchantdfiles":
                document["document_type"] = "filesystem"
                syntax = "plain-text"
            case "add_image_document_nchantdimage":
                document["document_type"] = "image"
                syntax = "bytes"
                document["location"] = "external"
            case "image":
                document["document_type"] = "image"
                syntax = "bytes"
                document["location"] = "internal"
            case _:
                syntax = "plain-text"
                document["document_type"] = "note"
        document["syntax"] = syntax
        self.store.store_doc_media(document)
        page_n = 0
        entry_n = 0
        media_fk = None
        logma.info(f"Document {document}")
        logma.info(f"Type {type(document)}")
        self.add_document_content(document, media_fk, page_n, entry_n, version, hash_, policy)
        if tab_new is True:
            logma.info(f"Add Tab {widget}")
            self.add_tab(name, pid, pos, widget, widgdata, document["did"], tab["type"], tabset, True, db)
        self.has_changed = True
        return self

    def add_document_app(
        self, document, did, pid, pos, widget=None, widgdata=None, doc_type=None, tabset="center", db="db", tab_new=True
    ):
        """"""
        if isinstance(document, PyfficeDocument):
            tab = document.to_dict()
            logma.info(f"Pyffice Document Provided {tab}")
            # tab["widget"] = lookup_widget(tab["type"])
            tab["widget"] = self.app.model.get_document_type(tab["type"]).get("widget_txt", None)
            tab["type"] = document.doc_type
            tab["pid"] = pid
            tab["position"] = pos
            tab["tabset"] = tabset
            tab["context"] = {}
            tab["version"] = 0
            tab["hash"] = ""
            tab["policy_fk"] = None
            if tab.get("content", None) is None:
                tab["content"] = tab["data"]
            tab_new = False
        else:
            tab = document
        if widget is None:
            # tab["widget"] = lookup_widget(tab["type"])
            tab["widget"] = self.app.model.get_document_type(tab["type"]).get("widget_txt", None)
        name = tab["name"]
        if widgdata is None:
            widgdata = {"name": name, "type": tab["type"], "focus": "userapp"}
        tags = ""
        context = ""
        version = 0.0
        hash_ = ""
        policy = None
        document = tab
        document["name"] = name
        document["file_name"] = tab.get("file_path", None)
        document["description"] = ""
        document["path"] = tab.get("file_path", None)
        document["location"] = tab.get("location", "internal")

        document["encoding"] = tab.get("encoding", "utf-8")
        document["tags"] = tags
        document["context"] = context
        document["version"] = version
        document["hash"] = hash_
        document["policy"] = policy
        logma.info(f"Document {document}")
        logma.info(f"Widget {widget}")
        match document["type"]:
            case "add_browser_document_nchantdbrowser":
                document["document_type"] = "browser"
                syntax = "html"
            case "browser":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_note_attachment_nchantdnote":
                document["document_type"] = "note"
                syntax = "plain-text"
            case "add_superweb_custom_nchantdprompt":
                document["document_type"] = "prompt"
                syntax = "html"
            case "add_script_document_nchantdscript":
                document["document_type"] = "script"
                syntax = "html"
            case "script":
                document["document_type"] = "script"
                syntax = "html"
            case "add_http_media_canva":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_http_media_notion":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_http_media_scenarioai":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_http_media_leonardoai":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_http_media_jsonpub":
                document["document_type"] = "browser"
                syntax = "html"
            case "add_pdf_document_nchantdpdf":
                document["document_type"] = "pdf"
                syntax = "plain-text"
            case "add_files_document_nchantdfiles":
                document["document_type"] = "filesystem"
                syntax = "plain-text"
            case "add_image_document_nchantdimage":
                document["document_type"] = "image"
                syntax = "bytes"
                document["location"] = "external"
            case "image":
                document["document_type"] = "image"
                syntax = "bytes"
                document["location"] = "internal"
            case _:
                syntax = "plain-text"
                document["document_type"] = "note"
        document["syntax"] = syntax
        self.store.store_app_media(document)
        page_n = 0
        entry_n = 0
        media_fk = None
        logma.info(f"Document {document}")
        logma.info(f"Type {type(document)}")
        self.add_document_content_app(document, media_fk, page_n, entry_n, version, hash_, policy)
        if tab_new is True:
            logma.info(f"Add Tab {widget}")
            self.add_tab(name, pid, pos, widget, widgdata, document["did"], tab["type"], tabset, True, db)
        self.has_changed = True

    def add_document_content(self, document, media_fk=None, page_n=0, entry_n=0, version=0.0, hash_=None, policy=None):
        """"""
        context = ""
        logma.info(f"document {document}")
        logma.info(f"document type {type(document)}")
        content = document.get("content", {})
        if content == {}:
            content = document.get("data", {})
        if content is None:
            content = {}
        if isinstance(content, dict):
            logma.info(f"Content {content}")
            enc_content = encode64(j.dumps(content))
        elif isinstance(content, str):
            logma.info(f"Content {content[:500]}")
            enc_content = encode64(content)
        elif isinstance(content, bytes):
            enc_content = encode64(content)
        else:
            raise Exception(f"content is not a dict or a str or a bytes but is {type(content)}")
        payload = {
            "uuid": uuid(),  # each piece of media content is saved uniquely?
            "pUUID": document["did"],
            "media_fk": media_fk,
            "page": page_n,
            "entry": entry_n,
            "version": version,
            "hash": hash_,
            "content": enc_content,
            "context": context,
        }
        self.store.store_doc_media_content(payload)
        logma.info("Document Content Saved")
        return self

    def add_document_content_app(
        self, document, media_fk=None, page_n=0, entry_n=0, version=0.0, hash_=None, policy=None
    ):
        """"""
        context = ""
        logma.info(f"document {document}")
        logma.info(f"document type {type(document)}")
        content = document.get("content", {})
        if content == {}:
            content = document.get("data", {})
        if content is None:
            content = {}
        if isinstance(content, dict):
            logma.info(f"Content {content}")
            enc_content = encode64(j.dumps(content))
        elif isinstance(content, str):
            logma.info(f"Content {content[:500]}")
            enc_content = encode64(content)
        elif isinstance(content, bytes):
            enc_content = encode64(content)
        else:
            raise Exception(f"content is not a dict or a str or a bytes but is {type(content)}")
        payload = {
            "uuid": uuid(),  # each piece of media content is saved uniquely?
            "pUUID": document["did"],
            "media_fk": media_fk,
            "page": page_n,
            "entry": entry_n,
            "version": version,
            "hash": hash_,
            "content": enc_content,
            "context": context,
        }
        logma.info(f"Payload {payload}")
        self.store.store_app_media_content(payload)
        return self

    def add_node(self, name, ntype, pid, pos, parameters=None, tabset=None, return_node=False):
        """"""
        node = super().add_node(name, ntype, pid, pos, parameters, tabset, return_node)
        self.has_changed = True
        return node

    def add_node_app(self, name, ntype, pid, pos, parameters=None, tabset=None, return_node=False):
        """"""
        node = super().add_node(name, ntype, pid, pos, parameters, tabset, return_node)
        self.has_changed = True
        return node

    def add_note(self, document, pid, pos, tabset="center", db="db"):
        """"""
        # add document
        if isinstance(document, PyfficeDocument):
            note = document.to_dict()
            note["widget"] = "NchantdOfficeNote"
            note["type"] = "note"
            note["pid"] = pid
            note["position"] = pos
            note["noteset"] = "center"
            note["context"] = {}
            note["version"] = 0
            note["hash"] = ""
            note["policy_fk"] = None
            note["content"] = []
            # self.store.store_doc_media(note)
        else:
            note = document
        logma.info(f"Note {note}")
        name = note["name"]
        widget = note["widget"]
        widgdata = {"name": name, "type": "tag", "focus": "userapp"}
        location = None
        tags = ""
        context = ""
        version = 0.0
        hash_ = ""
        policy = None
        document = {
            "did": uuid(),
            "document_type": "note",
            "syntax": note.get("syntax", "plain-text"),
            "name": name,
            "file_name": note.get("file_path", ""),
            "description": "",
            "path": "",
            "location": "internal",
            "encoding": "utf-8",
            "tags": tags,
            "context": context,
            "version": version,
            "hash": hash_,
            "policy": policy,
        }
        self.store.store_doc_media(document)
        page_n = 0
        entry_n = 0
        media_fk = None
        logma.info(f"Tab {note.get("content", "")}")
        content = {
            "uuid": uuid(),
            "pUUID": document["did"],
            "media_fk": media_fk,
            "page": page_n,
            "entry": entry_n,
            "version": version,
            "hash": hash_,
            "content": encode64(j.dumps(note.get("content", {}))),
            "context": context,
        }
        self.store.store_doc_media_content(content)
        # self.add_document_content(document, media_fk, page_n, entry_n, version, hash_, policy)
        return self

    def add_note_app(self, document, pid, pos, tabset="center"):
        """"""
        # add document
        if isinstance(document, PyfficeDocument):
            note = document.to_dict()
            note["widget"] = "NchantdOfficeNote"
            note["type"] = "note"
            note["pid"] = pid
            note["position"] = pos
            note["noteset"] = "center"
            note["context"] = {}
            note["version"] = 0
            note["hash"] = ""
            note["policy_fk"] = None
            note["content"] = []
            # self.store.store_doc_media(note)
        else:
            note = document
        logma.info(f"Note {note}")
        name = note["name"]
        widget = note["widget"]
        widgdata = {"name": name, "type": "tag", "focus": "userapp"}
        location = None
        tags = ""
        context = ""
        version = 0.0
        hash_ = ""
        policy = None
        document = {
            "did": uuid(),
            "document_type": "note",
            "syntax": note.get("syntax", "plain-text"),
            "name": name,
            "file_name": note.get("file_path", ""),
            "description": "",
            "path": "",
            "location": "internal",
            "encoding": "utf-8",
            "tags": tags,
            "context": context,
            "version": version,
            "hash": hash_,
            "policy": policy,
        }
        self.store.store_doc_media(document)
        page_n = 0
        entry_n = 0
        media_fk = None
        logma.info(f"Tab {note.get("content", "")}")
        content = {
            "uuid": uuid(),
            "pUUID": document["did"],
            "media_fk": media_fk,
            "page": page_n,
            "entry": entry_n,
            "version": version,
            "hash": hash_,
            "content": encode64(j.dumps(note.get("content", {}))),
            "context": context,
        }
        self.store.store_doc_media_content(content)
        # self.add_document_content(
        #     document, media_fk, page_n, entry_n, version, hash_, policy
        # )  # TODO: does this need to be moved to the app set of tables
        return self

    def add_tab(
        self, name, pid, pos, widget, widgdata=None, did=None, doc_type=None, tabset=None, in_doc=True, db="db"
    ):
        """
        Add a tab to the application model.

        :param name: Tab name.
        :param pid: Parent node ID.
        :param pos: Tab position.
        :param widget: Widget to display in the tab.
        :param widgdata: Initial data for the widget.
        :param did: Document ID.
        :param doc_type: Document type.
        :param tabset: Target tab set.
        :param in_doc: Whether the tab is part of a document.
        :param db: Database alias.
        :return: Created tab object.
        """
        tab = super().add_tab(name, pid, pos, widget, widgdata, did, doc_type, tabset, in_doc, db)
        self.has_changed = True
        return tab

    def add_day_node(self, day, month, year, pid=None):
        """"""
        self.get_today_node()
        year_df = self.nodes[self.nodes["name_txt"] == year]
        if year_df.empty:
            pid = self.create_nodeset_year(year)
            self.nodes = self.get_nodes()
        else:
            pid = year_df["nid_txt"].values[0]
        year_df = self.nodes[self.nodes["pid_txt"] == pid]
        month_df = year_df[year_df["name_txt"] == month]
        if month_df.empty:
            pid = self.create_nodeset_month(month, year, pid)
            self.nodes = self.get_nodes()
        else:
            pid = month_df["nid_txt"].values[0]
        month_df = self.nodes[self.nodes["pid_txt"] == pid]
        day_df = month_df[month_df["name_txt"] == day]
        if day_df.empty:
            pos = month_df["position_int"].astype(int).max() + 1
            if isnan(pos):
                pos = 1
            pid, row = self.store.store_app_tree_node(day, "daynode", pid, pos, {"focus": "userapp"})
            self.nodes = self.get_nodes()
            self.create_tabset_day(pid)
            self.has_changed = True
            return pid

    def add_week_tabs(self):
        """
        when adding a day tab add the week that day is in as a tab to the month node if it doesnt exist some weeks will
        be duplicated across months - label them based on their week number of year
        :return:
        """
        widget = "nchantrs.widgets.calendars.timelines.NchantdWeeklyDashboard"
        widgdata = {}
        # TODO: Define pid properly or pass it as an argument
        # self.parent.app.view.panes["center"].model.add_tab("Weekly Dashboard", pid, 1, widget, widgdata)
        self.has_changed = True
        return self

    def backup(self):
        """Backup the application database."""
        self.store.backup_database()
        return self

    # def auto_save(self):
    #     """"""
    #     # will need to access each changed document/tab and each new node and tab to ensure they are saved
    #     # if I add a save on defocus then only the last accessed tab needs to be saved
    #     # self.app.model.save()
    #     # self.app.model.backup()
    #     super().auto_save()
    #     return self

    def change_node_parent(self, pid):
        """"""
        data = {"table": {"doc_tree_node": {"data": {"pid_txt": pid}}}}
        self.store.update_record(data, "nid_txt", self.get_current_node().nid)
        return self

    def change_node_position(self, position):
        """"""
        data = {"table": {"doc_tree_node": {"data": {"position_int": position}}}}
        self.store.update_record(data, "nid_txt", self.get_current_node().nid)
        return self

    def change_tab_parent(self, pid):
        """"""
        data = {"table": {"doc_tab": {"data": {"pid_txt": pid}}}}
        self.store.update_record(data, "nid_txt", self.get_current_node().nid)
        return self

    def change_tab_position(self, position):
        """"""
        data = {"table": {"doc_tab": {"data": {"position_int": position}}}}
        self.store.update_record(data, "nid_txt", self.get_current_node().nid)
        return self

    def close_application(self):
        """"""
        if self.has_changed is True:
            self.auto_save()
        self.store.compact_database()
        return self

    def convert_database(self, version_from, version_to):
        """"""
        super().convert_database(version_from, version_to)
        self.has_changed = True
        # handle data updates
        return self

    def convert_db_to_tab_doc(self):
        """"""

    def convert_db_to_journal(self, document_):
        """"""
        document = {}
        document["data"] = decode64(document_["content_enc64_txt"])
        logma.info(f"Content {document}")
        try:
            document["data"] = j.loads(document["data"])
        except Exception:
            pass
        logma.info(f"Document_ {document_}")
        logma.info(f"Document {document}")
        document["did"] = document_["did"]
        document["name"] = document_["name_txt"]
        document["path"] = document_["path_txt"]
        document["filename"] = document_["filename_txt"]
        document["syntax"] = document_["syntax_txt"]
        # document["position"] = document_["position_int"]
        # document["document_type"] = document_["document_type_txt"]
        # document["readonly"] = document_["readonly_bit"]
        # document["editable"] = document_["editable_bit"]
        # document["visible"] = document_["visible_bit"]
        # document["moveable"] = document_["moveable_bit"]
        # document["tid"] = document_["tid_txt"]
        # document["pid"] = document_["pid_txt"]
        # document["widget"] = document_["widget_txt"]
        # document["widgdata"] = document_["widgdata_dict"]
        document["compatibility"] = document_.get("compatibility_txt", "pyffice")
        document["version"] = document_.get("content_version_int", 0)
        # document["tab_type"] = document_.get("tab_type_txt", "custom_widget")
        document["document_type"] = document_.get("document_type_txt", None)
        document["location"] = document_.get("store_location_txt", None)
        document["encoding"] = document_.get("encoding_txt", None)
        document["tags"] = document_.get("tags_dict", None)
        document["hash"] = document_.get("hash_txt", None)
        document["meta_data"] = self.convert_encoding(document_.get("meta_data_enc64_dict", None))
        document["policy_FK"] = document_.get("policy_FK", None)
        document["page"] = document_["page_int"]
        document["entry"] = document_["entry_int"]
        document["content_version"] = document_["content_version_int"]
        document["content_hash"] = document_["content_hash_txt"]
        document["content"] = self.convert_encoding(document_["content_enc64_txt"])
        return document

    def convert_encoding(self, entry):
        """"""
        if isinstance(entry, bytes):
            entry = decode64(entry)
        if isinstance(entry, str):
            entry = j.loads(entry)
        return entry

    def create_doc_media(self, document):
        """"""
        tags = ",".join(document.tags)
        hash_ = text_hashing_function(j.dumps(document.content))
        payload = [
            document.id,
            document.type,
            document.file_name,
            document.description,
            document.path,
            document.location,
            document.encoding,
            tags,
            document.context,
            document.version,
            hash_,
            document.policy_fk,
        ]
        self.store.store_doc_media()
        self.create_doc_media_content()
        self.has_changed = True
        return self

    def create_doc_media_content(self, document=None):
        """Create content records for a document media item."""
        if document is None:
            return self
        pages = []
        cnt = 0
        entry = 0
        version = 0
        content_part = ""
        context = ""
        payload = []
        hash_ = text_hashing_function(document.content)
        for page in pages:
            payload.append([uuid(), document.id, cnt, entry, version, hash_, content_part, context])
            cnt += 1
        self.store.store_doc_media_content(payload)
        # self.add_document_content(document, None, cnt, entry, version, hash_, None)
        self.has_changed = True
        return self

    def create_new_instance(self):
        """"""
        super().create_new_instance()
        return self

    def create_nodeset_month(self, month, year, pid=None):
        """"""
        year_df = self.nodes[self.nodes["name_txt"] == year]
        if year_df.empty:
            pid = self.create_nodeset_year(year, pid)
            self.nodes = self.get_nodes()
            year_df = self.nodes[self.nodes["name_txt"] == year]
        else:
            pid = year_df["nid_txt"].values[0]
        month_df = year_df[year_df["name_txt"] == month]
        if month_df.empty:
            pos = year_df[year_df["pid_txt"] == pid]["position_int"].astype(int).max() + 1
            if isnan(pos):
                pos = 1
            pid, row = self.store.store_app_tree_node(month, "monthnode", pid, pos, {"focus": "userapp"})
        self.create_month_tabset(pid)
        self.has_changed = True
        return pid

    def create_nodeset_year(self, year, pid=None):
        """"""
        if pid is None:
            pid = self.today_nid
        pos = self.nodes[self.nodes["pid_txt"] == pid]["position_int"].astype(int).max() + 1
        if isnan(pos):
            pos = 1
        logma.info(f"Year {year}")
        pid, row = self.store.store_app_tree_node(year, "yearnode", pid, pos, {"focus": "userapp"})
        self.create_tabset_year(pid)
        self.has_changed = True
        return pid

    def create_tabset_day(self, pid, day=None):
        """"""
        if day is None:
            day = self.store.time.get_day(None, "%d - %A")
        widget = "nchantrs.widgets.calendars.days.NchantdDayCalendar"
        widgdata = {}
        self.add_tab(str(day), pid, 0, widget, widgdata, uuid(), "day", "center", in_doc=False)
        widget = "nchantrs.widgets.calendars.days.NchantdDayJournal"
        widgdata = {}
        self.add_tab("Journal", pid, 1, widget, widgdata, uuid(), "day", "center", in_doc=False)
        self.has_changed = True
        return self

    def create_month_tabset(self, pid, month=None):
        """
        Create a set of tabs for the Month
        List of Major Events/Sechedule Events for the month
        if it is a month of the current year
            - user monthly appts?
        :param pid:
        :return:
        """
        if month is None:
            month = self.store.time.get_month(None, "%B")
        widget = "nchantrs.widgets.calendars.months.NchantdMonthDashboard"
        widgdata = {}
        self.add_tab(month, pid, 0, widget, widgdata, uuid(), "month", "center", in_doc=False)
        widget = "nchantrs.widgets.calendars.months.NchantdMonthlyJournal"
        widgdata = {}
        self.add_tab("Journal", pid, 1, widget, widgdata, uuid(), "month", "center", in_doc=False)
        self.has_changed = True
        return self

    def create_tabset_year(self, pid, year=None):
        """
        #Create a set of tabs for the Year
        List of Major Events/Scheduled Events for the year
        Calendar of the year
        :return:
        """
        if year is None:
            year = self.store.time.get_year()
        # TODO: need to refactor how the widget is added to the database using the app_document_type registry
        widget = "nchantrs.widgets.calendars.years.NchantdYearCalendar"
        widgdata = {}
        self.add_tab(year, pid, 0, widget, widgdata, uuid(), "year", "center", in_doc=False)
        widget = "nchantrs.widgets.calendars.years.NchantdYearlyJournal"
        widgdata = {}
        self.add_tab("Journal", pid, 1, widget, widgdata, uuid(), "year", "center", in_doc=False)
        self.has_changed = True
        return self

    def delete_document(self, did):
        """"""
        logma.info(f"Document {did} will be deleted")
        pk = self.store.delete_record("doc_media", uuid=did, column="did")
        # raise Exception()
        self.store.delete_record("doc_media_content", uuid=did, column="pUUID")
        cfg = {"did": did, "doc_media_pk": pk}
        self.store_event("NONACTIVE", "DeleteDocument", cfg)
        self.has_changed = True
        return self

    def delete_node(self, node):
        """"""
        super().delete_node(node)
        cfg = {"nid": node.nid}
        self.store_event("CloseNode", cfg)
        return self

    def delete_note(self, note):
        """"""
        self.delete_document(note.document.did)
        return self

    def delete_tab(self, tab):
        """"""
        logma.info(f"Tab will be deleted {tab.tid}")
        cfg = {}
        # self.store_event("CloseTab", cfg)
        self.has_changed = True
        self.delete_document(tab.document.did)
        super().delete_tab(uuid=tab.tid)
        return self

    def duplicate_node(self):
        """"""

    def duplicate_tab(self):
        """"""

    def get_available_services(self):
        """"""
        cfg = {"WHERE": {"IN": {"file_type_txt": ["api"]}}}
        df = self.store.get_view_documents_all(cfg)
        return df

    def get_browse_history(self, limit=100, db="db"):
        """"""
        table = "vw_media"
        filters = {"WHERE": {"EQUAL": {"file_type_txt": "browse_history"}}, "LIMIT": limit}
        return self.get_table(table, filters, db)

    def get_document(self, doc_action=None, did=None, db="db"):
        """"""
        if doc_action is not None:
            cfg = {"WHERE": {"EQUAL": {"document_txt": doc_action}, "NOT IN": {"file_type_txt": ["api"]}}}
        elif did is not None:
            cfg = {"WHERE": {"EQUAL": {"doc_media_FK": did}}}
        else:
            raise Exception("No Document Action or Document ID Provided")
        df = self.store.get_view_documents_all(cfg)
        return df

    def get_documents(self, node, tabset):
        """"""
        if node is None:
            return DataFrame()
        table = "vw_tab_document"
        filters = {"WHERE": {"IN": {"pid_txt": [node], "tabset_type_txt": [tabset]}}}
        try:
            df = self.store.get_table(table, filters)
            return df if df is not None else DataFrame()
        except Exception as e:
            logma.warning(f"Error getting documents for node {node}: {e}")
            return DataFrame()

    def get_document_type(self, action_code):
        """"""
        if action_code is None:
            return None
        cfg = {"WHERE": {"EQUAL": {"action_txt": action_code}}}
        df = self.store.get_view_documents_all(cfg)
        return df.iloc[0] if not df.empty else None

    def get_document_types(self, registered=False, quick_launch=False):
        """"""
        cfg = {"WHERE": {"NOT IN": {"document_txt": ["api"]}}}
        if quick_launch is True:
            cfg["WHERE"]["EQUAL"] = {"quick_launch_bit": 1}
        if registered is True:
            cfg["WHERE"]["EQUAL"] = {"registered_bit": 1}
        df = self.store.get_view_documents_all(cfg)
        return df

    def get_document_all(self, doc_action):
        """"""
        cfg = {"WHERE": {"EQUAL": {"document_txt": doc_action}}}
        df = self.store.get_view_documents_all(cfg)
        return df

    def get_link(self, name):
        """"""
        link = self.store.get_view_link(name)
        return link

    def get_link_last_affiliate_update(self):
        """"""
        cfg = {"WHERE": {"EQUAL": {"eventtype_txt": "affiliate_update"}}}
        df = self.store.get_app_event(cfg)
        if df.empty:
            return None
        df.sort_values(by="MODON_DTTM", inplace=True)
        record = df.to_dict("records")[0]
        return record

    def get_links(self):
        """"""
        return self

    def get_node_name(self):
        """"""
        return self

    def get_node(self, nid):
        """"""
        # TODO this likely needs routed through the tree not sure the issue

    def get_profiles(self):
        """"""
        profiles = self.store.get_app_profile()["profile_txt"].values.tolist()
        logma.info(f"Profiles {profiles}")
        return profiles

    def get_recent_files(self, recent_files_n=50, db="db"):
        """
        will need to return recent Nchantrs Based Files associated with the
        provided applicationNCD

        check applicationNCD config for application setup
        then get all recent files up to x

        :return:
        """

    def get_rss_feeds(self):
        """"""
        return self.store.get_links(type_="rss_feed")

    def get_rss_entries(self):
        """"""
        #        self.mole.collect("rss")
        df = self.store.get_cache("ds_recent_rss_entries")
        if df is None:
            return None
        if df.empty:
            return None
        # df["published_dttm"] = df["published_dttm"].apply(lambda x: parser.parse(x).isoformat())
        # df = df[df["published_dttm"] == dt.datetime.now().date() - 3]#TODO convert to correct formats
        df.sort_values(by=["published_dttm"])
        logma.info(f"Store RSS Feeds {df.head()}")
        self.store_rss_entries(df)
        return df

    def get_settings(self, filter=None, db="db"):
        """"""
        table = "vw_settings"
        cfg = {"WHERE": {"EQUAL": {"key_txt": f"{filter}"}}}
        df = self.store.get_table(table, cfg, db)
        logma.info(f"DF {df}")
        df = df.sort_values(by=["table_txt", "key_txt", "label_txt", "value_txt", "is_default_bit", "MODON_DTTM"])
        return df

    def get_service(self, doc_action):
        """"""
        cfg = {"WHERE": {"EQUAL": {"document_txt": doc_action}, "IN": {"file_type_txt": ["api"]}}}
        df = self.store.get_view_documents_all(cfg)
        return df

    def get_sources(self):
        """"""
        sources = self.store.get_active_sources()
        df = DataFrame(self.config.dikt.get("sources", []), columns=list(sources.columns))
        sources = concat([sources, df])
        return sources

    def get_supported_os(self):
        """"""
        table = "vw_supported_os"
        params = {"table": [table]}
        rdr = self.docs["db"].read(params)
        df = next(rdr).dikt[table]["df"]
        # convert df to list of us using the columns key_text and option_txt
        for row in df.to_dict(records=True):
            for version in row["option_txt"].split(","):
                slug = kahndor.slugify(f"{row['key_txt']}_{version}")
                self.supported_os.append(slug)
        return self

    def get_urls(self, tag=None):
        """return a simple list of urls using the given criteria"""
        return []

    def get_tab_documents(self, node, tabset="center"):
        """"""
        table = "vw_tab_document"
        if node is None:
            return None
        if tabset == "right":
            filters = {"WHERE": {"IN": {"tabset_type_txt": ["right"]}}}
        else:
            filters = {"WHERE": {"IN": {"pid_txt": [node], "tabset_type_txt": [tabset]}}}
        filters["ORDER"] = [5]
        return self.store.get_table(table, filters)

    def get_tab_name(self):
        """"""
        return self

    def get_tab_set(self, tag):
        """"""
        table = "app_tab_set"
        cfg = {"WHERE": {"EQUAL": {"tag_txt": tag}}}
        return self.get_table(table, cfg)

    def get_today_node(self):
        """"""
        self.today_nid = "067ce332-8864-7d0b-8000-bfd314a580cc"
        return self.get_node(self.today_nid)

    def get_view_document_content(self, document_type, uuid=None, db="db"):
        """"""
        table = "vw_document"
        filters = {"WHERE": {"EQUAL": {"file_type_txt": document_type}}}
        if uuid is not None:
            filters["WHERE"]["EQUAL"]["UUID"] = uuid
        else:
            filters["LIMIT"] = 1
        document_data = self.get_table(table, filters, db)
        return document_data

    def get_view_journal(self, cfg):
        """"""
        document = self.store.get_view_journal(cfg).to_dict(orient="records")
        if len(document) == 0:
            did = uuid()
            pid = "0"
            pos = 0
            widget = "journal"
            widgdata = {}
            doc_type = "journal"
            tabset = "center"
            db = "db"
            document = {
                "did": did,
                "name": "Journal",
                "compatibility": "pyffice",
                "type": "journal",
                "syntax": "plain-text",
                "description": "internal",
                "store_location": "",
                "encoding": "utf-8",
                "meta_data": {},
                "widget": "",
            }
            logma.info(f"Journal Document Created: {document}")
            self.add_document_app(document, did, pid, pos, widget, widgdata, doc_type, tabset, db, False)
            document = self.store.get_view_journal(cfg).to_dict(orient="records")
        return self.convert_db_to_journal(document[0])

    def init_mole(self, db="db"):
        """"""
        self.mole.set_storage_path(self.store_rss_entries)
        # self.mole.load_feeds_list("rss")
        # This is getting any new feeds from the perspective of the NchantdApplication those feeds would come from the
        # WorldBridgeService
        # new_feeds = self.get_rss_feeds()
        # logma.info(f"New RSS Feeds {new_feeds}")
        # if new_feeds is None:
        #     raise Exception("No new feeds")
        # new_feeds = new_feeds["url_ltxt"].tolist()
        # if isinstance(self.mole.feeds, DataFrame):
        #     df = DataFrame([x for x in self.mole.feeds["url"].values.tolist() if x not in new_feeds], columns=["url"])
        # elif isinstance(self.mole.feeds, list):
        #     df = DataFrame([x for x in self.mole.feeds if x not in new_feeds], columns=["url"])
        # elif isinstance(self.mole.feeds, dict):
        #     raise Exception(f"Unknown feeds type {self.mole.feeds}")
        # else:
        #     raise Exception(f"Unknown feeds type {self.mole.feeds}")
        # self.store_rss_feeds(df)
        return self

    def initialize_application(self):
        """"""
        last_affilate_update_dttm = self.get_link_last_affiliate_update()
        update_affilate_links(self, last_affilate_update_dttm)
        super().initialize_application()
        # self.store.create_virtual_table() #TODO: relocat
        return self

    def import_cherrytree(self, file_path):
        """Pyffice doesnt' have a native direct overlay document for cherrytree as it is distributed Scripts, etc within
        NchantdOffice"""
        pid = self.get_current_node().nid
        logma.info(f"File Path {file_path}")
        cfg = {"document": {"file_path": file_path}}
        cherrytree = self.codex.import_cherrytree(cfg)
        pos = 0
        for node in cherrytree.nodes:
            self.import_cherrytree_nodes(node, pid, pos)
            pos += 1
        self.app.view.panes["left"].tree.refresh()

    def import_cherrytree_node(self, node, pid=None, pos=0):
        """"""
        if pid is None:
            pid = "0"
        name = node["name"]
        ntype = "usernode"
        parameters = {"name": name, "type": ntype, "parent_nid": pid, "position": pos}
        pid = self.add_node(name, ntype, pid, pos, parameters, "center")
        return pid

    def import_cherrytree_nodes(self, node, pid, pos):
        """"""
        pid = self.import_cherrytree_node(node, pid, pos)
        self.import_cherrytree_tabs(node, pid)
        for child in node["nodes"]:
            self.import_cherrytree_nodes(child, pid, pos)
            pos += 1

    def import_cherrytree_tabs(self, node, pid, pos=0):
        """"""
        logma.info(f"Tabs {node['tabs']}")
        for tab in node["tabs"]:
            logma.info(f"Tab {tab["name"]}")
            logma.info(f"Text {tab['rich_text']}")
            # TODO change this so that a tab code, images and tables
            tab["content"] = tab["rich_text"].get(
                "data", tab["rich_text"].get("unit", {})
            )  # how to store content universally?
            logma.info(f"Content {tab['content']}")
            tab["uuid"] = tab["unique_id"]
            logma.info(f"Tab Type {tab['type']}")
            # tab["widget"] = lookup_widget(tab["type"])
            tab["widget"] = self.app.model.get_document_type(tab["type"]).get("widget_txt", None)
            tab["did"] = uuid()
            self.add_document(tab, tab["did"], pid, pos)
        return self

    def import_nchantdoffice(self, file_path):
        """"""
        # pid = self.get_current_node().nid
        # cloak = NchantdOfficeCloakModel()
        # db = connect(file_path)

    def import_nchantdoffice_node(self, node, pid=None, pos=0):
        """"""

    def import_nchantdoffice_nodes(self, node, pid, pos):
        """"""

    def import_nchantdoffice_tabs(self, node, pid, pos=0):
        """"""

    def import_filetree(self, file):
        """"""
        # each directory becomes a node
        # each file becomes a tab
        # limit depth
        # limit size?
        if file is not None:
            if exists(file):
                pass
        return self

    def import_image(self, file):
        """"""
        if file is not None:
            if exists(file):
                current_tab = self.get_current_tab()
                if current_tab.document.doc_type != "image":
                    logma.info(f"File Type {current_tab.document.file_type}")
                    logma.info(f"File Type {current_tab.document.doc_type}")
                    logma.info(f"Create New Tab for Document{file}")
                    document = self.codex.init_image({"file_path": file})
                    document.open_file()
                    self.add_document(document, self.get_current_node().nid, current_tab.pos + 1)
                else:
                    current_tab.open_file(file)
                    current_tab.save()
        return self

    def import_pdf(self, file):
        """"""
        if file is not None:
            if exists(file):
                current_tab = self.get_current_tab()
                if current_tab.document.doc_type != "pdf":
                    logma.info(f"File Type {current_tab.document.file_type}")
                    logma.info(f"File Type {current_tab.document.doc_type}")
                    logma.info(f"Create New Tab for Document{file}")
                    document = self.codex.init_pdf({"data": {"file_path": file}})
                    document.load_document()
                    document.open_file()
                    self.add_document(document, self.get_current_node().nid, current_tab.pos + 1)
                    # need to refresh the tabset
                else:
                    current_tab.open_file(file)
                    # current_tab.save()
        return self

    def import_sessions(self, file):
        """"""
        if file is not None:
            if exists(file):
                pass
        return self

    def import_web_sessions(self, file):
        """Import web browser sessions from a file."""
        if file is not None and exists(file):
            # TODO: Implement session parsing
            pass
        return self

    def import_text(self, file):
        """"""
        if file is not None:
            if exists(file):
                current_tab = self.get_current_tab()
                if current_tab.document.doc_type != "script":
                    logma.info(f"File Type {current_tab.document.file_type}")
                    logma.info(f"File Type {current_tab.document.doc_type}")
                    logma.info(f"Create New Tab for Document{file}")
                    document = self.codex.init_script({"file_path": file})
                    current_tab.open_file()
                    # document.load_document()
                    self.add_document(document, self.get_current_node().nid, current_tab.pos + 1)
                else:
                    logma.info(f"Load Document to existing tab {file}")
                    # current_tab.document.load_document()
                    current_tab.open_file(file)
                    current_tab.save()
                    # current_tab.document.set_file_format = "python"
                    # current_tab.populate_document()
        return self

    # TODO: add import of things like notion and evernote in the future
    def register_document(self, document_type, actions):
        """"""
        # Store action using proper store method
        if isinstance(actions, list):
            for action in actions:
                self.store._store("app_action", [action])
        else:
            self.store._store("app_action", [actions])
        # Update document type registration using proper store method
        self.store.update_record(
            {"table": {"app_document_type": {"data": {"registered_bit": 1}}}},
            "document_type_txt",
            document_type
        )
        # Refresh registered documents list
        self.parent.model.registered_documents = self.get_document_types(registered=True)

    def remove_document(self, uuid):
        """"""
        document = self.get_document(uuid)
        self._delete("doc_media", {"UUID": uuid})
        self._delete("doc_media_content", {"parent_FK": document["doc_media_FK"][0]})
        return True

    def remove_document_entry(self, uuid):
        """"""
        page_n, entry_n = self.archive_document_entry(uuid)
        return page_n, entry_n

    def save_config_document_types(self):
        """Save document type configuration."""
        # TODO: Implement this method when the required 'document' object is available.
        return self

    def save_config_document(self):
        """"""

    def send_notification(self):
        """send notification of crash to service for trouble shooting and tracking
        TODO 20240804: check to see if sending external notifications is approved
        """

    def set_instance(self, instance):
        """"""
        self.active_instance = instance
        self.has_changed = True
        return self

    def set_today(self):
        """
        Sets the current date as today and updates the action node if necessary.

        :param nid: The unique identifier of the action node.
        :return: None
        """
        if self.today != self.store.time.get_current_datetime_str():
            logma.info(f"Today {self.today} changed to {self.store.time.get_current_datetime_str()}")
            self.today = self.store.time.get_current_datetime_str()
            self.nodes = self.get_nodes()
            self.add_day_node(self.store.time.get_day(), self.store.time.get_month(), self.store.time.get_year())
            self.has_changed = True
        return self

    def split_document(self, data, format_=None, formula=None):
        """Split

        how to parse "DOCUMENT" into doc_media and doc_media_content
        NchantdOffices concept of a Document is a cohesive document typically analigous to a tab
        Pyffice concept of a Document is each interchangable unit but will try to change this to match NchantdOffice

        Ideally each "DOCUMENT" gets one entry per version into doc_media
        the content of that document are then broken up and sent to doc_media_content

        """
        if isinstance(data, list):
            if format_ is None:
                format_ = [[] for x in range(len(data))]
            if formula is None:
                formula = [[] for x in range(len(data))]
            num_cols = len(data[0])
            max_size = 1000
            max_rows = max_size / num_cols
            if len(data) > max_rows:
                for i in range(len(data) - max_rows + 1):
                    yield i, (data[i : i + max_rows], format_[i : i + max_rows], formula[i : i + max_rows])
        else:
            raise Exception(f"data object not recognized {type(data)}")
        yield None, None

    def store_document(self, pydoc):
        """
        :param document:
        :return:
        """
        # logma.info(f"Document {pydoc.to_dict()}")
        if hasattr(pydoc, "is_changed") and pydoc.is_changed is False:
            return pydoc
        # check if content or metadata has changed
        # check version of current document
        # increment version based on overall version count...needs a check out process eventually
        # initial is just used as long term undo
        # TODO: increment version
        # pydoc.increment_version()
        # how to address content versioning
        self.add_document_content(pydoc.to_dict(), version=pydoc.version)
        return pydoc

    def store_event(self, state, action, cfg=None, db="db"):
        """"""
        if cfg is None:
            cfg = {}
        cfg["action"] = action
        self.store.store_app_event(state, action, cfg, db)
        return self

    def store_instance(self, instance):
        """"""
        self.instance = instance
        self.store.store_app_instance(instance)
        return self

    def store_instances(self):
        """"""
        for instance in self.instances:
            self.store_instance(instance)
        return self

    def store_node(self):
        """"""
        return self

    def store_rss_feeds(self, df, how=None):
        """"""
        # need to convert df to document format for rss feed storage
        self.store.store_link(df["url"].values.tolist())

    def store_rss_entries(self, df, how="append"):
        """"""
        if how == "append":
            self.append_cache("ds_recent_rss_entries", df)
        elif how == "override":
            self.store_cache("ds_recent_rss_entries", df)
        else:
            raise Exception(f"how {how} not recognized")
        return True

    def store_settings(self):
        """"""
        return self

    def store_tab(self):
        """"""
        return self


class NchantdOfficeStore(NchantdStore):
    """"""

    EXTENSION = ".pyof"

    def __init__(self, name, parent=None, cfg=None):
        """"""
        self.name = name.lower().replace(" ", "")  # "nchantdoffice"
        # this controls the location of the database storage on the local drive
        super().__init__(self.name, parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeStore"))
        self.parent = parent
        self.app = self.parent.app
        if parent is not None:
            self.config.override(parent.config)
        self.config.override(cfg)

        if self.app.agent_manager is None:
            return
        agent = self.app.agent_manager.assign_agent(self.mole)
        cfg = {"process-in": "series"}
        agent.define_processing(cfg)
        task = {
            "0": {"method": "set_storage", "inputs": [self.store_rss_entries]},
            "1": {"method": "load_feeds_list", "inputs": ["rss"]},
            "2": {"method": "update_feeds", "inputs": ["rss", {"file": ""}]},
            "3": {"method": "collect", "inputs": ["rss", "ds_recent_rss_entries"]},
        }
        # agent.assign_task(task)

    def convert_database(self, version_from, version_to):
        """"""
        super().convert_database(version_from, version_to)
        # Handle structure differences and switching to different database engines
        return self

    def create_virtual_table(self, db="db"):
        """Create a virtual table using the given schema."""
        if not self.docs[db].exists("vectorized_data"):
            return
        self.docs[db].execute(f"DROP TABLE IF EXISTS vectorized_data")
        DIMENSION = 384  # Adjust based on your embedding model
        self.docs[db].execute(f"""
            CREATE VIRTUAL TABLE vectorized_data USING vec0(
                id INTEGER PRIMARY KEY,
                version_txt TEXT,
                embedding float[{DIMENSION}],
                raw_data_txt TEXT,
                did_txt TEXT,
                CREBY_USER_FK,
                CREON_DTTM,
                MODON_USER_FK,
                MODON_DTTM,
                DELETE_BIT,
                ARCHIVE_BIT,
                ACTIVE_BIT
            );
        """)
        self.docs[db].commit()

    def get_application_documents(self):
        """"""
        data = {"contacts": {}, "settings": {}}
        return data

    def get_cache(self, key):
        """"""
        df = DataFrame()
        return df

    def get_view_browser_session(self, cfg, db="db"):
        """"""
        table = "vw_browser_session"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_browser_session_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_contact(self, cfg, db="db"):
        """"""
        table = "vw_contact"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_contact_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_document(self, cfg, db="db"):
        """"""
        table = "vw_document"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_document_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_document_app(self, cfg, db):
        """"""
        table = "vw_document_app"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_document_app_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_document_note(self, cfg, db):
        """"""
        table = "vw_document_note"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_document_note_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_journal(self, cfg=None):
        """"""
        table = "vw_journal"
        return self.get_table(table, cfg, "db")

    def get_view_chart_options(self, cfg, db="db"):
        """"""
        table = "vw_chart_options"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_chart_options_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_chart_types(self, cfg, db="db"):
        """"""
        table = "vw_chart_types"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_chart_types_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_documents_all(self, cfg=None):
        """"""
        table = "vw_app_document_type"
        params = {"table": [table]}
        rdr = self.docs["db"].read(params, cfg)
        df = next(rdr).dikt[table]["df"]
        df = df.sort_values(by=["sequence_int"])
        if df.empty:
            raise Exception("Documents Are Empty")
        return df

    def get_view_link(self, name=None, description=None, type_=None, tag=None, url=None, db="db"):
        """"""
        logma.info(f"Get View Link {name} {description} {type_} {tag} {url}")
        df = self.get_links(name, description, type_, tag, url, db)
        logma.info(f"DF {df}")
        link = None
        if not df.empty:
            link = df.to_dict(orient="records")[0]["url_ltxt"]
        return link

    def get_view_link_affiliates(self, url):
        """"""
        table = "vw_link_affiliate"
        cfg = {}
        cfg["WHERE"] = {"EQUAL": {"url_ltxt": url}}
        df = self.get_table(table, cfg)
        logma.info(f"Store Affiliates {df.head()}")
        df = df.sort_values(by=["name_txt", "type_txt"])  # TODO need to determine version handling etc
        return df

    def get_view_link_affiliate(self, cfg, db="db"):
        """"""
        table = "vw_link_affiliate"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_link_affiliate_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_browser(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_browser"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_browser_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_calendar(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_calendar"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_calendar_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_chart(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_chart"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_chart_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_files(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_files"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_files_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_form(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_form"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_form_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_image(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_image"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_image_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_matrix(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_matrix"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_matrix_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_pdf(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_pdf"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_pdf_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_prompt(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_prompt"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_prompt_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_script(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_script"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_script_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_document_sketch(self, cfg, db="db"):
        """"""
        table = "vw_settings_document_sketch"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_document_sketch_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_settings_journal(self, cfg, db="db"):
        """"""
        table = "vw_settings_journal"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_settings_journal_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_sources(self, cfg, db="db"):
        """"""
        table = "vw_sources"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_sources_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_sources_available_(self, cfg, db="db"):
        """"""
        table = "vw_sources_available"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_sources_available_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def get_view_tab_document(self, cfg, db="db"):
        """"""
        table = "vw_tab_document"
        if self.instance is not None:
            if self.instance.is_independent:
                table = f"vwt_tab_document_{self.instance.alias}"
        return self.get_table(table, cfg, db)

    def store_doc_media(self, document, db="db", how="INSERT"):
        """
        Store document creates a new record in the database table doc_media representing a document.

        :param document: Dictionary containing document metadata.
        :param db: Database alias.
        :param how: Action to perform (INSERT, UPDATE, etc.).
        :return: Document ID.
        """
        return self.store_app_media(document, db, how, table="doc_media")

    def store_app_media(self, document, db="db", how="INSERT", table="app_media"):
        """
        Store application media creates a new record in the specified database table.

        :param document: Dictionary containing media metadata.
        :param db: Database alias.
        :param how: Action to perform (INSERT, UPDATE, etc.).
        :param table: Target database table.
        :return: Document ID.
        """
        if how not in ["INSERT", "UPDATE", "DEACTIVATE", "DELETE", "ARCHIVE"]:
            raise Exception(f"{how} is not supported.")

        payload = [
            [
                document["did"],
                document.get("compatibility", "pyffice"),
                document["document_type"],
                document["syntax"],
                document["name"],
                document["file_name"],
                document["description"],
                document["path"],
                document["location"],
                document["encoding"],
                "|".join(document["tags"]),
                document["version"],
                self.parent.instance.version,
                document["hash"],
                document["policy"],
                encode64(j.dumps(document.get("metadata", {}))),
            ]
        ]
        self._store(table, payload, db)
        return document["did"]

    def store_doc_media_content(self, content, db="db", how="INSERT"):
        """"""
        table = "doc_media_content"
        if how == "INSERT":
            payload = []
        elif how == "UPDATE":
            payload = [{}]
        elif how == "DEACTIVATE":
            payload = []
        elif how == "DELETE":
            payload = []
        elif how == "ARCHIVE":
            payload = []
        else:
            raise Exception(f"{how} is not supported.")
        payload = [
            [
                content["uuid"],
                content["pUUID"],
                content["page"],
                content["entry"],
                content["version"] + 1,
                content["hash"],
                content["content"],
                content["context"],
            ]
        ]
        # set delete for all but the largest 3 versions
        self._store(table, payload, db)
        # self._archive_versions(table, content["pUUID"], "pUUID", "UUID", 3)
        return content["uuid"]

    def update_document_entry(self, uuid, content, db="db"):
        """"""
        media_PK, page, entry = self.archive_media_content(uuid, db)
        uuid = self.store_document_entry(media_PK, content, page, entry)
        return uuid

    def update_document_entry_script(self, uuid, content):
        """"""
        page_n, entry_n = self.remove_document_entry_script(uuid)
        uuid = self.store_document_entry(page_n, entry_n, content)
        return uuid

    def _archive_versions(self, table, uuid, gcolumn="UUID", dcolumn="UUID", max_versions=3, db="db"):
        """"""
        df = self.get_table(table, {"WHERE": {"EQUAL": {gcolumn: uuid}}}, db)
        if not df.empty:
            logma.info(f"DF {df.head()}")
            df.sort_values(by=["version_int"], inplace=True)
            self._delete_by_uuid(table, df.tail(len(df) - max_versions)[dcolumn].values.tolist(), dcolumn, db)
        return self


class NchantdOfficeTabSetModel(NchantdTabSetModel):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTabSetModel"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.new_document = None
        self.show_add_tab = self.config.dikt.get("show_add_tab", False)
        self.tabsdata = None

    def initModel(self, create_objects=True):
        """"""
        self.tabsdata = []
        super().initModel(create_objects)
        return self

    def buildTabSet(self, node, tabset="center", toolbox=None):
        """"""
        if hasattr(self, "_building") and self._building:
            return self
        self._building = True
        active_tab_position = 0
        try:
            self.parent.blockSignals(True)
            self.parent.clear()
            self.tabsdata = []
            self.tab_widgets = []

            tabsdata = self.get_documents(node, tabset)
            tabsdata.sort_values(by=["position_int"], ascending=True, inplace=True)
            logma.info(f"Tabsdata {tabsdata}")
            if not tabsdata.empty:
                tabsdata = [self.convert_db_to_doc(tab) for tab in tabsdata.to_dict(orient="records")]
            else:
                tabsdata = []

            self.tabset = tabset
            self.current_node = node
            self.tabsdata = tabsdata

            # Lazy loading logic
            active_tab_position = node.parameters.get("active_tab_position", 0)
            # Ensure it's an integer and within bounds
            try:
                active_tab_position = int(active_tab_position)
            except (ValueError, TypeError):
                active_tab_position = 0

            if tabsdata:
                if active_tab_position >= len(tabsdata):
                    active_tab_position = 0

                for tabn, tab in enumerate(self.tabsdata):
                    if tabn == active_tab_position:
                        self.load_tab(tab, tabn, tabset, active_tab_position)
                    else:  # TODO: this supports lazy loading probably needs to be moved to nchantrs base library
                        # Create placeholder
                        from nchantrs.libraries import pyqt

                        dummy = pyqt.QWidget(self.parent)
                        dummy.dummy = True
                        dummy.toolbox_config = {}
                        dummy.position = tabn
                        dummy.name = tab.get("name", tab.get("name_txt", None))
                        _type = tab.get("tab_type", tab.get("tab_type_txt", "custom_widget"))
                        dummy.type = _type[-len(_type) + _type.rfind("_") + 1 :]
                        self.tab_widgets.insert(tabn, dummy)
                        self.parent.insertTab(tabn, dummy, dummy.name)

                self.parent.setCurrentIndex(active_tab_position)

            if self.show_add_tab or tabset == "center":
                logma.info(f"New Document {self.new_document}")
                if self.new_document is None:
                    self.new_document = NchantdOfficeDocumentsCatalog(self.parent, self.config)
                self.new_document.initWidget()
                self.new_document.position = len(self.tabsdata) + 1
                self.parent.addTab(self.new_document, " + ")

            # When building center pane, also build right pane tabs
            if tabset == "center" and hasattr(self.parent, "app"):
                right_pane = self.parent.app.view.panes.get("right")
                if right_pane and hasattr(right_pane, "model"):

                    logma.info("Building right pane tabs")
                    right_pane.model.buildTabSet(node, "right")
                    active_tab_position = 0

        finally:
            self.parent.blockSignals(False)
            if hasattr(self.parent, "on_tab_focus"):
                self.parent.on_tab_focus(active_tab_position)
            self._building = False
        return self

    def convert_db_to_doc(self, document_):
        """"""
        document = {}
        document["data"] = decode64(document_["content_enc64_txt"])
        try:
            document["data"] = j.loads(document["data"])
        except Exception:
            pass
        # logma.info(f"Document_ {document_}")
        # logma.info(f"Document {document}")
        document["did"] = document_["did_txt"]
        document["syntax"] = document_["syntax_txt"]
        document["name"] = document_["name_txt"]
        document["position"] = document_["position_int"]
        document["document_type"] = document_["document_type_txt"]
        document["readonly"] = document_["readonly_bit"]
        document["editable"] = document_["editable_bit"]
        document["visible"] = document_["visible_bit"]
        document["moveable"] = document_["moveable_bit"]
        document["tid"] = document_["tid_txt"]
        document["pid"] = document_["pid_txt"]
        document["widget"] = document_["widget_txt"]
        document["widgdata"] = document_["widgdata_dict"]
        document["version"] = document_.get("content_version_int", None)
        document["tab_type"] = document_.get("tab_type_txt", "custom_widget")
        document["document_type"] = document_.get("document_type_txt", None)
        document["location"] = document_.get("store_location_txt", None)
        document["encoding"] = document_.get("encoding_txt", None)
        document["tags"] = document_.get("tags_dict", None)
        document["hash"] = document_.get("hash_txt", None)
        document["meta_data"] = {"creon": document_["doc_CREON_DTTM"], "modon": document_["doc_MODON_DTTM"]}
        return document

    def defocus(self):
        """"""
        super().defocus()
        return self

    def get_documents(self, node, tabset):
        """"""
        if isinstance(node, int):
            nid = node
        else:
            nid = node.nid
        tab_docs = self.parent.app.model.get_tab_documents(nid, tabset)
        return tab_docs

    def load_tab(self, tab, tabn=0, tabset="center", active_tab_position=0):
        """"""
        # Workaround for bug in nchantrs.models.tabsetmodels.NchantdTabSetModel.load_tab
        # which uses 'tabn in self.tab_widgets' incorrectly for a list.
        if tabn < len(self.tab_widgets):
            # remove from parent QTabWidget
            self.parent.removeTab(tabn)
            # remove from our internal list so super().load_tab doesn't shift other tabs
            self.tab_widgets.pop(tabn)

        # super().load_tab calls self.load_widget, which we override.
        # Ensure we pass the converted document if needed, but nchantrs' load_tab
        # expects the 'tab' dict which it then passes to parse_widget_data.
        super().load_tab(tab, tabn, tabset, active_tab_position)
        return self

    def load_widget(self, cfg, tabset="center", document=None, tab_type="custom_widget"):
        """"""
        logma.info(f"Load Widget {cfg}")
        logma.info(f"Tabset {tabset}")
        logma.info(f"Document {document}")
        logma.info(f"Tab Type {tab_type}")

        # If document is not None, use it to populate cfg, similar to base load_widget
        if document:
            cfg["widget"] = document.get("widget", document.get("widget_txt", cfg.get("widget")))
            cfg["tid"] = document.get("tid", document.get("tid_txt", cfg.get("tid")))
            cfg["document"] = document

        # Workaround for KeyError: 'tab' in lookupWidget
        # This happens when 'widget' is not in cfg, and 'tab' is the first key.
        widget_name = cfg.get("widget")
        if (not widget_name) and "tab" in cfg:
            tab_data = cfg["tab"]
            widget_name = tab_data.get("widget", tab_data.get("widget_txt", None))

        if widget_name:
            # Rebuild cfg so the widget name is the FIRST key,
            # which is what nchantrs.widgets.widgets.lookupWidget expects:
            # registered_widget = lookupWidget(list(cfg.keys())[0])
            new_cfg = {widget_name: cfg.get(widget_name, {})}
            for k, v in cfg.items():
                if k != widget_name:
                    new_cfg[k] = v
            cfg = new_cfg
            cfg["widget"] = widget_name

        tabW = super().load_widget(cfg, tabset, document, tab_type)
        if hasattr(tabW, "initWidget"):
            tabW.initWidget()
        return tabW

    def set_focus(self):
        """"""
        super().set_focus()
        return self


class NchantdOfficeSettingsModel(NchantdModel):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdSettingsModel"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.security = {}
        self.storage = {}
        self.packages = {}
        self.theme = {}
        self.interface = {}
        self.nchantd_account = {}

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def change_user_password(self):
        """"""
        # verify old password
        # validate new password strength
        # check new password match

    def get_journal_focus_enable(self):
        """"""

    def get_show_settings_focus_enable(self):
        """"""

    def get_automation_enable(self):
        """"""

    def get_data_sources_enable(self):
        """"""

    def get_show_left_side_pane(self):
        """"""

    def get_show_quick_launch_toolbar(self):
        """"""

    def get_quick_launch_documents(self):
        """"""

    def get_show_document_launch_catalog(self):
        """"""

    def get_default_tab_enable(self):
        """"""

    def get_default_tab_select(self):
        """"""

    def get_always_refocus_right_side_enable(self):
        """"""

    def get_refocus_right_side_select(self):
        """"""

    def get_document_storage_default(self):
        """"""

    def get_document_delete_policy(self):
        """"""

    def get_document_name_convention_default(self):
        """"""

    def get_lock_screen_enable(self):
        """"""

    def get_lock_screen_timeout(self, value):
        """"""

    def get_lock_screen_pin_enable(self):
        """"""

    def get_package_enable(self):
        """"""

    def get_package_focus_enable(self):
        """"""

    def get_package_theme(self):
        """"""

    def get_theme(self):
        """"""

    def get_pro_edition(self):
        """"""
        # change tab focus to Nchantd Account tab

    def get_password_new_entry(self):
        """"""
        password = ""
        return password

    def get_password_new_confirm_entry(self):
        """"""
        password = ""
        return password

    def get_password_old_entry(self):
        """"""
        password = ""
        return password

    def get_lock_screen_enable(self):
        """"""
        enable = True
        return enable

    def get_lock_screen_timeout_select(self):
        """"""
        timeout = 0
        return timeout

    def get_lock_screen_pin_enable(self):
        """"""
        enable = True
        return enable

    def get_lock_screen_pin_entry(self):
        """"""
        pin = 1111
        return pin

    def load_settings(self):
        """"""

    def set_journal_focus_enable(self):
        """"""

    def set_show_settings_focus_enable(self):
        """"""

    def set_automation_enable(self):
        """"""

    def set_data_sources_enable(self):
        """"""

    def set_show_left_side_pane(self):
        """"""

    def set_show_quick_launch_toolbar(self):
        """"""

    def set_quick_launch_documents(self):
        """"""

    def set_show_document_launch_catalog(self):
        """"""

    def set_default_tab_enable(self):
        """"""

    def set_default_tab_select(self):
        """"""

    def set_always_refocus_right_side_enable(self):
        """"""

    def set_refocus_right_side_select(self):
        """"""

    def set_document_storage_default(self):
        """"""

    def set_document_delete_policy(self):
        """"""

    def set_document_name_convention_default(self):
        """"""

    def set_lock_screen_enable(self):
        """"""

    def set_lock_screen_timeout(self, value):
        """"""

    def set_lock_screen_pin_enable(self):
        """"""

    def set_package_enable(self):
        """"""

    def set_package_focus_enable(self):
        """"""

    def set_package_theme(self):
        """"""

    def set_theme(self):
        """"""

    def to_dict(self):
        """"""
        doc = {}
        return doc


class NchantdOfficeImportModel(NchantdModel):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeImportModel"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
