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
from os.path import dirname, join
import datetime as dt
from sys import argv

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
# try:
#     import crow
#
#     # crow.crowLoad removed
# except:
#     pass
from condor import condor
from nchantrs.nchantrs import nchantment
from nchantrs.widgets.applications.applications import NchantdCloak, NchantdMainWindow
from nchantdoffice.models import NchantdOfficeCloakModel
from nchantdoffice.views import NchantdOfficeCloakView
from nchantdoffice.wizards.wizards import NchantdOfficeApplicationStartupWizard
from nchantdoffice.updates.db import NchantdOfficeDBUpdate
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
logma.info(f"here: {here}")
pxcfg = join(here, "_data_", "nchantdoffice.yaml")


class NchantdOfficeCloak(NchantdCloak):
    """"""

    def __init__(self, name, instance=None, parent=None, cfg=None, args=None):
        """ """
        super().__init__(name, instance, parent, None, args)
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeCloak").override(cfg))
        self.config.override({"app": "nchantdoffice"})
        self.parent = parent
        logma.info(f"NchantdOfficeCloak: {self.config.dikt.get("config", None)}")
        if self.parent is None:
            self.parent = self
        self.main = NchantdOfficeMainWindow(self)
        self.model = NchantdOfficeCloakModel(name, self.instance, self)
        self.view = NchantdOfficeCloakView(self)
        self.dbupdate = NchantdOfficeDBUpdate(self)
        self.application_NCD = "40c94efb-d374-437f-a48b-3c6b843fd110"
        self.install = True
        self.primary_focus = "office_platform"
        self.is_installable = True
        self.is_install_optional = False
        self.has_comms = True
        self.has_library = True
        self.library_optional = True
        self.toolbox = None

    def run_on_launch(self):
        """"""
        super().run_on_launch()
        self.model.set_today()


class NchantdOfficeMainWindow(NchantdMainWindow):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeMainWindow"))
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

    def hideEvent(self, event):
        """"""
        # self.parent.sigils.hide()
        super().hideEvent(event)


# if __name__ == "__main__":
#     start = dt.datetime.now()
#     logma.info("Start")
#     app = NchantdOfficeCloak
#     wizard = NchantdOfficeApplicationStartupWizard
#     nchantment("NchantdOffice", argv, app, None, wizard)
#     end = dt.datetime.now()
#     logma.info(f"End Duration {end - start}")

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
