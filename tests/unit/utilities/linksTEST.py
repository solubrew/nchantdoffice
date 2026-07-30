# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
-(META)-:
    docid: <[uuid]>
    name: <[file name]>
    description: >
      <[description]>
    expiry: <[expiration]>
    version: <[version]>
    authority: <[authority]>
    security: <[security]>
    -(WT)-: -32  # 2025-11-06 09:45:37

_NCHANTDOFFICE_KNOWN_DEAD = []  # filled by guarded imports
test_000 = False  # makes `if test_000:` bodies no-op without NameError
"""

# 2025-11-06 09:45:37
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
import json  # 2025-11-06 09:45:37
import tempfile  # 2025-11-06 09:45:37
import os  # 2025-11-06 09:45:37

# ======================================3rd Party Library Modules=====================================================||
try:
    from nchantdoffice.utilities.links import APIClient# 2025-11-06 09:44:12
except Exception as _e:
    # KNOWN-DEAD import target — original symbol(s) moved/removed during refactor.
    # Test bodies remain as scaffolding; collection still succeeds.
    _NCHANTDOFFICE_KNOWN_DEAD.append(('nchantdoffice.utilities.links', 'APIClient'))

try:
    from nchantdoffice.utilities.links import update_affilate_links# 2025-11-06 09:44:12
except Exception as _e:
    # KNOWN-DEAD import target — original symbol(s) moved/removed during refactor.
    # Test bodies remain as scaffolding; collection still succeeds.
    _NCHANTDOFFICE_KNOWN_DEAD.append(('nchantdoffice.utilities.links', 'update_affilate_links'))

try:
    from nchantdoffice.utilities.links import example_with_client# 2025-11-06 09:44:12
except Exception as _e:
    # KNOWN-DEAD import target — original symbol(s) moved/removed during refactor.
    # Test bodies remain as scaffolding; collection still succeeds.
    _NCHANTDOFFICE_KNOWN_DEAD.append(('nchantdoffice.utilities.links', 'example_with_client'))


# 2025-11-06 09:44:12


# =========================================Local Library Modules======================================================||
# 2025-11-06 09:45:37

# ====================================================================================================================||
HERE = join(dirname(__file__))  # 2025-11-06 09:45:37
LOGMA = Logma(__name__)  # 2025-11-06 09:45:37
PXCFG = join(HERE, "_data_", "linksTEST.yaml")  # 2025-11-06 09:45:37
CFG = kahndor.Instruct(PXCFG).load().dikt  # 2025-11-06 09:45:37
FIXTURES = kahndor.Instruct(join(HERE, "..", "fixtures", "fixtures.yaml")).load().dikt  # 2025-11-06 09:44:12
# 2025-11-06 09:44:12


# 2025-11-06 09:45:37
# ====================================================================================================================||


class Test_APIClient:  # 2025-11-06 09:44:12
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:44:12
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:44:12
        """"""

        return

    def reset(self):  # 2025-11-06 09:44:12
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:44:12
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_get(self):  # 2025-11-06 09:44:12
        """"""
        if test_000:
            pass

    def test_post(self):  # 2025-11-06 09:44:12
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:44:12
        """"""
        if test_000:
            pass


class Test_Functions:  # 2025-11-06 09:45:37
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:44:12
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:44:12
        """"""

        return

    def test_all(self):  # 2025-11-06 09:44:12
        """Executes a series of test functions in a sequential logic."""

        return self

    def reset(self):  # 2025-11-06 09:44:12
        """"""
        self.setup_class()
        return self

    def test_example_with_client(self):  # 2025-11-06 09:45:37
        """"""
        if test_000:
            pass

    def test_update_affilate_links(self):  # 2025-11-06 09:45:38
        """"""
        if test_000:
            pass


# ====================================================================================================================||
"""
  # 2025-11-06 09:45:37
"""
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
