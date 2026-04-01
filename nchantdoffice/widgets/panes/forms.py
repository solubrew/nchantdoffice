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
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxGroup
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "forms.yaml")


class NchantdNewFormItemPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)
        self.compatibility = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView({"layout": "horizontal"})
        logma.info(f"New Form Item Pane:")
        cfg = {
            "label": "Enter Inquiry Text: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "entrybox": {"size": ["auto", 60]},
        }
        self.entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.left_side_layout.addWidget(self.entry)
        cfg = {"layout": "horizontal"}
        buttons = {
            0: "_insert_stretch",
            1: {"action": "set_entry_type_text", "handler": self.cmd_on_click_text_response},
            2: {"action": "set_entry_type_date", "handler": self.cmd_on_click_date_response},
            3: {"action": "set_entry_type_time", "handler": self.cmd_on_click_time_response},
            4: {"action": "set_entry_type_datetime", "handler": self.cmd_on_click_dateteime_response},
            5: {"action": "set_entry_type_number", "handler": self.cmd_on_click_number_response},
            6: {"action": "set_entry_type_file", "handler": self.cmd_on_click_file_response},
            7: {"action": "set_entry_type_select", "handler": self.cmd_on_click_list_response},
            8: {"action": "set_entry_type_hidden", "handler": self.cmd_on_click_hidden_response},
            9: "_insert_stretch",
        }
        if self.compatibility is not None:
            if self.compatibility.lower().replace(" ", "_") == "google_forms":
                buttons[8] = "_skip"
            elif self.compatibility.lower().replace(" ", "_") == "microsoft_forms":
                buttons[8] = "_skip"
            elif self.compatibility.lower().replace(" ", "_") == "apple_forms":
                buttons[8] = "_skip"
            elif self.compatibility.lower().replace(" ", "_") == "you_form":
                buttons[8] = "_skip"
        self.response_type_toolbar = NchantdButtonBar(self, cfg).initWidget(buttons)
        self.left_side_layout.addWidget(self.response_type_toolbar)
        response_layout = pyqt.QHBoxLayout()
        cfg = {
            "label": "Enter Response Text: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "entrybox": {"size": ["auto", 60]},
        }
        self.response = NchantdLabeledEntry(self, cfg).initWidget()
        response_layout.addWidget(self.response)
        options = [
            "Proceed to Next Inquiry",
            "Submit Response",
            "Submit Form",
            "Cancel Form",
            "Cancel Response",
            "Proceed to Speicif Inquiry",
        ]
        cfg = {
            "label": "Select Response Trigger: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "combobox": {"options": options},
        }
        self.response_trigger = NchantdDropDown(self, cfg).initWidget()
        response_layout.addWidget(self.response_trigger)
        self.left_side_layout.addLayout(response_layout)
        cfg = {"multi_options": ["Answer Required", "Always Asked"], "layout": "horizontal", "size": ["auto", "auto"]}
        self.options = NchantdCheckboxGroup(self, cfg).initWidget()
        # TODO change always asked to a asked rate spinbox really should be part of the survey and not the form itself
        self.left_side_layout.addWidget(self.options)
        cfg = {}
        self.accept_button_group = NchantdAcceptButtons(self, cfg).initWidget()
        self.right_side_layout.addWidget(self.accept_button_group)

        #        self.right_side_layout.addStretch(1)
        self.right_side_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignRight | pyqt.Qt.AlignmentFlag.AlignBottom)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_on_change_form_description(self, event=None, *args, **kwargs):
        """"""

    def cmd_on_change_query_text(self, event=None, *args, **kwargs):
        """"""

    def cmd_on_click_text_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_date_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_time_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_dateteime_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_hidden_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_table_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_number_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_file_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_list_response(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_select_trigger_response(self, event=None, *args, **kwargs):
        """"""

    def cmd_on_toggle_answer_required(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_toggle_always_asked(self, event=None, *args, **kwargs):
        """"""
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
