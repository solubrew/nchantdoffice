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
    -(WT)-: -32  # 2025-11-06 09:48:01
"""

# 2025-11-06 09:48:01
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
import json  # 2025-11-06 09:48:01
import tempfile  # 2025-11-06 09:48:01
import os  # 2025-11-06 09:48:01

# ======================================3rd Party Library Modules=====================================================||
from nchantdoffice.widgets.documents.atnrg.prompts import NchantdContextListPane  # 2025-11-06 09:48:01
from nchantdoffice.widgets.documents.atnrg.prompts import NchantdOfficePromptManager  # 2025-11-06 09:48:01
from nchantdoffice.widgets.documents.atnrg.prompts import NchantdOfficePrompt  # 2025-11-06 09:48:01
from nchantdoffice.widgets.documents.atnrg.prompts import NchantdOfficeSuperPromptPane  # 2025-11-06 09:48:01

# =========================================Local Library Modules======================================================||
# 2025-11-06 09:48:01

# ====================================================================================================================||
HERE = join(dirname(__file__))  # 2025-11-06 09:48:01
LOGMA = Logma(__name__)  # 2025-11-06 09:48:01
PXCFG = join(HERE, "_data_", "promptsTEST.yaml")  # 2025-11-06 09:48:01
CFG = kahndor.Instruct(PXCFG).load().dikt  # 2025-11-06 09:48:01
FIXTURES = kahndor.Instruct(join(HERE, "..", "fixtures", "fixtures.yaml")).load().dikt  # 2025-11-06 09:48:01
# 2025-11-06 09:48:01
# ====================================================================================================================||


class Test_NchantdContextListPane:  # 2025-11-06 09:48:01
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:48:01
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:48:01
        """"""

        return

    def reset(self):  # 2025-11-06 09:48:01
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:48:01
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:48:01
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass


class Test_NchantdOfficePromptManager:  # 2025-11-06 09:48:02
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:48:02
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:48:02
        """"""

        return

    def reset(self):  # 2025-11-06 09:48:02
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:48:02
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_initModel(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass


class Test_NchantdOfficePrompt:  # 2025-11-06 09:48:02
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:48:02
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:48:02
        """"""

        return

    def reset(self):  # 2025-11-06 09:48:02
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:48:02
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_cmd_select_model_new(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_set_chat_history_expiry(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_toggle_dual_models(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_get_prompt_max_length(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_init_drawer_context_inputs(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_init_drawer_document_config(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_init_drawer_models_config(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_init_drawer_quickstart(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_init_toolbox(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_inject_context(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_insert_input(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_save(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_set_prefix_context(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_set_suffix_context(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass


class Test_NchantdOfficeSuperPromptPane:  # 2025-11-06 09:48:02
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:48:02
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:48:02
        """"""

        return

    def reset(self):  # 2025-11-06 09:48:02
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:48:02
        """Executes a series of test functions in a sequential logic."""

        return self

    def test_add_model(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_insert_context(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_insert_document(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_insert_image(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_model_one_selected(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_model_two_selected(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_set_track_conversation(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_cmd_submit(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_context_handler(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_get_model_one_name(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_get_model_two_name(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initModel(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initView(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_initWidget(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_show_radio_buttons(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test_update_pane(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass

    def test___init__(self):  # 2025-11-06 09:48:02
        """"""
        if test_000:
            pass


class Test_Functions:  # 2025-11-06 09:48:02
    """"""

    @classmethod
    def setup_class(cls):  # 2025-11-06 09:48:02
        """"""

        return cls()

    @classmethod
    def teardown_class(cls):  # 2025-11-06 09:48:02
        """"""

        return

    def reset(self):  # 2025-11-06 09:48:02
        """"""
        self.setup_class()
        return self

    def test_all(self):  # 2025-11-06 09:48:02
        """Executes a series of test functions in a sequential logic."""

        return self


# ====================================================================================================================||
"""
  # 2025-11-06 09:48:01
"""
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
