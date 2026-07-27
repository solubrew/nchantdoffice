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
        logma.info(f"[users] NchantdOfficeUser.__init__ parent={type(parent).__name__} cfg_keys={list((cfg or {}).keys())}")

    def create_bridge(self, profile="default"):
        """"""
        logma.info(f"[users] create_bridge: profile={profile!r} (currently a no-op stub)")
        # self.bridges[profile.lower()] = Bridge(profile.lower())

    def add_api_service(self, service):
        """
        need to lookup the service and determine how it is connected
        :param service:
        :return:
        """
        logma.info(f"[users] add_api_service: service={service!r}")
        if self.services is None:
            self.get_available_services()
        try:
            service_params = self.app.model.get_service(service)
            logma.debug(f"[users] add_api_service: service_params shape={getattr(service_params, 'shape', None)}")
            if self.service_params.empty():
                logma.error(f"[users] add_api_service: service_params empty for service={service!r}")
                raise Exception(f"service_params empty for service={service!r}")
            self.app.model.store_api_service(
                service,
                self.username,
            )
            logma.info(f"[users] add_api_service: stored service={service!r} for user={self.username!r}")
        except Exception as e:
            logma.error(f"[users] add_api_service failed: service={service!r} err={e}", exc_info=True)
            raise

    def get_available_services(self):
        """"""
        logma.info("[users] get_available_services: querying model")
        try:
            df = self.app.model.get_available_services()
            self.available_services = df
            logma.info(f"[users] get_available_services: {len(df) if df is not None else 0} services returned")
        except Exception as e:
            logma.error(f"[users] get_available_services failed: {e}", exc_info=True)
            raise

    def connect_to_service(self, service):
        """"""
        logma.info(f"[users] connect_to_service: service={service!r}")
        try:
            if not hasattr(self, "bridge") or self.bridge is None:
                logma.error(f"[users] connect_to_service: no bridge initialised - call create_bridge first")
                return self
            self.bridge.connect_bridge(service)
            logma.info(f"[users] connect_to_service: connected to service={service!r}")
        except Exception as e:
            logma.error(f"[users] connect_to_service failed: service={service!r} err={e}", exc_info=True)
            raise


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
