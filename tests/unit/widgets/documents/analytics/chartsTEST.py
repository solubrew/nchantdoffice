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
    -(WT)-: -32  # 2025-11-06 09:46:34
"""

# 2025-11-06 09:46:34
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
import json  # 2025-11-06 09:46:34
import tempfile  # 2025-11-06 09:46:34
import os  # 2025-11-06 09:46:34

# ======================================3rd Party Library Modules=====================================================||
from nchantdoffice.widgets.documents.analytics.charts import NchantdSourcesListPane  # 2025-11-06 09:46:34
from nchantdoffice.widgets.documents.analytics.charts import NchantdWhereUsedListPane  # 2025-11-06 09:46:34
from nchantdoffice.widgets.documents.analytics.charts import NchantdOfficeChart  # 2025-11-06 09:46:34

# =========================================Local Library Modules======================================================||
# 2025-11-06 09:46:34

# ====================================================================================================================||
HERE = join(dirname(__file__))  # 2025-11-06 09:46:34
LOGMA = Logma(__name__)  # 2025-11-06 09:46:34
PXCFG = join(HERE, "_data_", "chartsTEST.yaml")  # 2025-11-06 09:46:34
CFG = kahndor.Instruct(PXCFG).load().dikt  # 2025-11-06 09:46:35
FIXTURES = kahndor.Instruct(join(HERE, "..", "fixtures", "fixtures.yaml")).load().dikt  # 2025-11-06 09:46:35
# 2025-11-06 09:46:34
# ====================================================================================================================||


class Test_NchantdSourcesListPane:  # 2025-11-06 09:46:35
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:46:35
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:46:35
        """"""

        return

    def reset(self):  # 2025-11-06 09:46:35
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:46:35
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass


class Test_NchantdWhereUsedListPane:  # 2025-11-06 09:46:35
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:46:35
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:46:35
        """"""

        return

    def reset(self):  # 2025-11-06 09:46:35
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:46:35
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass


class Test_NchantdOfficeChart:  # 2025-11-06 09:46:35
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:46:35
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:46:35
        """"""

        return

    def reset(self):  # 2025-11-06 09:46:35
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:46:35
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_cmd_toggle_config_pane(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_cmd_toggle_data_pane(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_cmd_toggle_full_screen_pane(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_get_border_styles(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_get_data_sources(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_get_data_views(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_get_palettes(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_get_themes(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_get_types(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_init_drawer_chart_config(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_init_drawer_connections(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_init_drawer_data_sources(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_init_drawer_quickstart(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_init_toolbox(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_load_types(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_set_pane(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test_set_type(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:46:35
        """"""
        if test_000:
            pass


class Test_Functions:  # 2025-11-06 09:46:35
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:46:35
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:46:35
        """"""

        return

    def reset(self):  # 2025-11-06 09:46:35
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:46:35
        """Executes a series of test functions in a sequential logic."""

        return self


# ====================================================================================================================||
"""
  # 2025-11-06 09:46:34
"""
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
