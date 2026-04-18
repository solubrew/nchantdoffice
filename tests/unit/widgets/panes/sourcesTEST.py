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
    -(WT)-: -32  # 2025-11-06 09:47:48
"""

# 2025-11-06 09:47:48
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
import json  # 2025-11-06 09:47:48
import tempfile  # 2025-11-06 09:47:48
import os  # 2025-11-06 09:47:48

# ======================================3rd Party Library Modules=====================================================||
from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdSourcesListPane  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdWhereUsedListPane  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdOfficeEDA  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdSourcePane  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdDataSetPane  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdViewPane  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdViewEditPane  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdDataSetConfigPane  # 2025-11-06 09:47:48
from nchantdoffice.widgets.panes.sources import NchantdSourceDefaultPane  # 2025-11-06 09:47:48

# =========================================Local Library Modules======================================================||
# 2025-11-06 09:47:48

# ====================================================================================================================||
HERE = join(dirname(__file__))  # 2025-11-06 09:47:48
LOGMA = Logma(__name__)  # 2025-11-06 09:47:48
PXCFG = join(HERE, "_data_", "sourcesTEST.yaml")  # 2025-11-06 09:47:48
CFG = kahndor.Instruct(PXCFG).load().dikt  # 2025-11-06 09:47:48
FIXTURES = kahndor.Instruct(join(HERE, "..", "fixtures", "fixtures.yaml")).load().dikt  # 2025-11-06 09:47:48
# 2025-11-06 09:47:48
# ====================================================================================================================||


class Test_NchantdSourceEditPane:  # 2025-11-06 09:47:48
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:48
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:48
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:48
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:48
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass


class Test_NchantdSourcesListPane:  # 2025-11-06 09:47:48
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:48
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:48
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:48
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:48
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass


class Test_NchantdWhereUsedListPane:  # 2025-11-06 09:47:48
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:48
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:48
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:48
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:48
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass


class Test_NchantdOfficeEDA:  # 2025-11-06 09:47:48
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:48
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:48
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:48
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:48
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_set_slim_tab(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass


class Test_NchantdSourcePane:  # 2025-11-06 09:47:48
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:48
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:48
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:48
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:48
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_cmd_launch_data_source(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_cmd_on_change_data_source_availability(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_cmd_show_api_key(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_get_data_source_availability(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:48
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_store_active_source(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_update_pane(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass


class Test_NchantdDataSetPane:  # 2025-11-06 09:47:49
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:49
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:49
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:49
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:49
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_get_data_view_fields(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass


class Test_NchantdViewPane:  # 2025-11-06 09:47:49
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:49
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:49
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:49
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:49
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass


class Test_NchantdViewEditPane:  # 2025-11-06 09:47:49
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:49
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:49
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:49
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:49
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_get_fields(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass


class Test_NchantdDataSetConfigPane:  # 2025-11-06 09:47:49
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:49
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:49
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:49
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:49
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_add_axis(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_add_data_series(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_add_legend(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_add_data_series(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_add_legend(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_connect_source(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_launch_color_sigil(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_on_change_type(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_on_description_change(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_on_name_change(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_on_palette_change(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_on_theme_change(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_border_color(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_border_style(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_border_thickness(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_color(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_color_area(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_color(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_name(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_shape(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_style(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_thickness(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_description(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_cmd_set_name(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_configure_background(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_configure_legend(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_configure_plotarea(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_area_color(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_area_colors(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_background_color(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_border_color(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_border_colors(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_border_style(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_border_styles(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_border_thickness(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_colors(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_legend(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_legends(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_palette(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_palettes(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_theme(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_themes(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_type(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_get_types(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_load_colors(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_load_types(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_set_type(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test_update_chart(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:49
        """"""
        if test_000:
            pass


class Test_NchantdSourceDefaultPane:  # 2025-11-06 09:47:50
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:50
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:50
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:50
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:50
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_cmd_on_data_table_change(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test_cmd_on_source_change(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test_get_source(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test_get_source_table(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test_get_source_tables(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test_get_sources(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:50
        """"""
        if test_000:
            pass


class Test_Functions:  # 2025-11-06 09:47:50
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:50
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:50
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:50
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:50
        """Executes a series of test functions in a sequential logic."""

        return self


# ====================================================================================================================||
"""
  # 2025-11-06 09:47:48
"""
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
