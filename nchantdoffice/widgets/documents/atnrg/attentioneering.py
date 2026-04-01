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

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdNEWSDashboard:
    """A standardized dashboard for displaying NEWS to the user where the
    specific NEWS content is pulled from various sources using a pluggable
    algorythm"""

    def __init__(self):
        """ """


class NchantdNEWSTab(tabs.NchantdTab):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NMBFTNEWSLTab")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdNEWSTab, self).__init__(parent, self.config)

    def buildPane(self):
        """ """
        layout = pyqt.QVBoxLayout()
        sections = [
            [
                "Daily Updates",
            ]
        ]
        feeds = [
            "http://rss.cnn.com/rss/cnn_topstories.rss",
            "http://rssfeeds.usatoday.com/UsatodaycomNation-TopStories",
            "https://archive.nytimes.com/www.nytimes.com/services/xml/rss/index.html",
            "http://www.nbcnews.com/id/6257883/t/press-release/",
            "https://www.washingtontimes.com/feeds/",
            "https://www.huffingtonpost.in/news/rss/",
            "https://www.abc.net.au/news/rural/rss/",
            "https://www.theage.com.au/rssheadlines",
            "https://www.heraldsun.com.au/help-rss",
            "https://www.yahoo.com/news/rss",
            "https://www.yahoo.com/news/rss/us",
            "https://finance.yahoo.com/news/rssindex",
            "https://news.bitcoin.com/feed/",
        ]
        cnt = 0
        for section in sections:
            gb = pyqt.QGroupBox(section[0])
            scroll = pyqt.QScrollArea()
            # 			scroll.setFixedHeight(500)
            scroll.setWidget(gb)
            scroll.setWidgetResizable(True)
            gblo = pyqt.QVBoxLayout()
            for feed in feeds:
                try:
                    feeddata = feedparser.parse(feed)
                    if log:
                        print("Feeds", feeddata["feed"].keys())
                    if "title" in feeddata["feed"].keys():
                        cfg = {"text": feeddata["feed"]["title"]}
                        title = annotations.NchantdLabel(self).initWidget(cfg)
                    elif "summary" in feeddata["feed"].keys():
                        continue
                        # title = anns.NchantdLabel(feeddata['feed']['summary'])
                    else:
                        continue
                        if log:
                            print("Feed Keys", feeddata["feed"].keys())
                except:
                    cfg = {"text": "Unknown"}
                    title = annotations.NchantdLabel(self).initWidget(cfg)
                feedlo = pyqt.QVBoxLayout()
                feedlo.addWidget(title)
                gblo.addLayout(feedlo)
            gb.setLayout(gblo)
            layout.addWidget(scroll, cnt)
            cnt += 1
        self.setLayout(layout)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
