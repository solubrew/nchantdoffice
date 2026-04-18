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
    -(WT)-: -32  # 2025-11-06 09:47:34
"""

# 2025-11-06 09:47:34
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
import json  # 2025-11-06 09:47:34
import tempfile  # 2025-11-06 09:47:34
import os  # 2025-11-06 09:47:34

# ======================================3rd Party Library Modules=====================================================||
from nchantdoffice.widgets.panes.charts import NchantdChartConfigPane  # 2025-11-06 09:47:34
from nchantdoffice.widgets.panes.charts import NchantdChartAxisPane  # 2025-11-06 09:47:34
from nchantdoffice.widgets.panes.charts import NchantdChartDataSeriesPane  # 2025-11-06 09:47:34
from nchantdoffice.widgets.panes.charts import NchantdChartLegendPane  # 2025-11-06 09:47:34
from nchantdoffice.widgets.panes.charts import NchantdChartTrendlinePane  # 2025-11-06 09:47:34

# =========================================Local Library Modules======================================================||
# 2025-11-06 09:47:34

# ====================================================================================================================||
HERE = join(dirname(__file__))  # 2025-11-06 09:47:34
LOGMA = Logma(__name__)  # 2025-11-06 09:47:34
PXCFG = join(HERE, "_data_", "chartsTEST.yaml")  # 2025-11-06 09:47:34
CFG = kahndor.Instruct(PXCFG).load().dikt  # 2025-11-06 09:47:34
FIXTURES = kahndor.Instruct(join(HERE, "..", "fixtures", "fixtures.yaml")).load().dikt  # 2025-11-06 09:47:34
# 2025-11-06 09:47:34
# ====================================================================================================================||


class Test_NchantdChartConfigPane:  # 2025-11-06 09:47:34
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:34
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:34
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:34
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:34
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_add_axis(self):  # 2025-11-06 09:47:34
        """"""
        if test_000:
            pass

    def test_add_data_series(self):  # 2025-11-06 09:47:34
        """"""
        if test_000:
            pass

    def test_add_legend(self):  # 2025-11-06 09:47:34
        """"""
        if test_000:
            pass

    def test_cmd_add_data_series(self):  # 2025-11-06 09:47:34
        """"""
        if test_000:
            pass

    def test_cmd_add_legend(self):  # 2025-11-06 09:47:34
        """"""
        if test_000:
            pass

    def test_cmd_connect_data_source(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_launch_color_sigil(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_on_change_type(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_on_description_change(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_on_name_change(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_on_palette_change(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_on_theme_change(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_border_color(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_border_style(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_border_thickness(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_color(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_color_area(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_color(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_name(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_shape(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_style(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_data_series_thickness(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_description(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_cmd_set_name(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_configure_background(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_configure_legend(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_configure_plotarea(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_area_color(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_area_colors(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_background_color(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_border_color(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_border_colors(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_border_style(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_border_styles(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_border_thickness(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_colors(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_legend(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_legends(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_palette(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_palettes(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_theme(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_themes(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_type(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_types(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_load_colors(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_load_types(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_set_type(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_update_chart(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass


class Test_NchantdChartAxisPane:  # 2025-11-06 09:47:35
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:35
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:35
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:35
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:35
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_cmd_add_axis(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_axsi(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_updateGeometry(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass


class Test_NchantdChartDataSeriesPane:  # 2025-11-06 09:47:35
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:35
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:35
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:35
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:35
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_get_color(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_colors(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_line_marker(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_line_markers(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_series(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_series_data(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_shape(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_shapes(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_style(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_styles(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_thickness(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_thickness_range(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass


class Test_NchantdChartLegendPane:  # 2025-11-06 09:47:35
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:35
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:35
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:35
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:35
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_get_color(self):  # 2025-11-06 09:47:35
        """"""
        if test_000:
            pass

    def test_get_colors(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series_all(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series_color(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series_colors(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series_shape(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series_shapes(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series_style(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series_styles(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_data_series_thickness(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_line_marker(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_line_markers(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_thickness(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_thickness_range(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass


class Test_NchantdChartTrendlinePane:  # 2025-11-06 09:47:36
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:36
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:36
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:36
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:36
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_get_color(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_colors(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_line_marker(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_line_markers(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_thickness(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_thickness_range(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_trendline_form(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_trendline_forms(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_trendline_formula(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_get_trendline_formulas(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:47:36
        """"""
        if test_000:
            pass


class Test_Functions:  # 2025-11-06 09:47:36
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:47:36
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:47:36
        """"""

        return

    def reset(self):  # 2025-11-06 09:47:36
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:47:36
        """Executes a series of test functions in a sequential logic."""

        return self


# ====================================================================================================================||
"""
  # 2025-11-06 09:47:34
"""
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
