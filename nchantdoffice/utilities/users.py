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
from nchantrs.utilities.users import NchantdUser
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "users.yaml")


class NchantdOfficeUser(NchantdUser):
    """"""

    def __init__(self, parent=None, cfg=None):
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeUser").override(cfg))
        self.available_services = None
        self.services = None
        self.bridges = {}

    def create_bridge(self, profile="default"):
        """"""
        # self.bridges[profile.lower()] = Bridge(profile.lower())

    def add_api_service(self, service):
        """
        need to lookup the service and determine how it is connected
        :param service:
        :return:
        """
        if self.services is None:
            self.get_available_services()
        service_params = self.app.model.get_service(service)
        if self.service_params.empty():
            raise Exception()

        self.app.model.store_api_service(
            service,
            self.username,
        )

    def get_available_services(self):
        """"""
        df = self.app.model.get_available_services()
        self.available_services = df

    def connect_to_service(self, service):
        """"""
        self.bridge.connect_bridge(service)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
