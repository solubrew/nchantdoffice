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

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "utilities.yaml")


def lookup_widget(doc_type):
    """"""
    # match doc_type:
    #     case "add_browser_document_nchantdbrowser":
    #         widget = "widgets.documents.atnrg.browsers.browsers.NchantdOfficeWebBrowser"
    #     case "add_note_attachment_nchantdnote":
    #         widget = "widgets.documents.media.notes.NchantdOfficeNote"
    #     case "add_superweb_custom_nchantdprompt":
    #         widget = "widgets.documents.atnrg.prompts.NchantdOfficePrompt"
    #     case "add_script_document_nchantdscript":
    #         widget = "widgets.documents.media.scripts.NchantdOfficeScript"
    #     case "add_http_media_canva":
    #         widget = "widgets.documents.atnrg.browsers.browsers.NchantdOfficeWebBrowser"
    #     case "add_http_media_notion":
    #         widget = "widgets.documents.atnrg.browsers.browsers.NchantdOfficeWebBrowser"
    #     case "add_http_media_scenarioai":
    #         widget = "widgets.documents.atnrg.browsers.browsers.NchantdOfficeWebBrowser"
    #     case "add_http_media_leonardoai":
    #         widget = "widgets.documents.atnrg.browsers.browsers.NchantdOfficeWebBrowser"
    if doc_type == "browser":
        widget = "widgets.documents.atnrg.browsers.browsers.NchantdOfficeWebBrowser"
    elif doc_type == "calendar":
        widget = "widgets.documents.calendars.NchantdOfficeCalendar"
    elif doc_type == "chart":
        widget = "widgets.documents.analytics.charts.NchantdOfficeChart"
    elif doc_type == "dataset":
        widget = "widgets.documents.analytics.sources.NchantdOfficeDataset"
    elif doc_type == "form":
        widget = "widgets.documents.media.graphics.forms.NchantdOfficeForm"
    elif doc_type == "image":
        widget = "widgets.documents.media.graphics.images.NchantdOfficeImage"
    elif doc_type == "matrix":
        widget = "widgets.documents.workbooks.matrices.NchantdOfficeMatrix"
    elif doc_type == "note":
        widget = "widgets.documents.media.notes.NchantdOfficeNote"
    elif doc_type == "pdf":
        widget = "widgets.documents.media.pdfs.NchantdOfficePDF"
    elif doc_type == "prompt":
        widget = "widgets.documents.atnrg.prompts.NchantdOfficePrompt"
    elif doc_type == "sketch":
        widget = "widgets.documents.media.graphics.sketches.NchantdOfficeSketch"
    else:
        widget = "widgets.documents.media.scripts.NchantdOfficeScript"
    # TODO: this needs to access the database to get the widget name add a list here is defeating the purpose
    return widget


def document_lookup(app, action, cfg=None, deep=False, refresh=False):
    """Lookup document types."""
    pxcfg = kahndor.Instruct(join(here, "../actions", "_data_", "actions.yaml")).override(cfg).dikt
    table = "app_document_type"
    cfg = next(app.model.store.docs["dbc"].read(table))
    # logma.info(f"Lookups {cfg}")
    if cfg is None or refresh:
        params = {"table": [table]}
        db_cfg = {"WHERE": {"EQUAL": {"code_group_txt": pxcfg["action_type"]}}}
        actions = next(app.model.store.docs["db"].read(params, db_cfg))
        cfg = actions.dikt["app_action"]["df"].to_dict("records")
        cfg = {c["lookup_code_txt"]: c for c in cfg}
        # logma.info(f"Lookups {cfg}")
        app.model.store.docs["dbc"].write({table: cfg})


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
