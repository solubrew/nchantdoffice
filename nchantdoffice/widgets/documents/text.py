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
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from pyffice.document import PyfficeScript

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "text.yaml")


class NchantdOfficeScript(NchantdOfficeDocument, PyfficeScript):
    """Script/Script document - implements PyfficeScript"""
    
    PYTYPE = 'script'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for script documents"""
        return [
            {'id': 'run', 'icon': 'play', 'label': 'Run', 'method': 'run_script'},
            {'id': 'debug', 'icon': 'bug', 'label': 'Debug', 'method': 'debug_script'},
            {'id': 'terminal', 'icon': 'terminal', 'label': 'Terminal', 'method': 'open_terminal'},
            {'id': 'format', 'icon': 'align-left', 'label': 'Format', 'method': 'format_code'},
            {'id': 'find', 'icon': 'search', 'label': 'Find', 'method': 'find_in_script'},
            {'id': 'spell', 'icon': 'spell-check', 'label': 'Spell Check', 'method': 'spell_check'},
            {'id': 'wordcount', 'icon': 'counter', 'label': 'Word Count', 'method': 'word_count'},
        ]
    
    def __init__(self, name="Nchantd Script", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeScript"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self
    
    def run_script(self):
        """Run the script"""
        logma.info("Running script...")
        return self
    
    def debug_script(self):
        """Debug the script"""
        logma.info("Debugging script...")
        return self
    
    def open_terminal(self):
        """Open terminal"""
        logma.info("Opening terminal...")
        return self
    
    def format_code(self):
        """Format code"""
        logma.info("Formatting code...")
        return self
    
    def find_in_script(self):
        """Find in script"""
        logma.info("Finding in script...")
        return self
    
    def spell_check(self):
        """Spell check"""
        logma.info("Spell checking...")
        return self
    
    def word_count(self):
        """Word count"""
        logma.info("Counting words...")
        return self


class NchantdOfficeText(NchantdOfficeDocument):
    """Text document - implements PyfficeText"""
    
    PYTYPE = 'text'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for text documents"""
        return [
            {'id': 'format', 'icon': 'align-left', 'label': 'Format', 'method': 'format_text'},
            {'id': 'find_replace', 'icon': 'search', 'label': 'Find/Replace', 'method': 'find_replace'},
            {'id': 'spell', 'icon': 'spell-check', 'label': 'Spell Check', 'method': 'spell_check'},
        ]
    
    def __init__(self, name="Nchantd Text", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeText"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self
    
    def format_text(self):
        """Format text"""
        return self
    
    def find_replace(self):
        """Find and replace"""
        return self
    
    def spell_check(self):
        """Spell check"""
        return self


# ====================================================================================================================||
