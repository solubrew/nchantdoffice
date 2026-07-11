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
from nchantrs.libraries import pyqt
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown, NchantdComboBox
from kahndor.logma import Logma
from nchantrs.widgets.groups import NchantdVScrollGroupBox
from nchantrs.widgets.config.settings import NchantdSettingsWidget

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "journal.yaml")


class NchantdOfficeJournalSettings(NchantdSettingsWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(
            kahndor.Instruct(pxcfg).select("NchantdOfficeJournalSettings").override(parent.config).override(cfg)
        )

    def initModel(self):
        """"""
        super().initModel()
        self.journal_edit_enable = None  # self.app.model.store.get_settings_journal_edit_enable()
        self.journal_reedit_enable = None  # self.app.model.store.get_settings_journal_reedit_enable()
        self.journal_date_insert_enable = None  # self.app.model.store.get_settings_journal_date_insert_enable()
        self.journal_editor_enable = None  # self.app.model.store.get_settings_journal_editor_enable()
        self.journal_history_enable = None  # self.app.model.store.get_settings_journal_history_enable()
        self.journal_history_expirary_length = (
            None  # self.app.model.store.get_settings_journal_history_expirary_length()
        )
        self.journal_share_instance_enable = None  # self.app.model.store.get_settings_journal_share_instance_enable()
        self.journal_tree_enable = None  # self.app.model.store.get_settings_journal_tree_enable()

        return self

    def initView(self, cfg=None):
        """"""
        layout = pyqt.QHBoxLayout()
        text = "Journal Settings impact only the Journal data written within this application instance."
        layout.addWidget(NchantdLabel(self, {"text": text, "size": [600, 30], "wrap_limit": 400}).initWidget())
        # cfg = {"layouts": layout}
        super().initView(cfg)
        self.layout.addLayout(layout)
        cfg = {"size": ["auto", "auto"], "layout": "vertical", "justify": "left"}
        self.settings_group = NchantdVScrollGroupBox(self, cfg)
        self.layout.addLayout(self.settings_group.layout)
        self.settings_group.layout.setContentsMargins(0, 0, 0, 0)
        self.settings_group.setTitle("Journal Settings")

        today_settings_group = pyqt.QGroupBox(self)
        today_settings_group.setTitle("Today Settings")
        self.today_settings_layout = pyqt.QGridLayout()
        self.today_settings_layout.setAlignment(pyqt.Qt.AlignTop | pyqt.Qt.AlignLeft)
        today_settings_group.setLayout(self.today_settings_layout)
        cfg = {"text": "Enable Today Tab", "layout": "horizontal", "size": ["auto", "auto"]}
        self.today_headlines_enable = NchantdCheckbox(self, cfg).initWidget()
        self.today_settings_layout.addWidget(self.today_headlines_enable, 0, 0)
        cfg = {"text": "Enable Daily Headlines", "layout": "horizontal", "size": ["auto", "auto"]}
        self.today_headlines_enable = NchantdCheckbox(self, cfg).initWidget()
        self.today_settings_layout.addWidget(self.today_headlines_enable, 1, 0)
        cfg = {"text": "Enable Weekly Weather", "layout": "horizontal", "size": ["auto", "auto"]}
        self.today_headlines_enable = NchantdCheckbox(self, cfg).initWidget()
        self.today_settings_layout.addWidget(self.today_headlines_enable, 2, 0)
        today_settings_group.setMinimumHeight(self.today_settings_layout.sizeHint().height() * 1.2)
        self.settings_group.addWidget(today_settings_group)

        # history_settings_group = pyqt.QGroupBox(self)
        # history_settings_group.setTitle("Journal History")
        # history_settings_layout = pyqt.QGridLayout()
        # history_settings_layout.setSpacing(0)
        # history_settings_layout.setAlignment(pyqt.Qt.AlignTop | pyqt.Qt.AlignLeft)
        # history_settings_group.setLayout(history_settings_layout)
        # cfg = {"text": "Store Journal Entries Between Sessions", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_history_enable = NchantdCheckbox(self, cfg).initWidget()
        # history_settings_layout.addWidget(self.journal_history_enable, 0, 0)
        #
        # journal_history_enabled_group = pyqt.QGroupBox(self)
        # journal_history_enabled_group.setTitle("Journal History Enabled")
        # journal_history_enabled_layout = pyqt.QGridLayout()
        # journal_history_enabled_layout.setSpacing(0)
        # journal_history_enabled_layout.setAlignment(pyqt.Qt.AlignTop | pyqt.Qt.AlignLeft)
        # journal_history_enabled_layout.columnStretch(0)
        # journal_history_enabled_group.setLayout(journal_history_enabled_layout)
        #
        # cfg = {"text": "Expire History After X Days: ", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_history_expirary = NchantdCheckbox(self, cfg).initWidget()
        # journal_history_enabled_layout.addWidget(self.journal_history_expirary, 0, 0)
        # options = [str(x) for x in [3, 15, 30, 90, 180, 365, 730, 1825]]
        # cfg = {
        #     "label": "Select rolling days to keep Journal: ",
        #     "layout": "horizontal",
        #     "combobox": {"options": options, "size": [150, 30]},
        #     "value": self.journal_history_expirary_length,
        # }
        # self.journal_history_expirary_length = NchantdDropDown(self, cfg).initWidget()
        # journal_history_enabled_layout.addWidget(self.journal_history_expirary_length, 1, 0)
        # journal_history_enabled_group.setMinimumHeight(journal_history_enabled_layout.sizeHint().height() * 1.2)
        # cfg = {
        #     "text": "Delete Journal Entries When the Associated Tab is Deleted",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        # }
        # self.journal_share_instance_enable = NchantdCheckbox(self, cfg).initWidget()
        # history_settings_layout.addWidget(self.journal_share_instance_enable, 2, 0)
        # cfg = {"text": "Share Journal Between Instances", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_share_instance_enable = NchantdCheckbox(self, cfg).initWidget()
        # history_settings_layout.addWidget(self.journal_share_instance_enable, 3, 0)
        # history_settings_layout.addWidget(journal_history_enabled_group, 1, 0)
        # history_settings_layout.columnStretch(0)
        # history_settings_group.setMinimumHeight(self.today_settings_layout.sizeHint().height() * 1.2)
        # self.settings_group.addWidget(history_settings_group)
        #
        # editor_settings_group = pyqt.QGroupBox(self)
        # editor_settings_group.setTitle("Journal Editor")
        # editor_settings_layout = pyqt.QGridLayout()
        # editor_settings_layout.setAlignment(pyqt.Qt.AlignTop | pyqt.Qt.AlignLeft)
        # editor_settings_group.setLayout(editor_settings_layout)
        # cfg = {"text": "Show Journal Editor in Side Bar", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_editor_enable = NchantdCheckbox(self, cfg).initWidget()
        # editor_settings_layout.addWidget(self.journal_editor_enable, 0, 0)
        # cfg = {"text": "Insert Date Per Focus", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_date_insert_enable = NchantdCheckbox(self, cfg).initWidget()
        # editor_settings_layout.addWidget(self.journal_date_insert_enable, 1, 0)
        # self.settings_group.addWidget(editor_settings_group)
        # cfg = {"text": "Allow Editing on Entry", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_edit_enable = NchantdCheckbox(self, cfg).initWidget()
        # editor_settings_layout.addWidget(self.journal_edit_enable, 2, 0)
        # cfg = {"text": "Allow Editing on Re-Entry", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_reedit_enable = NchantdCheckbox(self, cfg).initWidget()
        # editor_settings_layout.addWidget(self.journal_reedit_enable, 3, 0)
        # editor_settings_group.setMinimumHeight(editor_settings_layout.sizeHint().height() * 1.2)
        # self.settings_group.addWidget(editor_settings_group)

        # tree_settings_group = pyqt.QGroupBox(self)
        # tree_settings_group.setTitle("Journal Tree")
        # tree_settings_layout = pyqt.QGridLayout()
        # tree_settings_layout.setSpacing(0)
        # tree_settings_layout.setAlignment(pyqt.Qt.AlignTop | pyqt.Qt.AlignLeft)
        # tree_settings_group.setLayout(tree_settings_layout)
        # self.settings_group.addWidget(tree_settings_group)
        # cfg = {"text": "Show Journal Date Tree", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_tree_enable = NchantdCheckbox(self, cfg).initWidget()
        # tree_settings_layout.addWidget(self.journal_tree_enable, 0, 0)
        # cfg = {"text": "Create each Year as Node", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_tree_year_insert = NchantdCheckbox(self, cfg).initWidget()
        # tree_settings_layout.addWidget(self.journal_tree_year_insert, 1, 0)
        # cfg = {"text": "Create each Quarter Year as Node", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_tree_quarter_year_insert = NchantdCheckbox(self, cfg).initWidget()
        # tree_settings_layout.addWidget(self.journal_tree_quarter_year_insert, 2, 0)
        # cfg = {"text": "Create each Month as Node", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_tree_month_insert = NchantdCheckbox(self, cfg).initWidget()
        # tree_settings_layout.addWidget(self.journal_tree_month_insert, 3, 0)
        # cfg = {"text": "Create each Day as Node", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_tree_day_insert = NchantdCheckbox(self, cfg).initWidget()
        # tree_settings_layout.addWidget(self.journal_tree_day_insert, 4, 0)
        # cfg = {"text": "Create each Hour as Node", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_hour_day_insert = NchantdCheckbox(self, cfg).initWidget()
        # tree_settings_layout.addWidget(self.journal_hour_day_insert, 5, 0)
        # cfg = {"text": "Create each Quarter Hour as Node", "layout": "horizontal", "size": ["auto", "auto"]}
        # self.journal_quarter_hour_day_insert = NchantdCheckbox(self, cfg).initWidget()
        # tree_settings_layout.addWidget(self.journal_quarter_hour_day_insert, 6, 0)
        # tree_settings_group.setMinimumHeight(tree_settings_layout.sizeHint().height())
        # self.settings_group.addWidget(tree_settings_group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_settings(self):
        """"""
        return super().get_settings("journal")

    def save(self):
        """"""
        # if self.enable_today_tab.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.enable_daily_headlines.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.enable_weekly_weather.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.store_journal_entries.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.journal_expire_history.changed:
        #     value = self.history_expirary_length.value
        # if self.journal_share_instance.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.show_journal_editor.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.insert_date_on_focus.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.allow_journal_edit.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.allow_journal_reedit.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.show_journal_tree.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.create_year_tree.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.create_quarter_year_tree.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.create_month_tree.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.create_day_tree.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.create_hour_tree.changed:
        #     self.app.model.store.store_settings_journal()
        # if self.create_quarter_hour_tree.changed:
        #     self.app.model.store.store_settings_journal()

        super().save()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
