class NchantdTODOCalendarTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdTODOTree")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOCalendarTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODOContactsTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdTODOContactsTab")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOContactsTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODOContactsLevelSummaryTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg)
        self.config.select("NchantdTODOContactsLevelTab").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOContactLevelSummaryTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODOContactTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdTODOContactTab")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOContactTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODODelegationTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdTODODelegationTab")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODODelegationTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODOeMailTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.config = kahndor.instruct(pxcfg).select("NchantdTODOeMailTab")
        self.config.override(cfg)  # ||
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOeMailTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODOEntryForm(forms.NchantdDynamicRecordEntryForm):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.config = kahndor.instruct(pxcfg).select("NchantdTODOEntryForm")
        self.config.override(cfg)  # ||
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOEntryForm, self).__init__(parent, cfg)

    def buildPane(self):
        """ """
        cnt, self.fieldWDGTs = 0, {}
        fields = self.config.dikt["params"]["fields"]
        self.loadFields(fields)
        for predecessor in self.predecessors:
            self.predecssorForms[predecessor[0]] = NchantdTODOPredecessorEntryForm()
        self.addPredecessorBTN = NchantdButton("Add Predecessor")
        return self

    def initView(self):
        """ """
        self.predecessorTasks = []
        return self


class NchantdTODOEventsListTab(tables.NchantdTable):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg)
        self.config.select("NchantdTODOEventsListTab").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOFundTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODOFundSummaryTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg)
        self.config.select("NchantdTODOFundSummaryTab").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOFundTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODOJournalTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.config = kahndor.instruct(pxcfg).override(cfg)  # ||
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOJournalTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODONeedActionTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdTODOTree").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODONeedActionTab, self).__init__(parent, self.config)

    def buildTab(self):
        """ """
        self.editors = {}
        self.forms = {}
        layout_b = pyqt.QVBoxLayout()
        labels = [
            "Yesterday - Monday 2022/01/30",
            "Today - Tuesday 2022/01/31",
            "Tommorrow - Wednesday 2022/02/01",
            "Thursday 2022/02/02",
            "Friday 2022/02/03",
            "Saturday 2022/01/04",
            "Sunday 2022/01/05",
            "Monday 2022/01/06 - Sunday 2022/01/13",
            "Monday 2022/01/06 - Sunday 2022/01/13",
            "Monday 2022/01/06 - Sunday 2022/01/13",
            "Monday 2022/01/06 - Sunday 2022/01/13",
        ]
        cnt = 0
        for label in labels:
            layout_b.addWidget(annotations.NchantdLabel(label))
            self.editors[cnt] = editors.NchandDocEditor(self).initWidget()
            layout_b.addWidget(self.editors[cnt])
            cnt += 1
        layout_c = pyqt.QVBoxLayout()
        self.forms[0] = NchantdTODOEntryForm(self).initWidget()
        self.editors[cnt] = editors.NchandDocEditor(self).initWidget()
        layout_c.addWidget(self.editors[cnt])
        layout_a = pyqt.QHBoxLayout()
        layout_a.addWidget(layout_b)
        layout_a.addWidget(layout_c)
        return self


class NchantdTODOPastSummaryTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdTODOTree")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOPastSummaryTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self


class NchantdTODOPredecessorEntryForm(forms.NchantdDynamicRecordEntryForm):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.config = kahndor.instruct(pxcfg)
        self.config.select("NchantdTODOPredecessorEntryForm").override(cfg)  # ||
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOPredecessorEntryForm, self).__init__(parent, cfg)

    def buildPane(self):
        """ """
        cnt, self.fieldWDGTs = 0, {}
        fields = self.config.dikt["params"]["fields"]
        self.loadFields(fields)
        return self

    def initView(self):
        """ """
        self.predecessorTasks = []
        return self


class NchantdTODOWaitingOnTab(tabsets.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdTODOWaitingOnTab")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdTODOWaitingOnTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        return self
