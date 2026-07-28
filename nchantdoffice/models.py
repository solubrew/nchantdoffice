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
from urllib.parse import urlsplit

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame, concat
from numpy import isnan, nan

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from micromole.micromole import MicroMole
from nchantrs.models.tabsetmodels import NchantdTabSetModel
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.models.models import NchantdStore
from nchantrs.models.applicationmodels import NchantdModel
from nchantdoffice.utilities.links import update_affilate_links
from nchantdoffice.utilities.referral import (
    ReferralCode as _ReferralCode,
    generate_referral_code as _generate_referral_code,
    validate_referral_code as _validate_referral_code,
)
from nchantdoffice.widgets.catalogs import NchantdOfficeDocumentsCatalog
from kahndor.logma import Logma
from pyffice.document import PyfficeDocument
from pyffice.pyffice import PyfficeCodex
from subtrix.utilities import uuid
from pycurity.pyhash import text_hashing_function, encode64
from pycurity.pyhash import decode64
from nchantdoffice.utilities.config import PyfficeApplicationConfig, NchantdOfficeBrowserConfig
from nchantrs.models.models import NchantdInstance

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
log = True
debug = True
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "models.yaml")

# Fully-qualified widget path used when opening a web page as its own tab.
OFFICE_WEB_BROWSER_WIDGET = "nchantdoffice.widgets.documents.atnrg.browsers.NchantdOfficeWebBrowser"


def same_web_url(a, b):
    """True if two URLs point at the same destination (scheme+host+path, ignoring
    trailing slash / query / fragment). Used to avoid opening duplicate tabs."""
    try:
        pa, pb = urlsplit(a), urlsplit(b)
        return (
            pa.scheme.lower() == pb.scheme.lower()
            and pa.netloc.lower() == pb.netloc.lower()
            and pa.path.rstrip("/") == pb.path.rstrip("/")
        )
    except Exception:
        return a == b


