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
from nchantrs.widgets import controls, tabs
from nchantrs.widgets.media import editors
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdAddResourceTab(tabs.NchantdTab):
    """
    NTDAddResourceTab

    A class for creating and initializing a tab layout with various editors and buttons for adding a new resource.

    Inherits from tabs.NchantdTab.

    Attributes:
    - parent: The parent widget.
    - config: The configuration options.
    - singlepane: Determines if the tab should be displayed in a single pane.

    Methods:
    - __init__(self, parent=None, cfg={}, singlepane=False): Initializes an instance of the NTDAddResourceTab class.
    - initView(self): Creates and initializes a pane layout with various editors and buttons.

    """

    # TODO: Move to Resources Node
    def __init__(self, parent=None, cfg={}, singlepane=False):
        """
        Initializes an instance of the NTDAddResourceTab class.

        :param parent: The parent widget. Defaults to None.
        :type parent: Union[None, QWidget]

        :param cfg: The configuration options. Defaults to an empty dict.
        :type cfg: Dict[str, Any]

        :param singlepane: Determines if the tab should be displayed in a single pane. Defaults to False.
        :type singlepane: bool

        """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg)
        self.config.select("NTDTaskSplitterTab").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdAddResourceTab, self).__init__(parent, self.config, singlepane)

    def initView(self):
        """
        Creates and initializes a pane layout with various editors and buttons.

        :return: The initialized pane layout.
        """
        layout = pyqt.QVBoxLayout()
        top_layout = pyqt.QHBoxLayout()
        gb = pyqt.QGroupBox()
        top_layout_left = pyqt.QHBoxLayout()

        top_layout_left.addWidget(controls.NchantdSaveButton(self).initWidget(None))
        cfg = {"label": "New Resource Name: "}
        top_layout_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())

        cfg = {"label": "New Resource Code: "}
        top_layout_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())

        top_layout_left.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)

        top_layout.addLayout(top_layout_left)
        top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        cfg = {"label": "New Resource Description: "}
        top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "medium"))

        gb.setLayout(top_layout)
        layout.addWidget(gb)
        layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)

        bottom_layout = pyqt.QHBoxLayout()
        gb = pyqt.QGroupBox()
        cfg = {"label": "List of Concerns: "}
        bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "large"))

        cfg = {"label": "Assign Resources: "}
        bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "large"))
        gb.setLayout(bottom_layout)
        layout.addWidget(gb)
        self.setLayout(layout)

        return self


class NchantdResourcesEventTab(tabs.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}, singlepane=None):
        """
        Initializes the NTDAdministrateResourcesTab object.

        :param parent: The parent object. Defaults to None.
        :type parent: object
        :param cfg: The configuration object. Defaults to an empty dictionary.
        :type cfg: dict
        :param singlepane: The singlepane object. Defaults to None.
        :type singlepane: object
        """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg)
        self.config.select("NTDConcernTasksTab").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdAdministrateResourcesTab, self).__init__(parent, self.config, singlepane)

    def initModel(self):
        """"""
        return self

    def initView(self):
        """
        Builds the pane with various entry editors and layouts.

        :return: The built pane.
        """
        layout = pyqt.QVBoxLayout()
        gb = pyqt.QGroupBox()
        top_layout = pyqt.QHBoxLayout()
        cfg = {"label": "Operations List"}
        top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "medium"))
        cfg = {"label": "Projects List"}
        top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "medium"))
        gb.setLayout(top_layout)
        layout.addWidget(gb)
        cfg = {"label": "Near Term Tasks List"}
        layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "large"))
        self.setLayout(layout)
        return self

    def initWidget(self):
        """"""
        return self


class NchantdResourceManagementTab(tabs.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}, singlepane=None):
        """
        Initialize the NTDAdministrateEventsTab object.

        :param parent: The parent object. Default is None.
        :type parent: object

        :param cfg: The configuration values. Default is an empty dictionary.
        :type cfg: dict

        :param singlepane: A singlepane object. Default is None.
        :type singlepane: object
        """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg)
        self.config.select("NTDConcernTasksTab").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdResourceManagementTab, self).__init__(parent, self.config, singlepane)

    def initModel(self):
        """"""
        return self

    def initView(self):
        """
        Builds the pane for the GUI.

        :return: The built pane.
        """
        layout = pyqt.QVBoxLayout()
        gb = pyqt.QGroupBox()
        top_layout = pyqt.QHBoxLayout()
        cfg = {"label": "Operations List"}
        top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "medium"))
        cfg = {"label": "Projects List"}
        top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "medium"))
        gb.setLayout(top_layout)
        layout.addWidget(gb)
        cfg = {"label": "Near Term Tasks List"}
        layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "large"))
        self.setLayout(layout)
        return self

    def initWidget(self):
        """"""
        return self


class NchantdResourcesManagementTab(tabs.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}, singlepane=None):
        """
        Initialize the NTDAdministrateEventsTab object.

        :param parent: The parent object. Default is None.
        :type parent: object

        :param cfg: The configuration values. Default is an empty dictionary.
        :type cfg: dict

        :param singlepane: A singlepane object. Default is None.
        :type singlepane: object
        """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg)
        self.config.select("NTDConcernTasksTab").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdResourcesManagementTab, self).__init__(parent, self.config, singlepane)

    def initModel(self):
        """"""
        return self

    def initView(self):
        """
        Builds the pane for the GUI.

        :return: The built pane.
        """
        layout = pyqt.QVBoxLayout()
        gb = pyqt.QGroupBox()
        top_layout = pyqt.QHBoxLayout()
        cfg = {"label": "Operations List"}
        top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "medium"))
        cfg = {"label": "Projects List"}
        top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "medium"))
        gb.setLayout(top_layout)
        layout.addWidget(gb)
        cfg = {"label": "Near Term Tasks List"}
        layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, "large"))
        self.setLayout(layout)
        return self

    def initWidget(self):
        """"""
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
