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
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt

# from nchantrs.widgets.browsers.browsers import NchantdWebApp
# from nchantrs.widgets.tables import NchantdList
from nchantrs.widgets.managers import NchantdManager
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.groups import NchantdVScrollGroupBox, NchantdHScrollGroupBox
from nchantrs.widgets.forms.forms import NchantdDynamicEntryForm, NchantdForm
from pyffice.forms.surveys import PyfficeSurveyManager

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "surveys.yaml")


class NchantdOfficeEvaluation(NchantdWidget):
    """An evaluation is the object that represents the actual entry of information about another object such as an
    image or artical

    """

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdEvaluation")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)

    def initModel(self):
        """"""
        return self

    def initView(self):
        """"""
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeSurvey(NchantdOfficeEvaluation):
    """A Survey is an evaulation solicited from a group which requires some additional information ontop of a
    standard evaluation"""

    def __init__(self, parent=None, cfg=None):
        """ """
        icfg = {}
        super().__init__(parent, icfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeSurvey").override(cfg))
        self.forms = {}
        self.questions = {}
        self.responses = {}
        self.question_options = []
        self.creator_uuid = self.widget().user.uuid

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def assemble_document(self, document_df):
        """
        process the dataframe to reassemble the Survey Document and decode the content
        :param document_df:
        :return:
        """
        return self

    def add_question(self):
        """"""

    def remove_question(self):
        """"""

    def deploy_survey(self):
        """"""

    def collect_responses(self):
        """"""


class NchantdOfficeSurveyManager(NchantdManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeSurveyManager")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)
        self.manager = PyfficeSurveyManager()

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_survey(self):
        """
        TODO: need to be able to select a form from various sources as part of the survey
        :return:
        """

    def add_survey_tag(self):
        """"""

    def close_survey(self):
        """"""

    def collect_responses(self):
        """"""
        return self

    def create_question_groups(self):
        """"""

    def open_survey(self, date_time=None):
        """"""

    def remove_survey(self):
        """"""

    def remove_survey_tag(self):
        """"""

    def parse_document(self):
        """
        break up each question in the survey into a separate media content entry
        media content is specifically an nchantrs concept but it may make sense to bring some of that over here
        a survey needs to be defined seperately from a form in the same way it is divided in nchantrs

        Surveys are a workflow of forms
        :return:
        """


class NchantdOfficeSurveyResponder(NchantdManager):
    """Nchantd Office Survey Responder is a manager to allow a user to review and select any surveys they would like to
    complete"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeSurveyResponder")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)
        self.active_item = None
        self.form = None
        self.completed_survey_list = None
        self.completed_survey_group = None
        self.open_survey_list = None
        self.open_survey_group = None
        self.responder_uuid = self.app.model.user.uuid

    def initModel(self):
        """"""
        super().initModel()
        self.select_item(self.config.dikt.get("survey_uuid", None))
        return self

    def initView(self):
        """"""
        super().initView({"layout": "horizontal"})
        layout = pyqt.QVBoxLayout()
        self.open_survey_group = NchantdVScrollGroupBox()
        self.open_survey_group.setTitle("Open Surveys")
        self.update_open_survey_group()
        layout.addLayout(self.open_survey_group.layout)
        self.completed_survey_group = NchantdVScrollGroupBox()
        self.completed_survey_group.setTitle("Recently Completed Surveys")
        layout.addLayout(self.completed_survey_group.layout)
        self.layout.addLayout(layout)
        self.open_survey_group = NchantdHScrollGroupBox()
        self.open_survey_group.setTitle("Selected Survey")
        self.layout.addLayout(self.open_survey_group.layout)
        # self.update_survey_type(self.active_item.type, self.active_item.id)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def select_item(self, uuid=None):
        """"""
        self.active_item = self.app.model.store.get_document_content("survey", uuid)

    def update_completed_survey_group(self):
        """"""
        # self.completed_survey_group.clear()
        cfg = {}
        self.completed_survey_list = NchantdList(self, cfg).initWidget()
        self.completed_survey_group.addWidget(self.completed_survey_list)
        return self

    def update_open_survey_group(self):
        """"""
        # self.open_survey_group.clear()
        cfg = {}
        self.open_survey_list = NchantdList(self, cfg).initWidget()
        self.open_survey_group.addWidget(self.open_survey_list)
        return self

    def update_survey_type(self, type_="internal", id=""):
        """"""
        if type_ in ("google", "youform", "typeform"):
            cfg = {"url_code": f"form_{id}"}
            self.form = NchantdWebApp(self, cfg).initWidget()
        elif type_ == "internal":
            cfg = {"id": id}
            self.form = NchantdForm(self, cfg).initWidget()
        elif type_ == "internal-dynamic":
            cfg = {"id": id}
            self.form = NchantdDynamicEntryForm(self, cfg).initWidget()
        else:
            raise Exception("Unknown Survey Type")
        self.open_survey_group.addWidget(self.form)


class NchantdOfficeSurveyFormBuilder(NchantdManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeSurveyFormBuilder")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)
        self.dynamic_form = None

    def initModel(self):
        """"""
        super().initModel()
        self.rebuild_form()
        return self

    def initView(self):
        """"""
        super().initView()
        self.questions_layout = pyqt.QVBoxLayout()
        self.layout.addLayout(self.questions_layout)
        self.question_layout = pyqt.QVBoxLayout()
        self.layout.addLayout(self.question_layout)
        self.deploy_layout = pyqt.QHBoxLayout()
        self.layout.addLayout(self.deploy_layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def rebuild_form(self):
        """"""
        cfg = {}
        self.dynamic_form = NchantdDynamicEntryForm(self, cfg)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
