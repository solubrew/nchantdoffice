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
from nchantrs.libraries import pyqt
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledDoubleSpinBox
from nchantrs.widgets.groups import NchantdGroup

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdNewObjectPane(NchantdPane):
    """T-066: object-launching wizard.

    Builds a small UI to pick an object type (Image / Chart /
    Form / Note / Document) and a position + size, then
    delegates the actual launch to ``self.app.model.codex`` via
    ``cmd_launch_object``. Returns a list of codex-initialised
    Documents to the caller.
    """

    # T-066: object-type -> codex-init-method map. Each entry is
    # the name of the codex method that initialises a fresh
    # document for the chosen object type. Adding a new object
    # type is as simple as registering a new (label, init_method)
    # tuple here.
    _OBJECT_INIT_METHODS = {
        "Image":    "init_image",
        "Chart":    "init_chart",
        "Form":     "init_form",
        "Note":     "init_note",
        "Document": "init_document",
        "Spreadsheet": "init_spreadsheet",
        "Notebook": "init_notebook",
    }

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdNewObjectPane").override(cfg))

    def initModel(self, cfg=None):
        """Load the list of launchable object types (T-066).

        Reads ``config.dikt['object_types']`` when set, falls
        back to the canonical list of built-in object types.
        """
        super().initModel(cfg)
        options = list(self._OBJECT_INIT_METHODS.keys())
        stored = self.config.dikt.get("object_types") if hasattr(self, "config") else None
        if stored:
            options = list(stored)
        self.config.dikt["object_options"] = options
        return self

    def cmd_launch_object(self, object_type=None, name=None, position=None, size=None, event=None, *args, **kwargs):
        """Launch a fresh in-app object via the application codex (T-066).

        Steps:
          1. Resolve the codex init-method for ``object_type``.
          2. Call ``self.app.model.codex.{init_method}`` with a
             dict payload including name + position + size.
          3. Add the new document to the active tabset via
             ``self.app.model.add_document_app``.

        Returns the new document (or ``None`` on failure).
        """
        try:
            object_type = (
                object_type
                or (self.config.dikt.get("last_object_type") if hasattr(self, "config") else None)
                or "Image"
            )
            init_method = self._OBJECT_INIT_METHODS.get(object_type)
            if not init_method:
                logma.warning(f"[objects] cmd_launch_object: unknown object_type {object_type!r}")
                return None
            model = getattr(self.app, "model", None) if hasattr(self, "app") else None
            if model is None or not hasattr(model, "codex") or model.codex is None:
                logma.warning("[objects] cmd_launch_object: no app.codex available")
                return None
            init_attr = getattr(model.codex, init_method, None)
            if not callable(init_attr):
                logma.warning(f"[objects] cmd_launch_object: codex.{init_method} unavailable")
                return None
            payload = {
                "did": uuid(),
                "name": name or f"{object_type}-{dt.datetime.utcnow().strftime('%H%M%S')}",
                "position": position or [0, 0],
                "size": size or [400, 300],
                "object_type": object_type,
            }
            document = init_attr(payload)
            if document is None:
                logma.warning(f"[objects] cmd_launch_object: {init_method} returned None")
                return None
            # Track + add to the active tabset via add_document_app
            if hasattr(self, "config"):
                self.config.dikt["last_object_type"] = object_type
            if hasattr(model, "add_document_app"):
                try:
                    model.add_document_app(
                        document.to_dict() if hasattr(document, "to_dict") else document,
                        payload["did"], 0, 0, object_type, {}, object_type.lower(), "center", "db", False,
                    )
                except Exception as e:
                    logma.error(f"[objects] cmd_launch_object add_document_app failed: {e}", exc_info=True)
            logma.info(f"[objects] cmd_launch_object: launched {object_type} -> did={payload['did']}")
            return document
        except Exception as e:
            logma.error(f"[objects] cmd_launch_object failed: {e}", exc_info=True)
            return None

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": "New Object: "}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"label": "Object Name: "}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        options = ["Image", "Chart"]
        cfg = {
            "label": "Select Object: ",
            "layout": "horizontal",
            "options": options,
        }
        self.new_object_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.new_object_select)
        cfg = {
            "label": "Set Position: ",
            "layout": "horizontal",
        }
        self.position_set = NchantdLabeledDoubleSpinBox(self, cfg).initWidget()
        layout.addWidget(self.position_set)
        cfg = {
            "label": "Set Size: ",
            "layout": "horizontal",
        }
        self.size_set = NchantdLabeledDoubleSpinBox(self, cfg).initWidget()
        layout.addWidget(self.size_set)
        cfg = {}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdHeaderPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdNewObjectPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": self.config.dikt.get("label", "Header: ")}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"label": "Header Text: "}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        options = ["Image", "Chart"]
        cfg = {
            "label": "Select Object: ",
            "layout": "horizontal",
            "options": options,
        }
        self.new_object_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.new_object_select)
        cfg = {}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdFooterPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdNewObjectPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": self.config.dikt.get("label", "Footer: ")}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"label": "Footer Text: "}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        options = ["Image", "Chart"]
        cfg = {
            "label": "Select Object: ",
            "layout": "horizontal",
            "options": options,
        }
        self.new_object_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.new_object_select)
        cfg = {}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
