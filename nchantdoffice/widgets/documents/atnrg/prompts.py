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

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdContextListPane").override(cfg))
        self.contexts = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.contexts = ["Automotive", "Medical", "Dietary"]
        return self

    def initView(self, cfg=None):
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
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# TODO: unsure how to integrate this at the moment
class NchantdOfficePromptManager(NchantdManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficePromptManager").override(cfg))

    def initModel(self):
        """"""
        super().initModel()

        return self

    def initView(self):
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

        return self

    def initWidget(self):
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

    def __init__(self, parent=None, cfg=None):
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

    def initModel(self, cfg=None):
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

    def initView(self):
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
        return self

    def initWidget(self, compare=False):
        """"""
        # self.compare_models = compare
        self.initModel()
        self.initView()
        return self

    def cmd_select_model_new(self, event, *args, **kwargs):
        """"""
        # TODO: implement method
        return self

    def cmd_set_chat_history_expiry(self, event, *args, **kwargs):
        """"""
        # TODO: implement method
        return self

    def cmd_toggle_dual_models(self, event, *args, **kwargs):
        """"""
        # TODO: implement method
        return self

    def get_prompt_max_length(self):
        """"""
        self.model_one.get_max_prompt_length()
        if self.model_two is None:
            return self.model_one.service.max_prompt_length, None
        self.model_two.get_max_prompt_length()
        return self.model_one.service.max_prompt_length, self.model_two.service.max_prompt_length

    def init_drawer_document_config(self):
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
        # TODO need a pane to allow setting of days to keep chat history
        return items

    def init_drawer_models_config(self):
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
        # TODO: show either a connection available or create connection to handle apis for the model
        return items

    def init_drawer_context_inputs(self):
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

    def init_drawer_quickstart(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_models_config()
        self.toolbox_config[300]["items"] = self.init_drawer_context_inputs()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def inject_context(self, context):
        """"""
        text = f"{self.prefix_context}{context}{self.suffix_context}"
        return text

    def insert_input(self, text):
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

    def save(self):
        """"""
        content = {"sessions": self.sessions}
        if content != self.document.content:
            self.document.set_content(content)
            super().save()
        return self

    def set_prefix_context(self, text):
        """"""
        self.prefix_context = text
        return self

    def set_suffix_context(self, text):
        """"""
        self.suffix_context = text
        return self


class NchantdOfficeSuperPromptPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
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

    def initModel(self, cfg=None):
        """"""
        if cfg is not None:
            self.models_cnt = cfg.get("model_cnt", 1)
        self.available_models = ["Grok-3", "OpenAI", "Gemini"]
        super().initModel()
        # self.update_contexts_options = self.app.model.store.get_table("vw_prompt_contexts")

        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        self.update_pane()
        self.set_size()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_model(self, name, source):
        """"""
        # NOTE:  will need to get configurations from user or NchantdService
        #  will need to get apikey if available

    def update_pane(self):
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

    def context_handler(self):
        """"""
        self.show_radio_buttons()
        return self

    def cmd_insert_image(self, event, *args, **kwargs):
        """"""

    def cmd_insert_context(self, event, *args, **kwargs):
        """"""

    def cmd_insert_document(self, event, *args, **kwargs):
        """"""

    def cmd_model_one_selected(self, event, *args, **kwargs):
        """"""

    def cmd_model_two_selected(self, event, *args, **kwargs):
        """"""

    def cmd_set_track_conversation(self, event, *args, **kwargs):
        """"""

    def cmd_submit(self, event, *args, **kwargs):
        """"""
        text = self.prompt_input.get_text()
        logma.info(f"Text {text}")
        self.parent.insert_input(text)
        return self

    def get_model_one_name(self):
        """"""

    def get_model_two_name(self):
        """"""

    def show_radio_buttons(self):
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