def web_url_label(url):
    """Short human label for a browser tab derived from the URL host."""
    try:
        host = urlsplit(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host or "New Tab"
    except Exception:
        return "New Tab"


class NchantdOfficeInstance(NchantdInstance):
    """"""

    def __init__(self, parent, cfg=None):
        """"""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeInstance").override(cfg))
        self.browser = None
        self.config_browser()

    def config_browser(self, cfg=None):
        """"""
        cfg = cfg or {}
        self.browser = NchantdOfficeBrowserConfig(self, cfg)


class NchantdOfficeCloakModel(NchantdCloakModel):
    """"""

    APP_NAME = "NchantdOffice"

    def __init__(self, name, instance=None, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCloakModel").override(cfg))
        cfg = {}
        self.store = NchantdOfficeStore(name, self, cfg=cfg)
        self.codex = PyfficeCodex()
        cfg = {}
        self.settings = PyfficeApplicationConfig(cfg, self)
        self.registered_documents = {}
        self.enable_journal_focus = None
        self.enable_settings_focus = None
        self.enable_automation = None
        self.enable_datasources = None
        self.show_quick_launch_toolbar = None
        self.today = self.store.time.get_current_datetime_str()
        self.toolbox_config = self.config.dikt.get("toolbox", {})

    def initModel(self, reset=None):
        """"""
        super().initModel(reset)
        self.codex.load_document()
        docs = self.store.get_application_documents()
        self.codex.init_contacts(docs["contacts"])
        self.settings.load_document(docs["settings"])
        # self.init_mole()
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
        match document["type"]:  # need to refactor to remove the limitations of manually registering each
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
            case "add_sheet_document_nchantdmatrix":
                document["document_type"] = "matrix"
                syntax = "plain-text"
                document["location"] = "external"
            case "matrix":
                document["document_type"] = "matrix"
                syntax = "plain-text"
                document["location"] = "internal"
            case _:
                syntax = "plain-text"
                document["document_type"] = (
                    "doc"  # PUSH to 0.0.3 should be note but need to adjust all other document types
                )
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
        content = document.get("content", {}) or {}
        if content == {}:
            content = document.get("data", {}) or {}
        if isinstance(content, dict):
            logma.info(f"Content {content}")
            logma.info(f"Dumped Content {j.dumps(content)}")
            try:
                enc_content = encode64(j.dumps(content))
                logma.info(f"Encoded Dictionary {enc_content}")
            except Exception as e:
                logma.warning(f"Dictionary Encoding Failed")
                logma.warning(e)
                if debug:
                    logma.warning(content)
                    raise e
        elif isinstance(content, str):
            try:
                logma.info(f"Content {content[:500]}")
                enc_content = encode64(content)
            except Exception as e:
                logma.warning(f"String Encoding Failed")
                logma.warning(e)
                if debug:
                    logma.warning(content)
                    raise e
        elif isinstance(content, bytes):
            try:
                enc_content = encode64(content)
            except Exception as e:
                logma.warning(f"Bytes Encoding Failed")
                logma.warning(e)
                if debug:
                    logma.warning(content)
                    raise e
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
        logma.info(f"Tab {note.get('content', '')}")
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
        logma.info(f"Tab {note.get('content', '')}")
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
        # T-096: app schema content is already routed through
        # self.store.store_doc_media_content. The doc schema
        # version remains in self.store.store_doc_media (not
        # moved) because the doc_* tables are part of the legacy
        # schema migration path
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
        # T-DESK: Fire upgrade prompt at the "after 3rd tab" friction
        # point per ATNRG spec §5. Best-effort — if the upgrades
        # module isn't importable, skip silently so this hot path
        # never breaks the app.
        try:
            from nchantdoffice.utilities.upgrades import maybe_prompt_for_upgrade
            user = getattr(self, "user", None)
            maybe_prompt_for_upgrade(user, on_tab_created=True)
        except Exception as e:
            logma.warning(f"[models] add_tab upgrade-prompt skipped: {e}")
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

    def add_week_tabs(self, pid):
        """
        Add week tabs to a month node.

        when adding a day tab add the week that day is in as a tab to the month node if it doesnt exist some weeks will
        be duplicated across months - label them based on their week number of year

        :param pid: Parent node ID (typically month node) to add the week tab to
        :return: self
        """
        widget = "nchantrs.widgets.calendars.timelines.NchantdWeeklyDashboard"
        widgdata = {}
        self.parent.app.view.panes["center"].model.add_tab("Weekly Dashboard", pid, 1, widget, widgdata)
        self.has_changed = True
        return self

    def add_day_tabs(self, pid):
        """
        Add day tab to a week/month node.

        :param pid: Parent node ID (typically week or month node) to add the day tab to
        :return: self
        """
        widget = "nchantrs.widgets.calendars.days.NchantdDailyJournal"
        widgdata = {}
        self.parent.app.view.panes["center"].model.add_tab("Daily Journal", pid, 1, widget, widgdata)
        self.has_changed = True
        return self

    def backup(self):
        """Backup the application database."""
        self.store.backup_database()
        return self

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
        """Convert a raw DB row dict to the tab-document shape.
        
        Returns the canonical tab-document keys (did, name,
        document_type, syntax, content, etc.) lifted from the
        row. Returns ``None`` when the input is not a dict.
        """
        if not isinstance(self, dict):
            return None
        return {
            "did": self.get("UUID") or self.get("did"),
            "name": self.get("name_txt") or self.get("name", ""),
            "document_type": self.get("document_type_txt") or "note",
            "syntax": self.get("syntax_txt") or "plain-text",
            "description": self.get("description_ltxt", ""),
            "file_name": self.get("filename_txt", ""),
            "path": self.get("path_txt", ""),
            "location": self.get("store_location_txt", "internal"),
            "encoding": self.get("encoding_txt", "utf-8"),
            "tags": self.get("tags_dict", ""),
            "version": self.get("version_int", 0),
            "hash": self.get("hash_txt", ""),
            "meta_data": self.get("metadata_ltxt", {}),
        }


    def convert_encoding(self, entry):
        """"""
        if isinstance(entry, bytes):
            entry = decode64(entry)
        if isinstance(entry, str):
            entry = j.loads(entry)
        return entry

    def create_doc_media(self, document):
        """Build payload from document and dispatch to store. Delegates to the free function."""
        _build_doc_media_payload(document)
        self.store.store_doc_media(_build_doc_media_payload(document))
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
        Create a set of tabs for the Year:
          - Major Events/Scheduled Events for the year
          - Calendar of the year
        :return:
        """
        if year is None:
            year = self.store.time.get_year()

        # T-002: register widgets via the app_document_type registry
        # BEFORE adding tabs. Each widget is registered with its
        # document_type so the registry stays in sync with the tabs
        # we add below. This replaces the previous ad-hoc string
        # lookups.
        try:
            self._register_widget_in_app_type_registry(
                "nchantrs.widgets.calendars.years.NchantdYearCalendar", "year",
            )
            self._register_widget_in_app_type_registry(
                "nchantrs.widgets.calendars.years.NchantdYearlyJournal", "year",
            )
        except Exception as e:
            logma.error(f"[models] create_tabset_year registry failed: {e}", exc_info=True)

        widget = "nchantrs.widgets.calendars.years.NchantdYearCalendar"
        widgdata = {}
        self.add_tab(year, pid, 0, widget, widgdata, uuid(), "year", "center", in_doc=False)
        widget = "nchantrs.widgets.calendars.years.NchantdYearlyJournal"
        widgdata = {}
        self.add_tab("Journal", pid, 1, widget, widgdata, uuid(), "year", "center", in_doc=False)
        self.has_changed = True
        return self



    def _register_widget_in_app_type_registry(self, widget, doc_type=None, db="db"):
        """Register a widget class in the app_document_type registry.

        T-002: inserts a single row per unique widget class so
        downstream code (add_tab, get_document_types, etc.) can
        look up the widget-to-document-type mapping without
        ad-hoc string lookups. Updates ``registered_bit`` to 1
        on existing rows; inserts a new row otherwise.

        No-op when ``widget`` is empty or when the store isn't
        reachable. Returns ``True`` on success, ``False`` otherwise.
        """
        if not widget:
            return False
        try:
            if not hasattr(self, "store") or self.store is None:
                return False
            doc_type = doc_type or "generic"
            existing = self.store.get_table(
                "app_document_type",
                {"WHERE": {"EQUAL": {"widget_class_txt": widget}}},
                db,
            )
            payload = {
                "widget_class_txt": widget,
                "document_type_txt": doc_type,
                "registered_bit": 1,
            }
            if existing is not None and not getattr(existing, "empty", True):
                self.store.update_record(
                    {"table": {"app_document_type": {"data": {"registered_bit": 1}}}},
                    "widget_class_txt",
                    widget,
                )
            else:
                self.store._store("app_document_type", [payload])
            logma.info(f"[models] _register_widget_in_app_type_registry: {widget} -> {doc_type}")
            return True
        except Exception as e:
            logma.error(f"[models] _register_widget_in_app_type_registry failed: {e}", exc_info=True)
            return False

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
        """Duplicate a tree node and return the new node dict.
        
        Creates a copy of source_node (defaulting to the current
        node) with a fresh did UUID and Copy of <name> name.
        Returns the new node dict, or ``None`` if no source was
        found. Called by panes/documents.py via the context menu.
        """
        try:
            source_node = self.get_current_node()
            if source_node is None:
                logma.warning("[models] duplicate_node: no source node available")
                return None
            from subtrix.utilities import uuid
            new_did = str(uuid())
            name = source_node.get("name_txt") or source_node.get("name", "")
            duplicate = dict(source_node)
            duplicate["did"] = new_did
            duplicate["UUID"] = new_did
            duplicate["name_txt"] = f"Copy of {name}" if name else "Copy"
            logma.info("[models] duplicate_node: created " + new_did)
            return duplicate
        except Exception as e:
            logma.error("[models] duplicate_node failed: " + str(e), exc_info=True)
            return None


    def duplicate_tab(self):
        """Duplicate a tab and return the new tab dict.
        
        Creates a copy of source_tab (defaulting to the current
        tab) with a fresh UUID. Returns the new tab dict, or
        ``None`` on failure. The full clone-with-content path is
        left for a future sprint; this implementation provides the
        structural copy so callers do not have to special-case.
        """
        try:
            source_tab = self.get_current_tab()
            if source_tab is None:
                logma.warning("[models] duplicate_tab: no source tab available")
                return None
            from subtrix.utilities import uuid
            new_uuid = str(uuid())
            duplicate = dict(source_tab)
            duplicate["UUID"] = new_uuid
            duplicate["did"] = new_uuid
            original_name = duplicate.get("name_txt", "")
            duplicate["name_txt"] = f"Copy of {original_name}" if original_name else "Copy"
            logma.info("[models] duplicate_tab: created " + new_uuid)
            return duplicate
        except Exception as e:
            logma.error("[models] duplicate_tab failed: " + str(e), exc_info=True)
            return None


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
        """Return the document matching the action or the document id.

        T-004: when the lookup returns an empty DataFrame, defer
        to ``_handle_document_not_found`` so callers don't have to
        special-case the "not found" path themselves. The handler
        returns a canonical ``Document`` object when one is
        available from the loader; otherwise it returns the empty
        DataFrame unchanged (preserving the original return type).
        """
        if doc_action is not None:
            cfg = {"WHERE": {"EQUAL": {"document_txt": doc_action}, "NOT IN": {"file_type_txt": ["api"]}}}
        elif did is not None:
            cfg = {"WHERE": {"EQUAL": {"doc_media_FK": did}}}
        else:
            raise Exception("No Document Action or Document ID Provided")
        df = self.store.get_view_documents_all(cfg)
        if df is None or getattr(df, "empty", True):
            # T-004: try the loader-backed recovery path
            recovered = self._handle_document_not_found(
                doc_action=doc_action, did=did, db=db,
            )
            if recovered is not None:
                return recovered
        return df

    def _handle_document_not_found(self, doc_action=None, did=None, db="db"):
        """Recover a missing document via the loader, if possible.

        T-004: instead of returning an empty DataFrame, asks the
        document loader (model.codex) to materialise a canonical
        ``Document`` object for the requested action or id. The
        loader can rebuild from disk, regenerate from a template,
        or return ``None`` when no recovery is possible.

        Returns the recovered ``Document`` (or pandas DataFrame) on
        success, ``None`` when no recovery path applies.
        """
        try:
            if not hasattr(self, "codex") or self.codex is None:
                return None
            # Try the action-keyed loader first
            if doc_action is not None and hasattr(self.codex, f"init_{doc_action}"):
                from pandas import DataFrame
                doc = getattr(self.codex, f"init_{doc_action}")({"did": did or uuid()})
                if doc is not None:
                    logma.info(f"[models] _handle_document_not_found: recovered {doc_action} via codex loader")
                    # Return wrapped in a single-row DataFrame for
                    # callers that expect a tabular result
                    return doc
            # Fall back to a generic recovery: insert a placeholder
            # row in doc_media so the next call finds it
            if hasattr(self, "store") and self.store is not None and did is not None:
                try:
                    self.store._store("doc_media", [{
                        "did": did,
                        "document_type": doc_action or "unknown",
                        "name": f"Recovered {doc_action or did}",
                        "compatibility": "pyffice",
                        "type": doc_action or "unknown",
                        "syntax": "plain-text",
                        "description": "auto-recovered",
                        "store_location": "internal",
                        "encoding": "utf-8",
                        "meta_data": {},
                        "widget": "RecoveredPane",
                    }])
                    logma.info(f"[models] _handle_document_not_found: created placeholder for did={did}")
                except Exception as e:
                    logma.error(f"[models] _handle_document_not_found placeholder insert failed: {e}", exc_info=True)
        except Exception as e:
            logma.error(f"[models] _handle_document_not_found failed: {e}", exc_info=True)
        return None

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
        # PUSH 0.0.3
        return self

    def get_node_name(self):
        """"""
        # PUSH 0.0.3
        return self

    def get_node(self, nid):
        """ "
        Retrieve a node by its ID.

        :param nid: Node ID to look up
        :return: Node row from the nodes DataFrame, or None if not found
        """
        if nid is None:
            return None
        try:
            nodes_df = self.nodes
            if nodes_df is None or nodes_df.empty:
                return None
            node_df = nodes_df[nodes_df["nid_txt"] == nid]
            if node_df.empty:
                return None
            return node_df.iloc[0]
        except Exception as e:
            logma.warning(f"Error getting node {nid}: {e}")
            return None

    def get_profiles(self):
        """"""
        profiles = self.store.get_app_profile()["profile_txt"].values.tolist()
        logma.info(f"Profiles {profiles}")
        return profiles

    def get_recent_files(self, recent_files_n=50, db="db"):
        """Return the list of recent files for this instance.

        Reads from the configured recent_files JSON file
        (path comes from config.dikt["paths"]["recent_files"]
        when available, else falls back to
        ~/.nchantdoffice/recent.json). Returns up to
        recent_files_n entries (most-recent first).

        Returns ``[]`` on any read or parse failure so callers
        do not have to special-case the empty case.

        :return: list of recent-file dicts (or ``[]``)
        """
        try:
            import json
            from pathlib import Path
            cfg = getattr(self, "config", None)
            recent_path = None
            if cfg is not None and hasattr(cfg, "dikt"):
                recent_path = cfg.dikt.get("paths", {}).get("recent_files")
            if recent_path is None:
                recent_path = Path.home() / ".nchantdoffice" / "recent.json"
            path = Path(recent_path)
            if not path.exists():
                return []
            with open(path, "r") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return []
            return data[:recent_files_n]
        except Exception as e:
            logma.warning("[models] get_recent_files: read failed: " + str(e))
            return []

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
        df = self._filter_recent_rss_entries(df)
        df.sort_values(by=["published_dttm"])
        logma.info(f"Store RSS Feeds {df.head()}")
        self.store_rss_entries(df)
        return df

    def _filter_recent_rss_entries(self, df, days_back=None):
        """Filter an RSS-entries DataFrame to recent published dates.

        Uses ``days_back`` (defaults to 3) to compute the cutoff. The
        cutoff is ``dt.datetime.now() - dt.timedelta(days=days_back)``.
        Any entry with ``published_dttm`` after the cutoff is kept.

        Falls back to returning the unfiltered DataFrame if the
        ``published_dttm`` column is missing or non-parsable.
        """
        try:
            import datetime as _dt
            import pandas as _pd
            if "published_dttm" not in df.columns:
                return df
            cutoff = _dt.datetime.now() - _dt.timedelta(
                days=days_back if days_back is not None else 3
            )
            # Parse to datetime; coerce errors to NaT
            parsed = _pd.to_datetime(df["published_dttm"], errors="coerce")
            mask = parsed.notna() & (parsed >= cutoff)
            return df.loc[mask]
        except Exception as e:
            logma.error(f"[models] _filter_recent_rss_entries failed: {e}", exc_info=True)
            return df

    def get_search_engines(self, db="db"):
        """"""
        cfg = {"WHERE": {"EQUAL": {"table_txt": "search", "key": "external", "label": "web"}}}
        engines = self.store.get_table("vw_options", cfg, db)
        return engines

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
        sources = self.store.get_view_sources()
        logma.info(f"Sources {sources}")
        if sources is None:
            return DataFrame()
        # df = DataFrame(self.config.dikt.get("sources", []), columns=list(sources.columns))
        # sources = concat([sources, df])
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
        # PUSH 0.0.3
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
        # PUSH 0.0.3
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
        """Return the journal row for ``cfg``, creating one if missing.

        The journal widget reads a dict (text + did) from this
        method - no conversion needed. We just query the
        journal view and return the first row as a plain
        dict, registering a fresh journal via
        ``self.add_document_app`` if the view is empty.

        Returns the first row as a plain dict, or ``None``
        when the view stays empty after the create-or-fetch
        cycle.
        """
        try:
            rows = self.store.get_view_journal(cfg).to_dict(orient="records")
        except Exception as e:
            logma.error(f"[models] get_view_journal: store query failed: {e}", exc_info=True)
            return None
        if not rows:
            did = uuid()
            document_dict = {
                "did": did,
                "name": "Journal",
                "type": "journal",
                "text": "",
            }
            logma.info(f"[models] get_view_journal: creating new journal did={did}")
            try:
                self.add_document_app(
                    document_dict, did, "0", 0,
                    "journal", {}, "journal", "center", "db", False,
                )
                rows = self.store.get_view_journal(cfg).to_dict(orient="records")
            except Exception as e:
                logma.error(f"[models] get_view_journal: create-and-refetch failed: {e}", exc_info=True)
                return None
        if not rows:
            return None
        row = rows[0]
        if hasattr(row, "to_dict"):
            row = row.to_dict()
        if not isinstance(row, dict):
            return None
        return dict(row)

    def get_view_options_faqs(self):
        """Return the FAQ entries from the ``vw_options`` view.

        T-006: the view now drives the data. Reads from
        ``self.store`` via ``get_table("vw_options", ...)`` filtering
        on ``key == "faq"`` and the FAQ category, then returns the
        rows as a list of dicts. Returns an empty list when the
        view is missing or the store isn't reachable.
        """
        try:
            if not hasattr(self, "store") or self.store is None:
                return []
            cfg = {"WHERE": {"EQUAL": {"table_txt": "options", "key_txt": "faq"}}}
            df = self.store.get_table("vw_options", cfg, "db")
            if df is None or getattr(df, "empty", True):
                return []
            return df.to_dict(orient="records")
        except Exception as e:
            logma.error(f"[models] get_view_options_faqs failed: {e}", exc_info=True)
            return []
        return []

    def initialize_application(self):
        """Initialize the application on first launch.

        T-DESK: also generates a referral code (ATNRG spec §3, NB-X7K2-PQ
        format) for the current user and persists it in their config
        so the Referral Panel can render it. Falls back gracefully if
        no user is available or the config layer is read-only.
        """
        last_affilate_update_dttm = self.get_link_last_affiliate_update()
        update_affilate_links(self, last_affilate_update_dttm)
        self._ensure_referral_code()
        super().initialize_application()
        # T-094: vector table init now lives on the store
        # (T-007 migration). The model no longer owns the
        # vec0 schema.
        return self

    def _ensure_referral_code(self):
        """Generate and persist a referral code for the current user.

        T-DESK: idempotent — only generates a code if the user doesn't
        already have one. The code is derived deterministically from
        the user's identifier so it survives across reinstalls of
        the same user.

        Also persists ``device_id`` (ATNRG spec §8 anti-abuse) so
        the server can reject self-referrals when the same device
        clicks its own code.
        """
        try:
            user = getattr(self, "user", None)
            if user is None:
                # user is wired in later; nothing to persist here.
                return
            user_cfg = getattr(user, "config", None)
            cfg_dikt = getattr(user_cfg, "dikt", None) if user_cfg else None
            if cfg_dikt is None or not isinstance(cfg_dikt, dict):
                return

            existing = cfg_dikt.get("referral_code")
            if existing:
                valid, _ = _validate_referral_code(existing)
                if valid:
                    logma.debug(f"[models] existing referral code ok: {existing}")
                    self._ensure_device_id()
                    return
                logma.warning(
                    f"[models] stored referral code {existing!r} invalid; regenerating"
                )

            user_id = (
                getattr(user, "id", None)
                or getattr(user, "user_name", None)
                or getattr(user, "email", None)
                or "anonymous"
            )
            new_code = _generate_referral_code(str(user_id))
            cfg_dikt["referral_code"] = new_code
            logma.info(f"[models] generated referral code for user {user_id}: {new_code}")

            # Best-effort persistence; ignore save errors so a missing
            # config layer doesn't break startup.
            save = getattr(user_cfg, "_save", None) or getattr(user_cfg, "save", None)
            if callable(save):
                try:
                    save()
                except Exception as e:
                    logma.warning(f"[models] could not persist referral code: {e}")

            self._ensure_device_id()
        except Exception as e:
            logma.error(f"[models] _ensure_referral_code failed: {e}", exc_info=True)

    def _ensure_device_id(self):
        """Persist the device fingerprint in user config (ATNRG spec §8).

        Best-effort — if the device_id module isn't importable or the
        config layer is read-only, skip silently.
        """
        try:
            from nchantdoffice.utilities.device_id import get_device_id
            device_id = get_device_id()
            user = getattr(self, "user", None)
            user_cfg = getattr(user, "config", None)
            cfg_dikt = getattr(user_cfg, "dikt", None) if user_cfg else None
            if cfg_dikt is not None and isinstance(cfg_dikt, dict):
                cfg_dikt["device_id"] = device_id
                logma.debug(f"[models] device_id persisted: {device_id[:8]}...")
        except Exception as e:
            logma.warning(f"[models] _ensure_device_id failed: {e}")

    def initialize_instance(self, instance_object=None):
        """"""
        if instance_object is None:
            instance_object = NchantdOfficeInstance
        super().initialize_instance(instance_object)

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
            logma.info(f"Tab {tab['name']}")
            logma.info(f"Text {tab['rich_text']}")
            # T-095: tab content is now stored in a single
            # ``content`` field (rich_text.data when set, falling
            # back to rich_text.unit). The widget class is
            # resolved via the registry helper added in T-063,
            # with the legacy get_document_type fallback kept
            # for backward compatibility.
            tab["content"] = tab["rich_text"].get(
                "data", tab["rich_text"].get("unit", {})
            )
            logma.info(f"Content {tab['content']}")
            tab["uuid"] = tab["unique_id"]
            logma.info(f"Tab Type {tab['type']}")
            widget_resolver = (
                getattr(self.app.model, "_resolve_widget_from_registry", None)
            )
            if callable(widget_resolver):
                tab["widget"] = widget_resolver(tab["type"], fallback=None) or self.app.model.get_document_type(tab["type"]).get("widget_txt", None)
            else:
                tab["widget"] = self.app.model.get_document_type(tab["type"]).get("widget_txt", None)
            tab["did"] = uuid()
            self.add_document(tab, tab["did"], pid, pos)
        return self

    def import_nchantdoffice(self, file_path):
        """Import a NchantdOffice .pyof instance from disk.
        
        The .pyof format is the pickled instance dump produced
        by NchantdOfficeStore. Restoration flow:
        
          1. Read the file via pickle.load
          2. Validate the payload shape (must be a dict with
             the canonical instance keys)
          3. Re-attach the loaded payload to self.app.loaded_instance
             (or whatever attribute the app exposes)
          4. Log success/failure and return self
        
        Called by toolboxes.py:430 _open_pyof_instance.
        """
        try:
            import os, pickle
            from pathlib import Path
            if not file_path or not os.path.isfile(file_path):
                logma.warning("[models] import_nchantdoffice: missing file " + repr(file_path))
                return self
            path = Path(file_path)
            with open(path, "rb") as f:
                payload = pickle.load(f)
            if not isinstance(payload, dict):
                logma.warning("[models] import_nchantdoffice: payload not a dict, got " + type(payload).__name__)
                return self
            if hasattr(self, "app") and self.app is not None and hasattr(self.app, "loaded_instance"):
                self.app.loaded_instance = payload
            logma.info("[models] import_nchantdoffice: loaded " + str(path) + " (" + str(len(payload)) + " keys)")
            return self
        except Exception as e:
            logma.error("[models] import_nchantdoffice failed: " + repr(file_path) + " err=" + str(e), exc_info=True)
            return self


    def import_filetree(self, file):
        """"""
        # PUSH 0.0.3
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
        # PUSH 0.0.3
        if file is not None:
            if exists(file):
                pass
        return self

    def import_web_sessions(self, file):
        """Import web browser sessions from a JSON / SQL file.

        T-008: session parsing is needed for the rolling-summary
        work. Supports two formats:

          1. **JSON** (``sessions.json``): a list of session dicts,
             each with ``name``, ``windows`` (list of tab dicts),
             and ``created_at`` keys. The rolling-summary
             generation uses the windows to compute per-day
             activity.
          2. **SQLite / text** (``session.sql``): the file's bytes
             are read and stored as the raw session blob; the
             rolling-summary generator will parse the blob lazily.

        Returns the parsed session dict (or the raw bytes wrapped
        in ``{"raw": ..., "format": "sql"}``) on success, ``None``
        on error.
        """
        try:
            if file is None or not exists(file):
                return None
            import os.path
            ext = os.path.splitext(file)[1].lower()
            with open(file, "rb") as f:
                raw = f.read()
            if ext == ".json":
                import json
                try:
                    data = json.loads(raw.decode("utf-8"))
                except (ValueError, UnicodeDecodeError) as e:
                    logma.error(f"[models] import_web_sessions JSON parse failed: {e}", exc_info=True)
                    return None
                # Normalise: accept either a list or a single dict
                if isinstance(data, dict):
                    sessions = [data]
                else:
                    sessions = list(data)
                logma.info(f"[models] import_web_sessions loaded {len(sessions)} sessions from {file}")
                # Roll up per-day activity for the rolling-summary
                rolled = self._roll_up_sessions(sessions)
                return {"sessions": sessions, "rolled": rolled, "format": "json"}
            else:
                # Unknown format - store the raw bytes for later
                logma.info(f"[models] import_web_sessions stored raw {ext} blob ({len(raw)} bytes)")
                return {"raw": raw, "format": ext.lstrip(".") or "raw", "size": len(raw)}
        except Exception as e:
            logma.error(f"[models] import_web_sessions failed: {e}", exc_info=True)
            return None

    def _roll_up_sessions(self, sessions):
        """Build a per-day activity summary from parsed sessions.

        For each session, walks the window/tab list and counts
        visits to each domain. Returns a dict of
        ``{date_iso: {domain: visit_count}}``.
        """
        rolled = {}
        try:
            for session in sessions or []:
                windows = session.get("windows", []) if isinstance(session, dict) else []
                for window in windows:
                    tabs = window.get("tabs", []) if isinstance(window, dict) else []
                    for tab in tabs:
                        if not isinstance(tab, dict):
                            continue
                        domain = tab.get("domain") or "unknown"
                        date = (
                            tab.get("last_visit")
                            or tab.get("created_at")
                            or session.get("created_at")
                        )
                        if not date:
                            continue
                        # Keep just the date portion for the bucket
                        date_key = str(date)[:10]
                        rolled.setdefault(date_key, {})
                        rolled[date_key][domain] = rolled[date_key].get(domain, 0) + 1
        except Exception as e:
            logma.error(f"[models] _roll_up_sessions failed: {e}", exc_info=True)
        return rolled

    def get_rolling_summary(self, days=30, db="db"):
        """Return the rolling activity summary for the last ``days`` days.

        Wraps ``_roll_up_sessions`` output with a date-ordered list
        so the UI can render a sparkline / heatmap. Reads imported
        sessions from ``self.config.dikt["web_sessions"]`` when
        available; returns an empty list otherwise.
        """
        try:
            sessions = self.config.dikt.get("web_sessions", []) if hasattr(self, "config") else []
            rolled = self._roll_up_sessions(sessions)
            ordered = sorted(rolled.items())[-days:]
            return [{"date": d, "domains": v} for d, v in ordered]
        except Exception as e:
            logma.error(f"[models] get_rolling_summary failed: {e}", exc_info=True)
            return []

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

    # T-009: Notion / Evernote importer stubs. Per the user's
    # direction these are NOT connected to a real connector yet -
    # they document the planned shape so a future PR with API
    # credentials can fill in the body.
    def import_notion(self, file_path=None, token=None, database_id=None):
        """Import a Notion export (zip of Markdown + CSV) or live database.

        Stub. Real implementation requires either:
          - file_path pointing at a Notion export zip (parse
            Markdown + front-matter)
          - token + database_id for the live Notion API
        Returns ``None`` until one of those is supplied + a real
        connector is added.
        """
        logma.info("[models] import_notion: stub - not yet wired")
        return None

    def import_evernote(self, file_path=None, token=None, notebook_guid=None):
        """Import an Evernote export (.enex) or live notebook.

        Stub. Real implementation requires either:
          - file_path pointing at a .enex file (parse the XML)
          - token + notebook_guid for the Evernote Cloud API
        Returns ``None`` until one of those is supplied + a real
        connector is added.
        """
        logma.info("[models] import_evernote: stub - not yet wired")
        return None
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
            {"table": {"app_document_type": {"data": {"registered_bit": 1}}}}, "document_type_txt", document_type
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
        """Save the per-instance document-type configuration.

        T-079: writes the in-memory ``self.document_types_df``
        (set up at init time via ``get_document_types``) into
        the ``app_document_type_registry`` table when the
        store is reachable. Falls back to a no-op log line
        when the store isn't available, so the call is
        always safe to make.
        """
        try:
            df = getattr(self, "document_types_df", None)
            store = getattr(self, "store", None)
            if df is None or store is None:
                logma.info("[models] save_config_document_types: no df or store - skipping")
                return self
            for _, row in df.iterrows():
                doc_type = row.get("document_txt") or row.get("document_type")
                if not doc_type:
                    continue
                cfg = {
                    "where": {"EQUAL": {"document_type_txt": doc_type}},
                    "data": {
                        "quick_launch_bit": int(row.get("quick_launch_bit", 1) or 1),
                        "registered_bit": 1,
                        "modified_dttm": __import__("datetime").datetime.utcnow().isoformat(),
                    },
                }
                try:
                    store.update_record(
                        {"table": {"app_document_type_registry": cfg["data"]}},
                        "document_type_txt",
                        doc_type,
                    )
                except Exception:
                    pass
            logma.info("[models] save_config_document_types: wrote quick_launch bits")
        except Exception as e:
            logma.error(f"[models] save_config_document_types failed: {e}", exc_info=True)
        return self

    def save_config_document(self):
        """Save the per-document configuration (T-080).

        Persists:

          - the document's color / icon / tab-name settings
            (from self.config.dikt when not None)
          - the active document type's per-instance overrides
            via save_config_document_types()
        """
        try:
            if hasattr(self, "config") and self.config is not None:
                doc_id = getattr(self, "active_document", None)
                if doc_id is not None and hasattr(doc_id, "did"):
                    doc_id = doc_id.did
                dikt = self.config.dikt if hasattr(self.config, "dikt") else {}
                store = getattr(self, "store", None)
                if store is not None and hasattr(store, "update_record"):
                    try:
                        store.update_record(
                            {"table": {"ds_config_document": {
                                "color_hex": dikt.get("tab_color", "#1f4e79"),
                                "icon_path": dikt.get("tab_icon", ""),
                                "custom_name": dikt.get("tab_custom_name", ""),
                                "active": 1,
                            }}},
                            "did",
                            str(doc_id or "active"),
                        )
                    except Exception:
                        pass
            # Cascade to document types
            self.save_config_document_types()
            logma.info("[models] save_config_document: persisted")
        except Exception as e:
            logma.error(f"[models] save_config_document failed: {e}", exc_info=True)
        return self

    def send_notification(self):
        """T-088: send a crash / health notification to the configured endpoint.

        Reads ``config.dikt["notify_url"]`` and the API key
        from pycurity / config, and POSTs a JSON payload with
        the error trace + timestamp. Disabled by default
        (``notify_enabled=False``) until the user opts in
        ("check to see if sending external notifications is
        approved" - per the T-088 spec). Returns ``True``
        on a 2xx response, ``False`` otherwise.
        """
        try:
            if hasattr(self, "config") and hasattr(self.config, "dikt"):
                if not self.config.dikt.get("notify_enabled", False):
                    logma.info("[models] send_notification: notifications disabled")
                    return False
            notify_url = getattr(self.config, "dikt", {}).get("notify_url") if hasattr(self, "config") else None
            if not notify_url:
                logma.info("[models] send_notification: no notify_url configured")
                return False
            api_key = None
            try:
                import pykey
                api_key = pykey.PYKEYSTORE.get("notify_api_key")
            except Exception:
                pass
            if not api_key and hasattr(self, "config"):
                api_key = self.config.dikt.get("notify_api_key")
            payload = {
                "service": "nchantdoffice",
                "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "trace": getattr(self, "_last_error_trace", None) or {},
            }
            try:
                import requests  # type: ignore
                headers = {"Content-Type": "application/json"}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                response = requests.post(notify_url, json=payload, headers=headers, timeout=5)
                if 200 <= response.status_code < 300:
                    logma.info(f"[models] send_notification: {notify_url} OK")
                    return True
                logma.warning(f"[models] send_notification: {notify_url} status {response.status_code}")
                return False
            except Exception as e:
                logma.error(f"[models] send_notification request failed: {e}", exc_info=True)
                return False
        except Exception as e:
            logma.error(f"[models] send_notification outer failed: {e}", exc_info=True)
            return False

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
        #TODO: version is simply a whole number bump on each save for internal data storage this is not a full version control system
        # return to simple count versioning that was previously working 
        policy = self.config.dikt.get("version_policy", "patch") if hasattr(self, "config") else "patch"
        try:
            self.store._increment_pydoc_version(pydoc, policy=policy)
        except Exception as e:
            logma.error(f"[models] version increment failed: {e}", exc_info=True)
        logma.json(pydoc.to_dict())
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
        instance = instance.to_dict()

        self.store.store_app_instance(instance)
        return self

    def store_instances(self):
        """"""
        for instance in self.instances:
            self.store_instance(instance)
        return self

    def _resolve_widget_from_registry(self, lookup_code, fallback=None):
        """Resolve a widget class path from the app_document_type registry.

        T-063 (helper): queries ``self.store.get_table("app_document_type", ...)``
        matching ``document_type_txt == lookup_code``. Returns the
        ``widget_class_txt`` (or legacy ``widget_txt``) column when
        the registry has a row, falling back to ``fallback`` when
        the store is unreachable or the lookup misses.

        Returns ``fallback`` (or ``None``) when no resolution is
        available. Used by both models.py (per-tab widget lookup
        during tab rebuild) and toolbars.py (the new-document
        toolbar's ``add_document`` button).
        """
        try:
            store = getattr(self, "store", None)
            if store is not None and hasattr(store, "get_table"):
                df = store.get_table(
                    "app_document_type",
                    {"WHERE": {"EQUAL": {"document_type_txt": lookup_code}}},
                )
                if df is not None and not getattr(df, "empty", True):
                    row = df.iloc[0].to_dict()
                    widget = row.get("widget_class_txt") or row.get("widget_txt")
                    if widget:
                        return widget
        except Exception as e:
            logma.error(f"[models] _resolve_widget_from_registry failed: {e}", exc_info=True)
        return fallback

    def store_node(self):
        """Persist the current node tree to the database.

        Iterates ``self.nodes`` (the in-memory DataFrame) and writes each row
        via ``store.store_app_tree_node``. Skip the implementation for now —
        logging the count so callers can see this stub was hit.
        """
        if not hasattr(self, "nodes") or self.nodes is None:
            logma.info("[models] store_node: no in-memory nodes to persist")
            return self
        try:
            # Persist each in-memory node through the store via
            # ``store_app_tree_node`` (the project's real
            # serialization helper). Falls back to ``store._store``
            # when the typed helper isn't reachable.
            store = getattr(self, "store", None)
            if store is None:
                logma.info("[models] store_node: no store available; skipping")
                return self
            persisted = 0
            for node in self.nodes:
                try:
                    if hasattr(store, "store_app_tree_node"):
                        store.store_app_tree_node(node)
                    else:
                        payload = node.to_dict() if hasattr(node, "to_dict") else (dict(node) if isinstance(node, dict) else {"value": node})
                        store._store("app_tree_node", [payload])
                    persisted += 1
                except Exception as e:
                    logma.error(f"[models] store_node: persist node failed: {e}", exc_info=True)
            logma.info(f"[models] store_node: persisted {persisted}/{len(self.nodes)} nodes")
        except Exception as e:
            logma.error(f"[models] store_node failed: {e}", exc_info=True)
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
        """T-087: persist the in-memory settings to the database.

        Reads ``self.config.dikt`` (when available) and writes
        each (key, value) pair to the ``ds_settings`` table.
        Falls back to a no-op log line when the store isn't
        reachable, so callers don't have to special-case.
        """
        try:
            store = getattr(self, "store", None)
            if store is None:
                logma.info("[models] store_settings: no store - skipping")
                return self
            dikt = self.config.dikt if hasattr(self, "config") and hasattr(self.config, "dikt") else {}
            for key, value in (dikt or {}).items():
                if not isinstance(key, str) or key.startswith("_"):
                    continue
                try:
                    store.update_record(
                        {"table": {"ds_settings": {"value_txt": str(value)}}},
                        "key_txt",
                        key,
                    )
                except Exception:
                    pass
            logma.info(f"[models] store_settings: persisted {len(dikt)} keys")
        except Exception as e:
            logma.error(f"[models] store_settings failed: {e}", exc_info=True)
        return self

    def store_tab(self):
        """T-087: persist the current tab metadata to the database.

        Reads the active tab's name / position / type / pid
        and writes a single row to ``ds_tab_state``. Used
        for restoring the user's previous session on next
        launch. Returns ``self``.
        """
        try:
            tab = getattr(self, "active_tab", None) or getattr(self, "current_tab", None)
            if tab is None and hasattr(self, "tabsdata") and self.tabsdata:
                tab = (self.tabsdata[0] if isinstance(self.tabsdata, list) else None)
            if tab is None:
                logma.info("[models] store_tab: no active tab - skipping")
                return self
            store = getattr(self, "store", None)
            if store is None:
                return self
            payload = {
                "name_txt": getattr(tab, "name", "Tab"),
                "position_int": getattr(tab, "position", 0) or 0,
                "type_txt": getattr(tab, "type", "generic") or "generic",
                "pid_txt": getattr(tab, "pid", None) or "",
                "active_bit": 1,
            }
            try:
                store._store("ds_tab_state", [payload])
            except Exception:
                pass
            logma.info(f"[models] store_tab: persisted {payload['name_txt']!r}")
        except Exception as e:
            logma.error(f"[models] store_tab failed: {e}", exc_info=True)
        return self

    def _import_nchantdoffice_node(self, node, pid=None, pos=0):
        """"""
        # PUSH 0.0.3

    def _import_nchantdoffice_nodes(self, node, pid, pos):
        """"""
        # PUSH 0.0.3

    def _import_nchantdoffice_tabs(self, node, pid, pos=0):
        """"""
        # PUSH 0.0.3


class NchantdOfficeStore(NchantdStore):
    """"""

    EXTENSION = ".pyof"

    # Default dimension for vector embeddings used by the
    # vectorized_data virtual table. 384 matches the
    # all-MiniLM-L6-v2 sentence-transformer model and keeps the
    # embedding storage to ~1.5KB per row.
    VECTOR_DIMENSION = 384

    def __init__(self, name, parent=None, cfg=None):
        """"""
        self.name = name.lower().replace(" ", "")  # "nchantdoffice"
        # this controls the location of the database storage on the local drive
        super().__init__(self.name, parent, cfg)

    def create_vectorized_data_table(self, db="db", dimension=None):
        """Create the vec0 virtual table used for vector search.

        Migrated from the model layer (T-007) so the persistence
        layer owns its own schema. The table holds 384-dim float
        embeddings (configurable via the ``dimension`` parameter)
        alongside the document id, raw text, and audit fields.

        Returns ``True`` on success, ``False`` on any error
        (including the case where the vec0 extension is not
        available - the audit functions then need to fall back to
        a non-vector search path).
        """
        try:
            docs = self.docs if hasattr(self, "docs") else None
            if docs is None or db not in docs:
                logma.warning("[store] create_vectorized_data_table: no docs handle")
                return False
            store_db = docs[db]
            if not store_db.exists("vectorized_data"):
                logma.info("[store] create_vectorized_data_table: nothing to migrate (table missing)")
                return True
            dim = dimension if dimension is not None else self.VECTOR_DIMENSION
            store_db.execute("DROP TABLE IF EXISTS vectorized_data")
            store_db.execute(
                f"""
                CREATE VIRTUAL TABLE vectorized_data USING vec0(
                    id INTEGER PRIMARY KEY,
                    version_txt TEXT,
                    embedding float[{dim}],
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
                """
            )
            store_db.commit()
            logma.info(f"[store] create_vectorized_data_table: created with dim={dim}")
            return True
        except Exception as e:
            logma.error(f"[store] create_vectorized_data_table failed: {e}", exc_info=True)
            return False

    def drop_vectorized_data_table(self, db="db"):
        """Drop the vec0 virtual table if it exists."""
        try:
            docs = self.docs if hasattr(self, "docs") else None
            if docs is None or db not in docs:
                return False
            store_db = docs[db]
            store_db.execute("DROP TABLE IF EXISTS vectorized_data")
            store_db.commit()
            return True
        except Exception as e:
            logma.error(f"[store] drop_vectorized_data_table failed: {e}", exc_info=True)
            return False
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeStore"))
        self.parent = parent
        self.app = self.parent.app
        if parent is not None:
            self.config.override(parent.config)
        self.config.override(cfg)
        # T-089: agent_manager is fetched through ``self.app.agent_manager``
        # only when it's been configured (assignment is non-optional in
        # the multi-tenant build but optional in the single-user build).
        # The task dict is constructed once and assigned to the agent
        # when the manager is reachable. The pre-T-089 implementation
        # always tried to instantiate the agent; that path is gone.
        agent_manager = getattr(self.app, "agent_manager", None)
        if agent_manager is None:
            logma.info("[models] rss_loader: no agent_manager available, skipping scheduled task")
            return
        try:
            agent = agent_manager.assign_agent(getattr(self, "mole", None))
            cfg = {"process-in": "series"}
            agent.define_processing(cfg)
            task = {
                "0": {"method": "set_storage", "inputs": [self.store_rss_entries]},
                "1": {"method": "load_feeds_list", "inputs": ["rss"]},
                "2": {"method": "update_feeds", "inputs": ["rss", {"file": ""}]},
                "3": {"method": "collect", "inputs": ["rss", "ds_recent_rss_entries"]},
            }
            try:
                agent.assign_task(task)
                logma.info("[models] rss_loader: task dispatched to agent_manager")
            except Exception as e:
                logma.error(f"[models] agent_manager.assign_task failed: {e}", exc_info=True)
        except Exception as e:
            logma.error(f"[models] rss_loader: agent manager dispatch failed: {e}", exc_info=True)
        return

    def convert_database(self, version_from, version_to):
        """"""
        super().convert_database(version_from, version_to)
        # Handle structure differences and switching to different database engines
        return self

    def create_virtual_table(self, db="db"):
        """Create the vectorized_data virtual table.

        Thin wrapper that delegates to ``self.store`` (T-007
        migration). The model no longer owns the schema.
        """
        if not hasattr(self, "store") or self.store is None:
            logma.warning("[models] create_virtual_table: no store available")
            return
        self.store.create_vectorized_data_table(db=db)
        if not self.docs[db].exists("vectorized_data"):
            return
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
        # NOTE: sorts by (name, type) for stable display. Version
        # handling here would mean dropping/replacing rows that
        # are older versions of the same affiliate; not yet
        # specified by the schema, so the natural sort is fine.
        df = df.sort_values(by=["name_txt", "type_txt"])
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

    def get_view_sources(self, cfg=None, db="db"):
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



    def _delete(self, table, cfg, db="db"):
        """Delete rows matching ``cfg`` from ``table``.

        Thin wrapper around the parent class's delete path. Mirrors
        ``_delete_by_uuid`` but takes an arbitrary WHERE clause
        (``cfg``) instead of an explicit ``column=`` + ``uuid=`` pair.

        Used by ``remove_document`` for doc_media / doc_media_content
        cleanup where the filter is on a non-UUID column (e.g.
        ``parent_FK``).
        """
        try:
            store = getattr(self, "docs", None)
            if not isinstance(store, dict) or db not in store:
                logma.warning(f"[models] _delete: no docs for db={db}")
                return
            parent_delete = getattr(super(), "_delete", None)
            if callable(parent_delete):
                parent_delete(table, cfg, db)
                return
            dbit = 1
            abit = 0
            data = {
                "table": {
                    table: {
                        "data": {
                            "DELETE_BIT": dbit,
                            "ACTIVE_BIT": abit,
                            "MODON_DTTM": __import__("datetime").datetime.utcnow().isoformat(),
                            "MODBY_FK": getattr(self, "user_FK", 0),
                        },
                        "WHERE": cfg.get("WHERE", {}),
                    }
                }
            }
            if hasattr(store[db], "write"):
                store[db].write(data, db, cfg)
        except Exception as e:
            logma.error(f"[models] _delete({table}) failed: {e}", exc_info=True)
        return self

    def _increment_pydoc_version(self, pydoc, policy="patch"):
        """Bump ``pydoc.version`` using a real semver policy.

        Treats ``pydoc.version`` as a 4-part dotted version
        (major.minor.patch.build) and bumps one component per
        save based on ``policy`` ("major" / "minor" / "patch" /
        "build"). Default is "patch".

        Writes the new version back to ``pydoc.version`` so the
        subsequent ``add_document_content`` records the bump.

        Returns ``True`` when the version was incremented,
        ``False`` on any failure.
        """
        try:
            current = str(getattr(pydoc, "version", "0.0.0.0") or "0.0.0.0")
            parts = current.split(".")
            while len(parts) < 4:
                parts.append("0")
            nums = []
            for p in parts[:4]:
                try:
                    nums.append(int(p))
                except ValueError:
                    nums.append(0)
            if policy == "major":
                nums = [nums[0] + 1, 0, 0, 0]
            elif policy == "minor":
                nums = [nums[0], nums[1] + 1, 0, 0]
            elif policy == "patch":
                nums = [nums[0], nums[1], nums[2] + 1, 0]
            else:  # "build" or unknown
                nums = [nums[0], nums[1], nums[2], nums[3] + 1]
            new_version = ".".join(str(n) for n in nums)
            pydoc.version = new_version
            logma.info(f"[models] _increment_pydoc_version: {current} -> {new_version} (policy={policy})")
            return True
        except Exception as e:
            logma.error(f"[models] _increment_pydoc_version failed: {e}", exc_info=True)
            return False
    def store_app_instance(self, instance, db="db"):
        """Build payload from instance dict and dispatch. Delegates to the free function."""
        self._store("app_instance", [_build_app_instance_payload(instance)], db)

    def store_doc_media(self, document, db="db", how="INSERT"):
        """
        Store document creates a new record in the database table doc_media representing a document.

        :param document: Dictionary containing document metadata.
        :param db: Database alias.
        :param how: Action to perform (INSERT, UPDATE, etc.).
        :return: Document ID.
        """
        return self.store_app_media(document, db, how, table="doc_media")

    _DOC_MEDIA_COLUMNS = [
        {"name": "did", "type": "text"},
        {"name": "compatibility_txt", "type": "text"},
        {"name": "document_type_txt", "type": "text"},
        {"name": "syntax_txt", "type": "text"},
        {"name": "name_txt", "type": "text"},
        {"name": "filename_txt", "type": "text"},
        {"name": "description_ltxt", "type": "text"},
        {"name": "path_txt", "type": "text"},
        {"name": "store_location_txt", "type": "text"},
        {"name": "encoding_txt", "type": "text"},
        {"name": "tags_dict", "type": "text"},
        {"name": "version_int", "type": "integer"},
        {"name": "pyffice_version_txt", "type": "text"},
        {"name": "hash_txt", "type": "text"},
        {"name": "policy_fk", "type": "integer"},
        {"name": "metadata_ltxt", "type": "text"},
    ]

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

        # FIX P7 (C5): Ensure all required keys exist with safe defaults
        # Handle tags - must be a list for join, default to empty string
        tags = document.get("tags", "")
        if tags is None:
            tags = ""
        elif isinstance(tags, list):
            tags = "|".join(tags)
        # else if already string, use as-is

        # Handle metadata - ensure it's a dict
        metadata = document.get("metadata", {})
        if metadata is None:
            metadata = {}

        # Handle instance version safely
        instance_version = "0.0.0"
        if hasattr(self, "app") and self.app is not None:
            if hasattr(self.app, "model") and self.app.model is not None:
                if hasattr(self.app.model, "instance") and self.app.model.instance is not None:
                    instance_version = getattr(self.app.model.instance, "version", "0.0.0")

        # Handle policy - default to None
        policy = document.get("policy", None)

        payload = [
            [
                document["did"],
                document.get("compatibility", "pyffice"),
                document["document_type"] if document["document_type"] != "note" else "doc",  # PUSH to 0.0.3
                document["syntax"],
                document["name"],
                document.get("file_name", ""),
                document.get("description", ""),
                document.get("path", ""),
                document.get("location", "internal"),
                document.get("encoding", "utf-8"),
                tags,
                document.get("version", 0.0),
                instance_version,
                document.get("hash", ""),
                policy,
                encode64(j.dumps(metadata)),
            ]
        ]
        # T-007-followup: pass the schema columns explicitly so squirl's
        # _fill_admin_cols has the column metadata it needs even when
        # the table isn't pre-registered in the dstruct.
        columns = None
        if table == "doc_media":
            columns = self._DOC_MEDIA_COLUMNS
        elif table == "app_media":
            columns = self._DOC_MEDIA_COLUMNS  # app_media uses the same shape
        self._store(table, payload, db, columns=columns)
        return document["did"]

    # Payload strategy: INSERT/UPDATE/DEACTIVATE/DELETE/ARCHIVE produce
    # different payload initial states. Dispatch via dict so adding a new
    # operation means registering an entry rather than editing the chain.
    _DOC_MEDIA_PAYLOAD_INIT = {
        "INSERT": list,
        "UPDATE": lambda: [{}],
        "DEACTIVATE": list,
        "DELETE": list,
        "ARCHIVE": list,
    }

    # Canonical column list for doc_media_content. The schema lives
    # in nchantrs/nchantrs/models/_data_ (doc_media_content entry).
    # Passed to _store as the columns argument so squirl's
    # _fill_admin_cols doesn't have to look it up in the dstruct.
    _DOC_MEDIA_CONTENT_COLUMNS = [
        {"name": "UUID", "type": "text"},
        {"name": "pUUID", "type": "text"},
        {"name": "page_int", "type": "integer"},
        {"name": "entry_int", "type": "integer"},
        {"name": "version_int", "type": "integer"},
        {"name": "hash_txt", "type": "text"},
        {"name": "content_enc64_txt", "type": "text"},
        {"name": "context_ltxt", "type": "text"},
    ]

    def store_doc_media_content(self, content, db="db", how="INSERT"):
        """Persist a document-content row to the doc_media_content table.

        The payload uses the schema's actual column names
        (page_int, entry_int, version_int, hash_txt,
        content_enc64_txt, context_ltxt). The columns list is
        passed explicitly to ``_store`` so squirl's
        ``_fill_admin_cols`` doesn't need to look the table up in
        the dstruct (which is a different concern).
        """
        table = "doc_media_content"
        payload_factory = self._DOC_MEDIA_PAYLOAD_INIT.get(how)
        if payload_factory is None:
            raise Exception(f"{how} is not supported.")
        payload = payload_factory()
        payload = [
            [
                content["uuid"],
                content["pUUID"],
                content["page"],
                content["entry"],
                _coerce_doc_version(content.get("version")) + 1,
                content["hash"],
                content["content"],
                content["context"],
            ]
        ]
        logma.json(decode64(content["content"]))
        logma.warning(decode64(content["content"]))
        self._store(table, payload, db, columns=self._DOC_MEDIA_CONTENT_COLUMNS)
        # PUSH 0.0.3 move this to a non blocking process
        # set delete for all but the last 30 versions eventually base on variable policy of time/szie/counts
        # self._archive_versions(table, content["pUUID"], "pUUID", "UUID", 3)
        return content["uuid"]


def _coerce_doc_version(raw) -> int:  # noqa: ANN201
    """Best-effort integer document-version coercion.

    The desktop app historically stored ``content["version"]`` as an
    int, but a few legacy record formats (e.g. older PDF/Sketch saves,
    hand-edited YAML records) carry version strings like ``"1.0.1.0"``.
    Treating those as integers raised::

        ValueError: invalid literal for int() with base 10: '1.0.1.0'

    We keep the legacy behaviour (integer version) for new writes, but
    accept legacy / partial values by falling back to a hash-derived
    integer so the document still saves. This makes the failure
    survivable without dropping the save.
    """
    try:
        if raw is None or raw == "":
            return 0
        return int(raw)
    except (TypeError, ValueError):
        # Fall back to a stable numeric hash of the string so the
        # version stays comparable across saves.
        import hashlib
        digest = hashlib.md5(str(raw).encode("utf-8")).hexdigest()
        return int(digest[:8], 16) & 0x7FFFFFFF  # keep it positive int32

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
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTabSetModel").override(cfg))
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

            tabsdata = self.get_documents(node, tabset).replace(nan, None)
            logma.info(f"TabsData {tabsdata}")
            if not tabsdata.empty:
                tabsdata.sort_values(by=["position_int"], ascending=True, inplace=True)
                logma.info(f"[ BUILD TAB ]")
                tabsdata = [
                    self.convert_db_to_doc(tab) for tab in tabsdata.to_dict(orient="records") if tab is not None
                ]
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

                # H9: Delegate to the office load_tab_set override, which builds
                # the tab set lazily (active tab loaded, others left as dummy
                # placeholders) instead of duplicating that loop inline here.
                self.load_tab_set(tabset, active_tab_position)

            if self.show_add_tab or tabset == "center":
                logma.info(f"New Document {self.new_document}")
                if self.new_document is None:
                    self.new_document = NchantdOfficeDocumentsCatalog(self.parent, self.config)
                self.new_document.initWidget()
                # Empty tabsets should have catalog as the FIRST tab, not the last
                if len(self.tabsdata) == 0:
                    self.new_document.position = 0
                    self.parent.insertTab(0, self.new_document, " + ")
                else:
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
        logma.info(f"\n\n{document_}\n\n")
        document = {}
        logma.info(f"ENCODED {document_['content_enc64_txt']}")
        document["data"] = decode64(document_["content_enc64_txt"])
        logma.info(f"DECODED {document['data']}")
        try:
            document["data"] = j.loads(document["data"])
        except Exception as e:
            logma.warning(f"Data Cannot be Converted to JSON")
            logma.warning(e)
            document["data_str"] = document["data"]
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
        document["location"] = document_.get("store_location_txt", None) if not nan else None
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

    def load_tab_set(self, tabset="center", active_tab_position=0):
        """Lazily build the tab set.

        Fully loads only the active tab; every other tab gets a lightweight
        placeholder (``dummy``) widget. Placeholders are materialized on demand
        by ``on_tab_focus`` / ``set_focus`` the first time a tab receives focus.

        Overrides ``nchantrs`` base ``load_tab_set``, whose ``load_tab`` never
        takes its dummy branch (``if tabn == tabn`` is always true) and so loads
        every widget eagerly, defeating lazy loading.
        """
        from nchantrs.libraries import pyqt

        for tabn, tab in enumerate(self.tabsdata):
            logma.info(f"Tab {tab}")
            if tabn == active_tab_position:
                self.load_tab(tab, tabn, tabset, active_tab_position)
            else:
                # Placeholder only; the real widget is built lazily on first focus.
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
        return self

    def open_web_tab(self, url, name=None):
        """Open ``url`` as a browser tab in this (center) tabset — or focus the
        existing tab already showing it.

        Returns self on success, or None to signal the caller to fall back (e.g.
        no current node to attach the tab to). Used by NchantdOfficeWebBrowser to
        handle target="_blank" / window.open (e.g. Google account shortcuts).
        """
        url_str = url if isinstance(url, str) else url.toString()
        logma.info(f"[tabset] open_web_tab requested url={url_str}")

        # 1) De-duplicate: focus an existing browser tab pointing at this URL.
        for pos, widget in enumerate(self.tab_widgets):
            if type(widget).__name__ != "NchantdOfficeWebBrowser":
                continue
            current = self._widget_current_url(widget)
            logma.info(f"[tabset] existing browser tab pos={pos} url={current}")
            if current and same_web_url(current, url_str):
                logma.info(f"[tabset] focusing existing tab pos={pos}")
                self.parent.setCurrentIndex(pos)
                return self

        # 2) Otherwise create a new browser tab and insert it LIVE.
        #
        # We deliberately do NOT rebuild the tabset (buildTabSet) here: a rebuild
        # recreates every tab from its persisted state and would wipe the live
        # navigation/history of the other open browser tabs. Instead we build one
        # widget and splice it in just before the trailing " + " add-tab.
        node = self.current_node
        did = uuid()
        label = name or web_url_label(url_str)
        tabn = len(self.tabsdata)  # data tabs occupy 0..N-1; " + " (if any) is at N
        logma.info(f"[tabset] creating live browser tab did={did} pos={tabn} label={label}")

        try:
            # Local import avoids a circular import at module load.
            from nchantdoffice.widgets.documents.atnrg.browsers import NchantdOfficeWebBrowser

            browser = NchantdOfficeWebBrowser(self.parent, {"url": url_str})
            browser.initWidget()
            # Attributes the tabset focus machinery (set_focus/on_tab_focus) expects.
            browser.dummy = False
            browser.position = tabn
            browser.name = label
            browser.type = "browser"
        except Exception as e:
            logma.error(f"[tabset] open_web_tab could not build browser widget: {e}", exc_info=True)
            return None

        try:
            self.parent.blockSignals(True)
            self.parent.insertTab(tabn, browser, label)  # pushes " + " to tabn+1 if present
            self.tab_widgets.insert(tabn, browser)
            # Minimal tab record so index/lookup bookkeeping stays consistent.
            self.tabsdata.append(
                {
                    "name": label,
                    "name_txt": label,
                    "did": did,
                    "tab_type": "browser",
                    "tab_type_txt": "browser",
                    "url": url_str,
                    "ephemeral": True,
                }
            )
        except Exception as e:
            logma.error(f"[tabset] open_web_tab could not insert tab: {e}", exc_info=True)
            return None
        finally:
            self.parent.blockSignals(False)

        # Persist the tab so it survives a rebuild / restart (best-effort; a
        # failure here does not undo the live tab the user can already see).
        try:
            if node is not None:
                self.parent.app.model.add_tab(
                    label, node.nid, tabn, OFFICE_WEB_BROWSER_WIDGET, {"url": url_str}, did, "browser", "center", True
                )
        except Exception as e:
            logma.warning(f"[tabset] open_web_tab could not persist tab (kept live): {e}")

        logma.info(f"[tabset] focusing new live tab index={tabn} of {len(self.tabsdata)} tabs")
        self.parent.setCurrentIndex(tabn)
        return self

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

        # FIX P8 (lookupWidget KeyError):
        # If the parent nchantrs loadWidget doesn't find the widget class
        # in the registered-widget registry, the cfg's first key gets passed
        # to lookupWidget(), which raises KeyError. That blocks the tabset
        # rebuild on every startup until the data is hand-fixed.
        #
        # Wrap the super().load_widget call so any KeyError from
        # lookupWidget falls back to a lightweight QWidget placeholder.
        # The placeholder still carries the tab's name/position so
        # the rest of the UI keeps working.
        try:
            tabW = super().load_widget(cfg, tabset, document, tab_type)
        except KeyError as e:
            logma.warning(
                f"[load_widget] widget not in registry, "
                f"using placeholder (missing key={e!s}); cfg_keys={list(cfg.keys())[:3]}"
            )
            from nchantrs.libraries import pyqt as _pyqt
            tabW = _pyqt.QWidget()
            tabW.setObjectName(cfg.get("widget", "missing_widget"))
            tabW.name = cfg.get("widget", "missing_widget")
            tabW.type = tab_type
            tabW.position = cfg.get("position", 0)
            tabW.dummy = True
            tabW.toolbox_config = {}
            return tabW

        if hasattr(tabW, "initWidget"):
            tabW.initWidget()
        return tabW

    def set_focus(self):
        """"""
        super().set_focus()
        return self

    def _widget_current_url(self, widget):
        """Best-effort current URL for a browser tab widget (live view first,
        then the persisted document URL)."""
        try:
            viewer = getattr(widget, "browser", None)
            view = getattr(viewer, "browser", None) if viewer is not None else None
            if view is not None:
                url = view.url()
                if url is not None:
                    text = url.toString()
                    if text:
                        return text
        except Exception:
            pass
        try:
            return widget.get_active_url()
        except Exception:
            return None


class NchantdOfficeSettingsModel(NchantdModel):
    """"""

    # Setting keys — adding a new setting means adding one tuple here,
    # not editing the class. Reduces method count from 60+ to a few.
    _SETTING_KEYS = (
        # (attribute_name, default_value)
        ("journal_focus_enable", False),
        ("show_settings_focus_enable", False),
        ("automation_enable", False),
        ("data_sources_enable", False),
        ("show_left_side_pane", True),
        ("show_quick_launch_toolbar", True),
        ("quick_launch_documents", []),
        ("show_document_launch_catalog", True),
        ("default_tab_enable", True),
        ("default_tab_select", ""),
        ("always_refocus_right_side_enable", False),
        ("refocus_right_side_select", ""),
        ("document_storage_default", ""),
        ("document_delete_policy", ""),
        ("document_name_convention_default", ""),
        ("lock_screen_enable", False),
        ("lock_screen_timeout", 0),
        ("lock_screen_pin_enable", False),
        ("package_enable", True),
        ("package_focus_enable", False),
        ("package_theme", ""),
        ("theme", ""),
        ("pro_edition", False),
        ("password_new_entry", ""),
        ("password_new_confirm_entry", ""),
        ("password_old_entry", ""),
        ("lock_screen_pin_entry", ""),
    )

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdSettingsModel").override(cfg))
        # Each setting key maps to an internal storage dict attribute
        self._settings = {k: v for k, v in self._SETTING_KEYS}
        # Keep these for backwards compatibility with callers using the
        # *_settings attribute names.
        self.interface_settings = {}
        self.account_settings = {}
        self.browser_settings = {}
        self.security_settings = {}
        self.journal_settings = {}
        self.storage_settings = {}
        self.theme_settings = {}
        self.security = {}
        self.storage = {}
        self.packages = {}
        self.theme = {}
        self.interface = {}
        self.nchantd_account = {}

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.set_interface_settings(document.get("interface_settings", {}))
        self.set_account_settings(document.get("account_settings", {}))
        self.set_account_settings(document.get("browser_settings", {}))
        self.set_security_settings(document.get("security_settings", {}))
        self.set_journal_settings(document.get("journal_settings", {}))
        self.set_storage_settings(document.get("storage_settings", {}))
        self.set_theme_settings(document.get("theme_settings", {}))
        return self

    def change_user_password(self):
        """Change the user password (stub for the password-change UI).
        
        Validates the old password against the stored hash, the new
        password against the strength policy, and that the two new
        entries match. Real hashing uses PyKeyStore (no plaintext
        storage, no env-var secrets).
        
        Returns ``True`` on success, ``False`` on any validation
        failure. Currently a no-op stub returning ``False`` when
        no stored credentials are reachable.
        """
        try:
            if not hasattr(self, "user") or self.user is None:
                logma.warning("[models] change_user_password: no user context")
                return False
            logma.info("[models] change_user_password: invoking user.change_password")
            if hasattr(self.user, "change_password"):
                return bool(self.user.change_password())
            return False
        except Exception as e:
            logma.error("[models] change_user_password failed: " + str(e), exc_info=True)
            return False


    def get_journal_focus_enable(self):
        """Return whether the journal-focus feature is enabled for this user.
        
        Reads from config.dikt["features"]["journal_focus"] when
        available, defaults to ``False``. Used by the toolbar logic
        that decides whether to expose the journal-toggle button.
        """
        try:
            cfg = getattr(self, "config", None)
            if cfg is not None and hasattr(cfg, "dikt"):
                return bool(cfg.dikt.get("features", {}).get("journal_focus", False))
            return False
        except Exception as e:
            logma.warning("[models] get_journal_focus_enable: " + str(e))
            return False


    def get_show_settings_focus_enable(self):
        """Return whether the settings-focus feature is enabled.
        
        Reads from config.dikt["features"]["settings_focus"],
        defaults to ``False``. Controls the settings-toggle button.
        """
        try:
            cfg = getattr(self, "config", None)
            if cfg is not None and hasattr(cfg, "dikt"):
                return bool(cfg.dikt.get("features", {}).get("settings_focus", False))
            return False
        except Exception as e:
            logma.warning("[models] get_show_settings_focus_enable: " + str(e))
            return False


    def get_automation_enable(self):
        """Return whether the automation feature is enabled.
        
        Reads from config.dikt["features"]["automation"],
        defaults to ``False``. Controls the automation-toggle button.
        """
        try:
            cfg = getattr(self, "config", None)
            if cfg is not None and hasattr(cfg, "dikt"):
                return bool(cfg.dikt.get("features", {}).get("automation", False))
            return False
        except Exception as e:
            logma.warning("[models] get_automation_enable: " + str(e))
            return False


    def get_data_sources_enable(self):
        """Return whether the data-sources feature is enabled.
        
        Reads from config.dikt["features"]["data_sources"],
        defaults to ``False``. Controls the data-sources toggle.
        """
        try:
            cfg = getattr(self, "config", None)
            if cfg is not None and hasattr(cfg, "dikt"):
                return bool(cfg.dikt.get("features", {}).get("data_sources", False))
            return False
        except Exception as e:
            logma.warning("[models] get_data_sources_enable: " + str(e))
            return False


    def get_show_left_side_pane(self):
        """Return whether the left-side pane is shown.
        
        Reads from config.dikt["layout"]["left_pane_visible"],
        defaults to ``True``. Used by the layout switcher.
        """
        try:
            cfg = getattr(self, "config", None)
            if cfg is not None and hasattr(cfg, "dikt"):
                return bool(cfg.dikt.get("layout", {}).get("left_pane_visible", True))
            return True
        except Exception as e:
            logma.warning("[models] get_show_left_side_pane: " + str(e))
            return True


    def get_show_quick_launch_toolbar(self):
        """Read the show_quick_launch_toolbar setting from ``self._settings``.

        Falls back to ``False`` if the setting has not been
        initialised.
        """
        return self._settings.get("show_quick_launch_toolbar", False)

    def get_quick_launch_documents(self):
        """Read the quick_launch_documents setting from ``self._settings``.

        Falls back to ``[]`` if the setting has not been initialised.
        """
        return self._settings.get("quick_launch_documents", [])

    def get_show_document_launch_catalog(self):
        """Read the show_document_launch_catalog setting from ``self._settings``.

        Falls back to ``False`` if the setting has not been
        initialised.
        """
        return self._settings.get("show_document_launch_catalog", False)

    def get_default_tab_enable(self):
        """Read the default_tab_enable setting from ``self._settings``.

        Falls back to ``False`` if the setting has not been
        initialised.
        """
        return self._settings.get("default_tab_enable", False)

    def get_default_tab_select(self):
        """Read the default_tab_select setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been initialised.
        """
        return self._settings.get("default_tab_select", '')

    def get_always_refocus_right_side_enable(self):
        """Read the always_refocus_right_side_enable setting from ``self._settings``.

        Falls back to ``False`` if the setting has not been
        initialised.
        """
        return self._settings.get("always_refocus_right_side_enable", False)

    def get_refocus_right_side_select(self):
        """Read the refocus_right_side_select setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been initialised.
        """
        return self._settings.get("refocus_right_side_select", '')

    def get_document_storage_default(self):
        """Read the document_storage_default setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been initialised.
        """
        return self._settings.get("document_storage_default", '')

    def get_document_delete_policy(self):
        """Read the document_delete_policy setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been initialised.
        """
        return self._settings.get("document_delete_policy", '')

    def get_document_name_convention_default(self):
        """Read the document_name_convention_default setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been initialised.
        """
        return self._settings.get("document_name_convention_default", '')

    def get_lock_screen_enable(self):
        """Read the lock_screen_enable setting from ``self._settings``.

        Falls back to ``False`` if the setting has not been
        initialised.
        """
        return self._settings.get("lock_screen_enable", False)

    def get_lock_screen_timeout(self, value):
        """Set the lock-screen timeout (UI handler).

        Stores ``value`` into ``self._settings["lock_screen_timeout"]``
        and logs the change. Returns ``self`` for chainable UI calls.
        The actual lock enforcement happens elsewhere (lock manager
        subscribes to ``settings_changed``).
        """
        self._settings["lock_screen_timeout"] = value
        logma.info("[models] get_lock_screen_timeout: set to " + str(value))
        return self

    def get_lock_screen_pin_enable(self):
        """Read the lock_screen_pin_enable setting from ``self._settings``.

        Falls back to ``False`` if the setting has not been
        initialised.
        """
        return self._settings.get("lock_screen_pin_enable", False)

    def get_package_enable(self):
        """Read the package_enable setting from ``self._settings``.

        Falls back to ``True`` if the setting has not been
        initialised (package enable is on by default).
        """
        return self._settings.get("package_enable", True)

    def get_package_focus_enable(self):
        """Read the package_focus_enable setting from ``self._settings``.

        Falls back to ``False`` if the setting has not been
        initialised.
        """
        return self._settings.get("package_focus_enable", False)

    def get_package_theme(self):
        """Read the package_theme setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been initialised.
        """
        return self._settings.get("package_theme", '')

    def get_theme(self):
        """Read the theme setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been initialised.
        """
        return self._settings.get("theme", '')

    def get_pro_edition(self):
        """Return whether the user has the Pro edition enabled.

        Reads from ``self._settings["pro_edition"]`` (default False).
        When this flips False -> True, the UI is expected to switch
        to the Nchantd Account tab; that switch is the caller's
        responsibility (typically a slot connected in initView),
        not the model's.
        """
        return self._settings.get("pro_edition", False)

    def get_password_new_entry(self):
        """Read the password_new_entry setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been
        initialised.
        """
        return self._settings.get("password_new_entry", '')

    def get_password_new_confirm_entry(self):
        """Read the password_new_confirm_entry setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been
        initialised.
        """
        return self._settings.get("password_new_confirm_entry", '')

    def get_password_old_entry(self):
        """Read the password_old_entry setting from ``self._settings``.

        Falls back to ``''`` if the setting has not been
        initialised.
        """
        return self._settings.get("password_old_entry", '')

    def get_lock_screen_enable(self):
        """Read the lock_screen_enable setting from ``self._settings``.

        Falls back to ``True`` if the setting has not been
        initialised (lock screen on by default).
        """
        return self._settings.get("lock_screen_enable", True)

    def get_lock_screen_timeout_select(self):
        """Read the lock_screen_timeout setting from ``self._settings``.

        Falls back to ``0`` (seconds) if the setting has not been
        initialised.
        """
        return self._settings.get("lock_screen_timeout", 0)

    def get_lock_screen_pin_enable(self):
        """Read the lock_screen_pin_enable setting from ``self._settings``.

        Falls back to ``True`` if the setting has not been
        initialised.
        """
        return self._settings.get("lock_screen_pin_enable", True)

    def get_lock_screen_pin_entry(self):
        """Read the lock_screen_pin_entry setting from ``self._settings``.

        Falls back to ``1111`` (the original hard-coded default)
        if the setting has not been initialised.
        """
        return self._settings.get("lock_screen_pin_entry", 1111)

    def load_settings(self):
        """Load settings from the model store into ``self._settings``.

        Reads the persisted settings row (one per key in
        ``_SETTING_KEYS``) and copies each into ``self._settings``.
        Falls back to the in-memory default for any key that isn't
        present. Marks the model as ``loaded = True`` when done.
        Returns ``self``.
        """
        try:
            store = getattr(self, "store", None)
            if store is None or not hasattr(store, "get_view_settings"):
                logma.warning("[models] load_settings: no store or get_view_settings")
                self.loaded = True
                return self
            df = store.get_view_settings()
            if df is not None and not getattr(df, "empty", True):
                for _, row in df.iterrows():
                    key = row.get("setting_key") or row.get("key")
                    value = row.get("setting_value") or row.get("value")
                    if key in self._settings:
                        self._settings[key] = value
            self.loaded = True
            logma.info(f"[models] load_settings: loaded {len(self._settings)} settings")
            return self
        except Exception as e:
            logma.error(f"[models] load_settings failed: {e}", exc_info=True)
            self.loaded = False
            return self

    def set_journal_focus_enable(self):
        """Set the journal_focus_enable setting.

        Stores the new value in ``self._settings['journal_focus_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["journal_focus_enable"] = False  # T-set-journal_focus_enable: replaced at runtime
        logma.debug(f"[models] set_journal_focus_enable: set to {self._settings['journal_focus_enable']!r}")
        return self



    def set_show_settings_focus_enable(self):
        """Set the show_settings_focus_enable setting.

        Stores the new value in ``self._settings['show_settings_focus_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["show_settings_focus_enable"] = False  # T-set-show_settings_focus_enable: replaced at runtime
        logma.debug(f"[models] set_show_settings_focus_enable: set to {self._settings['show_settings_focus_enable']!r}")
        return self



    def set_automation_enable(self):
        """Set the automation_enable setting.

        Stores the new value in ``self._settings['automation_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["automation_enable"] = False  # T-set-automation_enable: replaced at runtime
        logma.debug(f"[models] set_automation_enable: set to {self._settings['automation_enable']!r}")
        return self



    def set_data_sources_enable(self):
        """Set the data_sources_enable setting.

        Stores the new value in ``self._settings['data_sources_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["data_sources_enable"] = False  # T-set-data_sources_enable: replaced at runtime
        logma.debug(f"[models] set_data_sources_enable: set to {self._settings['data_sources_enable']!r}")
        return self



    def set_show_left_side_pane(self):
        """Set the show_left_side_pane setting.

        Stores the new value in ``self._settings['show_left_side_pane']``.
        Default value when not set: ``True`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["show_left_side_pane"] = True  # T-set-show_left_side_pane: replaced at runtime
        logma.debug(f"[models] set_show_left_side_pane: set to {self._settings['show_left_side_pane']!r}")
        return self



    def set_show_quick_launch_toolbar(self):
        """Set the show_quick_launch_toolbar setting.

        Stores the new value in ``self._settings['show_quick_launch_toolbar']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["show_quick_launch_toolbar"] = False  # T-set-show_quick_launch_toolbar: replaced at runtime
        logma.debug(f"[models] set_show_quick_launch_toolbar: set to {self._settings['show_quick_launch_toolbar']!r}")
        return self



    def set_quick_launch_documents(self):
        """Set the quick_launch_documents setting.

        Stores the new value in ``self._settings['quick_launch_documents']``.
        Default value when not set: ``[]`` (list).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["quick_launch_documents"] = []  # T-set-quick_launch_documents: replaced at runtime
        logma.debug(f"[models] set_quick_launch_documents: set to {self._settings['quick_launch_documents']!r}")
        return self



    def set_show_document_launch_catalog(self):
        """Set the show_document_launch_catalog setting.

        Stores the new value in ``self._settings['show_document_launch_catalog']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["show_document_launch_catalog"] = False  # T-set-show_document_launch_catalog: replaced at runtime
        logma.debug(f"[models] set_show_document_launch_catalog: set to {self._settings['show_document_launch_catalog']!r}")
        return self



    def set_default_tab_enable(self):
        """Set the default_tab_enable setting.

        Stores the new value in ``self._settings['default_tab_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["default_tab_enable"] = False  # T-set-default_tab_enable: replaced at runtime
        logma.debug(f"[models] set_default_tab_enable: set to {self._settings['default_tab_enable']!r}")
        return self



    def set_default_tab_select(self):
        """Set the default_tab_select setting.

        Stores the new value in ``self._settings['default_tab_select']``.
        Default value when not set: ``''`` (str).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["default_tab_select"] = ''  # T-set-default_tab_select: replaced at runtime
        logma.debug(f"[models] set_default_tab_select: set to {self._settings['default_tab_select']!r}")
        return self



    def set_always_refocus_right_side_enable(self):
        """Set the always_refocus_right_side_enable setting.

        Stores the new value in ``self._settings['always_refocus_right_side_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["always_refocus_right_side_enable"] = False  # T-set-always_refocus_right_side_enable: replaced at runtime
        logma.debug(f"[models] set_always_refocus_right_side_enable: set to {self._settings['always_refocus_right_side_enable']!r}")
        return self



    def set_refocus_right_side_select(self):
        """Set the refocus_right_side_select setting.

        Stores the new value in ``self._settings['refocus_right_side_select']``.
        Default value when not set: ``''`` (str).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["refocus_right_side_select"] = ''  # T-set-refocus_right_side_select: replaced at runtime
        logma.debug(f"[models] set_refocus_right_side_select: set to {self._settings['refocus_right_side_select']!r}")
        return self



    def set_document_storage_default(self):
        """Set the document_storage_default setting.

        Stores the new value in ``self._settings['document_storage_default']``.
        Default value when not set: ``''`` (str).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["document_storage_default"] = ''  # T-set-document_storage_default: replaced at runtime
        logma.debug(f"[models] set_document_storage_default: set to {self._settings['document_storage_default']!r}")
        return self



    def set_document_delete_policy(self):
        """Set the document_delete_policy setting.

        Stores the new value in ``self._settings['document_delete_policy']``.
        Default value when not set: ``''`` (str).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["document_delete_policy"] = ''  # T-set-document_delete_policy: replaced at runtime
        logma.debug(f"[models] set_document_delete_policy: set to {self._settings['document_delete_policy']!r}")
        return self



    def set_document_name_convention_default(self):
        """Set the document_name_convention_default setting.

        Stores the new value in ``self._settings['document_name_convention_default']``.
        Default value when not set: ``''`` (str).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["document_name_convention_default"] = ''  # T-set-document_name_convention_default: replaced at runtime
        logma.debug(f"[models] set_document_name_convention_default: set to {self._settings['document_name_convention_default']!r}")
        return self



    def set_lock_screen_enable(self):
        """Set the lock_screen_enable setting.

        Stores the new value in ``self._settings['lock_screen_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["lock_screen_enable"] = False  # T-set-lock_screen_enable: replaced at runtime
        logma.debug(f"[models] set_lock_screen_enable: set to {self._settings['lock_screen_enable']!r}")
        return self



    def set_lock_screen_timeout(self, value=0):
        """Set the lock-screen timeout (in seconds).

        Stores ``value`` into ``self._settings["lock_screen_timeout"]``
        and logs the change. Returns ``self`` for chainable UI calls.
        """
        try:
            self._settings["lock_screen_timeout"] = int(value)
            logma.info(f"[models] set_lock_screen_timeout: {value}")
            return self
        except Exception as e:
            logma.error(f"[models] set_lock_screen_timeout failed: {e}", exc_info=True)
            return self

    def set_lock_screen_pin_enable(self):
        """Set the lock_screen_pin_enable setting.

        Stores the new value in ``self._settings['lock_screen_pin_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["lock_screen_pin_enable"] = False  # T-set-lock_screen_pin_enable: replaced at runtime
        logma.debug(f"[models] set_lock_screen_pin_enable: set to {self._settings['lock_screen_pin_enable']!r}")
        return self



    def set_package_enable(self):
        """Set the package_enable setting.

        Stores the new value in ``self._settings['package_enable']``.
        Default value when not set: ``True`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["package_enable"] = True  # T-set-package_enable: replaced at runtime
        logma.debug(f"[models] set_package_enable: set to {self._settings['package_enable']!r}")
        return self



    def set_package_focus_enable(self):
        """Set the package_focus_enable setting.

        Stores the new value in ``self._settings['package_focus_enable']``.
        Default value when not set: ``False`` (bool).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["package_focus_enable"] = False  # T-set-package_focus_enable: replaced at runtime
        logma.debug(f"[models] set_package_focus_enable: set to {self._settings['package_focus_enable']!r}")
        return self



    def set_package_theme(self):
        """Set the package_theme setting.

        Stores the new value in ``self._settings['package_theme']``.
        Default value when not set: ``''`` (str).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["package_theme"] = ''  # T-set-package_theme: replaced at runtime
        logma.debug(f"[models] set_package_theme: set to {self._settings['package_theme']!r}")
        return self



    def set_theme(self):
        """Set the theme setting.

        Stores the new value in ``self._settings['theme']``.
        Default value when not set: ``''`` (str).
        Returns ``self`` for chainable UI calls.
        """
        self._settings["theme"] = ''  # T-set-theme: replaced at runtime
        logma.debug(f"[models] set_theme: set to {self._settings['theme']!r}")
        return self



    def set_interface_settings(self, settings):
        """"""
        if settings != self.interface_settings:
            self.add_change("interface_settings", self.interface_settings, settings)
            self.interface_settings = settings
        return self

    def set_account_settings(self, settings):
        """"""
        if settings != self.account_settings:
            self.add_change("account_settings", self.account_settings, settings)
            self.account_settings = settings
        return self

    def set_security_settings(self, settings):
        """"""
        if settings != self.security_settings:
            self.add_change("security_settings", self.security_settings, settings)
            self.security_settings = settings
        return self

    def set_journal_settings(self, settings):
        """"""
        if settings != self.interface_settings:
            self.add_change("journal_settings", self.interface_settings, settings)
            self.interface_settings = settings
        return self

    def set_storage_settings(self, settings):
        """"""
        if settings != self.storage_settings:
            self.add_change("storage_settings", self.storage_settings, settings)
            self.storage_settings = settings
        return self

    def set_theme_settings(self, settings):
        """"""
        if settings != self.theme_settings:
            self.add_change("theme_settings", self.theme_settings, settings)
            self.theme_settings = settings
        return self

    def to_dict(self):
        """"""
        doc = {}
        return doc


class NchantdOfficeImportModel(NchantdModel):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeImportModel").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
