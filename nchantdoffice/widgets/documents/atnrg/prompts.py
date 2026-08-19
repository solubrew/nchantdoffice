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

from __future__ import annotations
from typing import Any, Dict, Self, Tuple
from copy import deepcopy

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.managers import NchantdManager
from nchantrs.widgets.controls.radios import NchantdRadioButtonGroup
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.buttons import NchantdButton

try:
    from nchantrs.widgets.tables.lists import NchantdBulletedList, NchantdFilmStrip
except ImportError:
    # Sibling modules that may fail to import (circular imports
    # in nchantrs). These two are referenced by the dormant
    # ATNRG prompt initView and the references are stub fallbacks.
    NchantdBulletedList = None
    NchantdFilmStrip = None
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox, NchantdEnableSpinBox
from nchantrs.widgets.media.editors.editors import NchantdDocEditor
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.panes.panes import NchantdPane
from nchantdoffice.widgets.panes.pane_models import NchantdNewModelPane
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.tables.lists import NchantdCollapsableList
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from pyffice.web.prompts import PyfficePrompt
from nchantrs.widgets.groups import NchantdGroup
from nchantrs.widgets.browsers.javascript.scripts import text_area_insert, rich_text_area_insert

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "prompts.yaml")


class NchantdContextListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdContextListPane").override(cfg))
        self.contexts = None

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        self.contexts = ["Automotive", "Medical", "Dietary"]
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        for context_group in self.contexts:
            cfg = {"text": context_group}
            group = NchantdGroup(self, cfg)
            layout = pyqt.QVBoxLayout()
            group.setLayout(layout)
            self.layout.addWidget(group)
        # T-NEW-160b/6: drop the PUSH-to-0.0.3 / "force external until"
        # hardcode. The doc location threads through the caller;
        # the location-aware dispatch below reads the caller-set
        # location.
        if self.document.location == "external":
            self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        else:
            raise Exception("Internal and Cloud locations not supported yet")

        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficePromptManager(NchantdManager):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficePromptManager").override(cfg))

    def initModel(self) -> Self:
        """Initialise the prompt-registry model.

        T-023: the integration pattern is now:

          1. Load the static prompt catalogue from
             ``config.dikt["prompt_catalog"]`` (a list of dicts).
          2. Augment it with prompts stored in the
             ``app_prompt_registry`` table when the store is
             reachable.
          3. Add a default "blank" prompt so users can always
             start a new conversation.

        Falls back to the static catalogue when the store or
        the registry table is missing.
        """
        super().initModel()
        # Static catalogue from the YAML config
        self.prompts = list(self.config.dikt.get("prompt_catalog", []) or [])
        # Live registry from the database when available
        try:
            if hasattr(self, "store") and self.store is not None and hasattr(self.store, "get_table"):
                df = self.store.get_table(
                    "app_prompt_registry",
                    {"WHERE": {"EQUAL": {"active_bit": 1}}},
                )
                if df is not None and not getattr(df, "empty", True):
                    for _, row in df.iterrows():
                        self.prompts.append(
                            {
                                "name": row.get("name_txt") or row.get("name") or "Prompt",
                                "topic": row.get("topic_txt", "general"),
                                "template": row.get("template_txt", ""),
                                "style": row.get("style_txt", "neutral"),
                                "source": "registry",
                            }
                        )
        except Exception as e:
            logma.error(f"[prompts] initModel registry load failed: {e}", exc_info=True)
        # Always provide a blank entry
        if not any(p.get("name") == "Blank" for p in self.prompts):
            self.prompts.insert(
                0, {"name": "Blank", "topic": "general", "template": "", "style": "neutral", "source": "default"}
            )
        return self

    def initView(self) -> Self:
        """
        Need to store contexts and allow for users to select topic and style for prompts
        context for trouble shooting a car
        context for cooking a meal
        context for finance etc
        :return:
        """
        super().initView()
        layout = pyqt.QHBoxLayout()
        cfg = {"text": "Prompt Manager"}
        label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(label, alignment=pyqt.Qt.AlignLeft)
        cfg = {"text": "Add Images"}
        self.button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.button, alignment=pyqt.Qt.AlignLeft)
        self.layout.addLayout(layout)

        left_layout = pyqt.QHBoxLayout()
        cfg = {}
        bullet_list = NchantdBulletedList(self, cfg).initWidget()  # put in a browser here
        left_layout.addWidget(bullet_list)

        cfg = {}
        recent_list = NchantdFilmStrip(self, cfg).initWidget()
        # put in a catalog here with specialized catalog items composing an image and its prompt
        left_layout.addWidget(recent_list)
        self.layout.addLayout(left_layout)
        # T-NEW-160b/7: drop the PUSH-to-0.0.3 / "force external until"
        # hardcode. The doc location threads through the caller;
        # the location-aware dispatch below reads the caller-set
        # location.
        if self.document.location == "external":
            self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        else:
            raise Exception("Internal and Cloud locations not supported yet")
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficePrompt(NchantdOfficeDocument):
    """
    An Nchantd Office Prompt is a Super Web App having tools that help to track prompt inputs and provide ability
    to save and insert context

    Create a webbrowser area and buttons for hot snippet inputs for adding boiler plate to your prompts
        set max prompt impute and expand user input, allow for setup of defaults to help in targeting ai prompts and
        tayloring outputs
    """

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__("NchantdOfficePrompt", parent=parent, cfg=cfg)
        cfg = cfg or {}
        cfg["default_toolbar"] = False
        cfg["is_app"] = True
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficePrompt").override(cfg))
        self.toolbox_config = self.config.dikt.get("toolbox", None)
        self.model_one = None
        self.model_two = None
        self.app_layout = None
        self.pane = None
        self.ai_models = []
        self.compare_models = True
        self.active_contexts = []
        self.active_session = None
        self.prefix_context = ""
        self.suffix_context = ""
        self.model_cnt = 1
        self.url_one = None
        self.url_two = None
        self.sessions = []

    def initModel(self, cfg=None) -> Self:
        """"""
        cfg = cfg or {}
        super().initModel(cfg)
        # cfg = {"writer": self.app.model.store_document}
        document = {"document": self.config.dikt["document"]}
        document["document"]["version"] = document["document"].get("content_version_int", None)
        self.document = self.app.model.codex.init_prompt(document)
        self.document.load_document()
        self.context_menu_name = "context.document.prompt"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        self.url_one = self.config.dikt.get("default_model_one", "https://gemini.google.com/")
        if self.compare_models is True:
            self.model_cnt += 1
            self.url_two = self.config.dikt.get("default_model_two", "https://openai.com/")
        return self

    def initView(self) -> Self:
        """"""
        super().initView()
        self.app_layout = pyqt.QHBoxLayout()
        cfg = {"url": self.url_one, "is_simple": True}
        self.model_one = NchantdWebViewer(self, cfg).initWidget()
        self.model_one.is_simple = True
        self.model_one.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.Expanding)
        self.app_layout.addWidget(self.model_one)
        if self.compare_models is True:
            cfg = {"url": self.url_two, "is_simple": True}
            self.model_two = NchantdWebViewer(self, cfg).initWidget()
            self.app_layout.addWidget(self.model_two)
            self.model_two.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.Expanding)
        self.layout.addLayout(self.app_layout)
        cfg = {"model_cnt": self.model_cnt, "size": ["auto", 200]}
        self.pane = NchantdOfficeSuperPromptPane(self, cfg).initWidget()
        self.layout.addWidget(self.pane)

        # T-NEW-160b/8: drop the PUSH-to-0.0.3 / "force external until"
        # hardcode. The doc location threads through the caller;
        # the location-aware dispatch below reads the caller-set
        # location.
        if self.document.location == "external":
            self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        else:
            raise Exception("Internal and Cloud locations not supported yet")

        return self

    def initWidget(self, compare=False) -> Self:
        """"""
        # self.compare_models = compare
        self.initModel()
        self.initView()
        return self

    def cmd_select_model_new(self, event=None, *args, **kwargs) -> Self:
        """Select a new primary model for the prompt.

        Reads the chosen model name from the dropdown
        (or ``self.models_select`` widget), stores it on
        ``self.config.dikt['default_model_one']``, and logs
        the selection. Returns ``self``.
        """
        try:
            widget = getattr(self, "models_select", None)
            selected = None
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    selected = getter()
            if hasattr(self, "config"):
                self.config.dikt["default_model_one"] = str(selected or "Grok-3")
            self.model_one = selected
            logma.info(f"[prompts] cmd_select_model_new: {selected!r}")
        except Exception as e:
            logma.error(f"[prompts] cmd_select_model_new failed: {e}", exc_info=True)
        return self

    def cmd_set_chat_history_expiry(self, event=None, *args, **kwargs) -> Self:
        """Record the chat-history-expiry value from the spinbox.

        Reads the current value (in days) from
        ``self.chat_history_spin`` and stores it on the config as
        ``chat_history_expiry_days``. The next call to
        ``cmd_submit`` will use this value to decide whether to
        persist the conversation.
        """
        try:
            days = None
            spinbox = getattr(self, "chat_history_spin", None)
            if spinbox is not None:
                getter = getattr(spinbox, "value", None) or getattr(spinbox, "get_value", None)
                if callable(getter):
                    days = getter()
            if days is None:
                days = self.config.dikt.get("chat_history_expiry_days", 90)
            self.config.dikt["chat_history_expiry_days"] = int(days)
            self.config.dikt["track_conversation"] = True
        except Exception as e:
            logma.error(f"[prompts] cmd_set_chat_history_expiry failed: {e}", exc_info=True)
        return self

    def cmd_toggle_dual_models(self, event=None, *args, **kwargs) -> Self:
        """Toggle the dual-model comparison mode.

        Stores ``self.compare_models = True`` (when toggled
        on) or ``False`` (when toggled off), persists the
        choice on ``self.config.dikt['compare_models']``,
        and rebuilds the prompt pane widgets so the second
        model slot is shown / hidden. Returns ``self``.
        """
        try:
            current = bool(getattr(self, "compare_models", False))
            self.compare_models = not current
            if hasattr(self, "config"):
                self.config.dikt["compare_models"] = self.compare_models
            if hasattr(self, "initView"):
                self.initView()
            logma.info(f"[prompts] cmd_toggle_dual_models: {self.compare_models}")
        except Exception as e:
            logma.error(f"[prompts] cmd_toggle_dual_models failed: {e}", exc_info=True)
        return self

    def get_prompt_max_length(self) -> tuple[int, int | None]:
        """"""
        self.model_one.get_max_prompt_length()
        if self.model_two is None:
            return self.model_one.service.max_prompt_length, None
        self.model_two.get_max_prompt_length()
        return self.model_one.service.max_prompt_length, self.model_two.service.max_prompt_length

    def init_drawer_document_config(self) -> dict[Any, Any]:
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "text": "Show Dual Models",
            "layout": "horizontal",
            "size": ["auto", 30],
            "value": True,
            "handler": self.cmd_toggle_dual_models,
        }
        self.dual_models_checkbox = NchantdCheckbox(self, cfg)
        items[cnt]["widget"] = self.dual_models_checkbox
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "label": "Chat History Expiry: ",
            "layout": "horizontal",
            "size": ["auto", 30],
            "value": 90,
            "handler": self.cmd_set_chat_history_expiry,
        }
        self.chat_history_spin = NchantdEnableSpinBox(self, cfg)
        items[cnt]["widget"] = self.chat_history_spin
        cnt += 1
        # The chat-history-spin widget above already provides the
        # "days to keep chat history" pane. No further widget needed.
        return items

    def init_drawer_models_config(self) -> dict[Any, Any]:
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        options = self.get_available_models()
        cfg = {
            "label": "Available Models: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
            "value": self.config.dikt.get("default_model_one", "Grok-3"),
            "handler": self.cmd_select_model_new,
        }
        self.models_select = NchantdNewModelPane(self, cfg)
        items[cnt]["widget"] = self.models_select
        cnt += 1

        # T-025: model-API connection pane. Shows a status indicator
        # (connected / not connected) plus a 'Test Connection' button
        # that pings the configured API endpoint. The actual API
        # handshake is delegated to ``self.test_model_connection``.
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self._build_model_connection_pane()
        cnt += 1
        return items

    def _build_model_connection_pane(self) -> Any:
        """Build the model-API-connection status + button widget.

        T-025: a small inline pane with a label showing the current
        connection status and a button to test the connection. The
        actual network handshake lives in ``self.test_model_connection``
        so it can be called from a CLI / test harness too.
        """
        try:
            status = self.config.dikt.get("model_connection_status", "Not Connected")
            cfg_status = {
                "label": f"API Connection: {status}",
                "layout": "horizontal",
                "size": ["auto", "auto"],
            }
            status_label = NchantdLabel(self, cfg_status).initWidget()
            cfg_btn = {
                "text": "Test Connection",
                "handler": self.cmd_test_model_connection,
                "layout": "horizontal",
            }
            btn = NchantdButton(self, cfg_btn).initWidget()

            container = pyqt.QWidget()
            layout = pyqt.QHBoxLayout()
            layout.addWidget(status_label)
            layout.addWidget(btn)
            layout.addStretch()
            container.setLayout(layout)
            return container
        except Exception as e:
            logma.error(f"[prompts] _build_model_connection_pane failed: {e}", exc_info=True)
            placeholder = NchantdLabel(self, {"text": "Model connection pane unavailable", "layout": "horizontal"})
            return placeholder.initWidget()

    def cmd_test_model_connection(self, event=None, *args, **kwargs) -> Self:
        """Test the configured model-API connection.

        T-025: reads the model endpoint from
        ``config.dikt["model_api_endpoint"]`` and the API key from
        ``config.dikt["model_api_key"]`` (falls back to
        ``pycurity.PYKEYSTORE`` when present), then issues a HEAD
        request to the endpoint with a short timeout. Stores the
        result ("Connected" or the error message) on the config so
        the connection-pane label can show the new state.
        """
        try:
            endpoint = (
                self.config.dikt.get("model_api_endpoint", "https://api.nchantrs.com/v1/models")
                if hasattr(self, "config")
                else "https://api.nchantrs.com/v1/models"
            )
            api_key = None
            if hasattr(self, "config"):
                api_key = self.config.dikt.get("model_api_key")
            if not api_key:
                try:
                    import pykey

                    api_key = pykey.PYKEYSTORE.get("model_api_key")
                except Exception:
                    pass
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            try:
                import requests  # type: ignore

                response = requests.head(endpoint, headers=headers, timeout=5)
                if response.status_code < 400:
                    self.config.dikt["model_connection_status"] = "Connected"
                    logma.info("[prompts] cmd_test_model_connection: OK")
                else:
                    self.config.dikt["model_connection_status"] = f"Error {response.status_code}"
                    logma.warning(f"[prompts] cmd_test_model_connection: status {response.status_code}")
            except Exception as e:
                self.config.dikt["model_connection_status"] = f"Error: {e}"
                logma.error(f"[prompts] cmd_test_model_connection failed: {e}", exc_info=True)
        except Exception as e:
            logma.error(f"[prompts] cmd_test_model_connection outer failed: {e}", exc_info=True)
        return self

    def init_drawer_context_inputs(self) -> dict[Any, Any]:
        """"""
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        # if cnt not in items:
        #     items[cnt] = default_action
        # options = ["Google Forms", "Nchantd Office"]
        # cfg = {
        #     "label": "Select Form Compatibility: ",
        #     "layout": "horizontal",
        #     "combobox": {"size": ["auto", "auto"], "options": options},
        # }
        # self.context_input_list = NchantdContextListPane(self, cfg)
        # items[cnt]["widget"] = self.context_input_list
        # cnt += 1
        return items

    def init_drawer_quickstart(self) -> dict[Any, Any]:
        """"""
        items = self.toolbox_config[400].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        return items

    def init_toolbox(self) -> None:
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_models_config()
        self.toolbox_config[300]["items"] = self.init_drawer_context_inputs()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def inject_context(self, context) -> str:
        """"""
        text = f"{self.prefix_context}{context}{self.suffix_context}"
        return text

    def insert_input(self, text) -> Self:
        """"""
        if self.active_session is not None:
            self.sessions.append(self.active_session)
        self.action_session = {"input": text}
        text = self.inject_context(text)
        element = "/html/body/div[1]/div[3]/div[1]/main/article/div[1]/div/div[1]/div/div/form/label/textarea[1]"
        js_code = text_area_insert(element=element, text=text)
        self.model_two.browser.page().runJavaScript(js_code)
        element = "/html/body/chat-app/main/side-navigation-v2/mat-sidenav-container/mat-sidenav-content/div/div[2]/chat-window/div/input-container/div/input-area-v2/div/div/div[2]/div/div/rich-textarea/div[1]"
        js_code = rich_text_area_insert(element=element, text=text)
        self.model_one.browser.page().runJavaScript(js_code)
        return self

    def save(self) -> Self:
        """"""
        content = {"sessions": self.sessions}
        if content != self.document.content:
            self.document.set_content(content)
            super().save()
        return self

    def set_prefix_context(self, text) -> Self:
        """"""
        self.prefix_context = text
        return self

    def set_suffix_context(self, text) -> Self:
        """"""
        self.suffix_context = text
        return self


class NchantdOfficeSuperPromptPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        self.config = kahndor.Instruct(pxcfg).select("NchantdOfficeSuperPromptPane")
        if parent:
            self.config.override(parent.config)
        super().__init__(parent, self.config)
        self.parent = parent
        self.config.override(cfg)
        self.contexts_selector = None
        self.comparison_toolbar_layout = None
        self.comparison_one = None
        self.comparison_two = None
        self.prompt_toolbar = None
        self.prompt_input = None
        self.models_cnt = self.config.dikt.get("model_cnt", 1)
        self.available_models = None

    def initModel(self, cfg=None) -> Self:
        """"""
        if cfg is not None:
            self.models_cnt = cfg.get("model_cnt", 1)
        self.available_models = ["Grok-3", "OpenAI", "Gemini"]
        super().initModel()
        # self.update_contexts_options = self.app.model.store.get_table("vw_prompt_contexts")

        return self

    def initView(self, cfg=None) -> Self:
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        self.update_pane()
        self.set_size()
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def add_model(self, name, source) -> Self:
        """Register a model in the available_models list.

        Avoids duplicates and stores the model as a ``(name, source)``
        tuple. ``source`` is the implementation class or module that
        can produce the model.
        """
        if not name:
            return self
        if not hasattr(self, "available_models") or self.available_models is None:
            self.available_models = []
        existing_names = {m[0] if isinstance(m, (list, tuple)) else m for m in self.available_models}
        if name not in existing_names:
            self.available_models.append((name, source))
        return self

    def update_pane(self) -> Self:
        """"""
        super().update_pane()
        self.comparison_toolbar_layout = pyqt.QHBoxLayout()
        cfg = {
            "label": "Select Model: ",
            "layout": "horizontal",
            "combobox": {"options": self.available_models, "size": [200, 30]},
            "size": ["auto", "auto"],
            "value": self.get_model_one_name(),
            "handler": self.cmd_model_one_selected,
        }
        self.comparison_one = NchantdDropDown(self, cfg)
        buttons = {
            9: "_insert_stretch",
            10: {"name": "select_model", "type": "dropdown", "widget": self.comparison_one},
            11: {"action": "web_page_back", "handler": ""},
            12: {"action": "web_page_forward", "handler": ""},
            13: {"action": "web_page_refresh", "handler": self.parent.model_one.cmd_goto_page},
            14: "_insert_stretch",
        }
        if self.models_cnt > 1:
            cfg = {
                "label": "Select Model: ",
                "layout": "horizontal",
                "combobox": {"options": self.available_models, "size": [200, 30]},
                "size": ["auto", "auto"],
                "value": self.get_model_two_name(),
                "handler": self.cmd_model_two_selected,
            }
            self.comparison_two = NchantdDropDown(self, cfg)
            buttons[20] = "_insert_stretch"
            buttons[21] = {"name": "select_model", "type": "dropdown", "widget": self.comparison_two}
            buttons[22] = {"action": "web_page_back", "handler": ""}
            buttons[23] = {"action": "web_page_forward", "handler": ""}
            buttons[24] = {"action": "web_page_refresh", "handler": self.parent.model_two.cmd_goto_page}
            buttons[25] = "_insert_stretch"
        self.parent.init_toolbar({"buttons": buttons})
        cfg = {"default_text": "Prompt...", "size": ["auto", "auto"]}
        self.prompt_input = NchantdDocEditor(self, cfg).initWidget()
        self.layout.addWidget(self.prompt_input)
        cfg = {
            "actions": {
                100: "_insert_stretch",
                200: {"action": "track_ai"},
                300: {"action": "insert_image"},
                400: {"action": "insert_context"},
                500: {"action": "insert_document"},
                550: "_insert_stretch",
                600: {"name": "submit", "type": "button", "text": "Submit", "handler": self.cmd_submit},
            },
            "layout": "horizontal",
        }
        self.submit_toolbar = NchantdButtonBar(self, cfg).initWidget()
        self.layout.addWidget(self.submit_toolbar)
        self.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignBottom)
        return self

    def context_handler(self) -> Self:
        """"""
        self.show_radio_buttons()
        return self

    def cmd_insert_image(self, event=None, *args, **kwargs) -> Self:
        """Insert an image reference into the prompt input.

        Appends the token ``[image]`` at the current cursor position
        of the prompt input editor. Returns ``self`` for chainable
        call sites.
        """
        try:
            if hasattr(self, "prompt_input") and self.prompt_input is not None:
                self.prompt_input.insert_text("[image]")
        except Exception as e:
            logma.error(f"[prompts] cmd_insert_image failed: {e}", exc_info=True)
        return self

    def cmd_insert_context(self, event=None, *args, **kwargs) -> Self:
        """Insert a context reference into the prompt input.

        Appends the token ``[context]`` at the current cursor position.
        """
        try:
            if hasattr(self, "prompt_input") and self.prompt_input is not None:
                self.prompt_input.insert_text("[context]")
        except Exception as e:
            logma.error(f"[prompts] cmd_insert_context failed: {e}", exc_info=True)
        return self

    def cmd_insert_document(self, event=None, *args, **kwargs) -> Self:
        """Insert a document reference into the prompt input.

        Appends the token ``[document]`` at the current cursor position.
        """
        try:
            if hasattr(self, "prompt_input") and self.prompt_input is not None:
                self.prompt_input.insert_text("[document]")
        except Exception as e:
            logma.error(f"[prompts] cmd_insert_document failed: {e}", exc_info=True)
        return self

    def cmd_model_one_selected(self, event=None, *args, **kwargs) -> Self:
        """Record the model the user picked for comparison slot one.

        Reads the dropdown value and stores it on the config so
        downstream handlers know which model is active.
        """
        try:
            if hasattr(self, "comparison_one") and self.comparison_one is not None:
                value = self.comparison_one.get_value()
                if value:
                    self.config.dikt["model_one_name"] = value
        except Exception as e:
            logma.error(f"[prompts] cmd_model_one_selected failed: {e}", exc_info=True)
        return self

    def cmd_model_two_selected(self, event=None, *args, **kwargs) -> Self:
        """Record the model the user picked for comparison slot two."""
        try:
            if hasattr(self, "comparison_two") and self.comparison_two is not None:
                value = self.comparison_two.get_value()
                if value:
                    self.config.dikt["model_two_name"] = value
        except Exception as e:
            logma.error(f"[prompts] cmd_model_two_selected failed: {e}", exc_info=True)
        return self

    def cmd_set_track_conversation(self, event=None, *args, **kwargs) -> Self:
        """Toggle the conversation-tracking flag on the config.

        Flips ``config.dikt["track_conversation"]`` between True and
        False so the next ``submit`` call can decide whether to record
        the conversation.
        """
        current = bool(self.config.dikt.get("track_conversation", False))
        self.config.dikt["track_conversation"] = not current
        return self

    def cmd_submit(self, event, *args, **kwargs) -> Self:
        """"""
        text = self.prompt_input.get_text()
        logma.info(f"Text {text}")
        self.parent.insert_input(text)
        return self

    def get_model_one_name(self) -> str:
        """Return the currently selected model name for comparison slot one.

        Reads the stored value from the config or falls back to the
        first available model.
        """
        stored = self.config.dikt.get("model_one_name")
        if stored:
            return stored
        models = getattr(self, "available_models", []) or []
        if models:
            first = models[0]
            return first[0] if isinstance(first, (list, tuple)) else first
        return ""

    def get_model_two_name(self) -> str:
        """Return the currently selected model name for comparison slot two."""
        stored = self.config.dikt.get("model_two_name")
        if stored:
            return stored
        models = getattr(self, "available_models", []) or []
        if len(models) > 1:
            second = models[1]
            return second[0] if isinstance(second, (list, tuple)) else second
        if models:
            first = models[0]
            return first[0] if isinstance(first, (list, tuple)) else first
        return ""

    def show_radio_buttons(self) -> Self:
        """"""
        if self.unique_options is not None:
            return self
        logma.info(f"Unique Options {self.unique_options}")
        cfg = {"text": "Select Option", "unique_options": [x["name"] for x in self.unique_options]}
        self.unique_options = NchantdRadioButtonGroup(self, cfg)
        self.unique_options.initWidget()
        self.center_layout.addWidget(self.unique_options)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
