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
from nchantrs.libraries import qpandas
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, '_data_', '.yaml')


class NchantdDocumentModel():
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdDocumentModel')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdDocumentModel, self).__init__(self.parent, self.config)

	def get_document(self, uuid):
		""""""
		params = {}
		cfg = {}
		self.app.model.store.docs['db'].read(params, cfg)
		return self

	def initModel(self):
		""""""
		return self

	def save_document(self):
		""""""
		return self


class NchantdFilmStripDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdFilmStripDocumentModel')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdFilmStripDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdFormDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdFormDocumentModel')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdFormDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdImageDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('Nchantd')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdImageDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdManagerModel(qpandas.DataFrameModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('Nchantd')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdManagerModel, self).__init__()

	def initModel(self):
		""""""
		return self


class NchantdMatrixDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('Nchantd')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdMatrixDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdPDFDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('Nchantd')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdPDFDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdScriptDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdScriptDocumentModel')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdScriptDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdSlideShowDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('Nchantd')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdSlideShowDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdSurveyDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdSurveyDocumentModel')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdSurveyDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdWebBrowserDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdWebBrowserDocumentModel')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdWebBrowserDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


class NchantdWebAppDocumentModel(NchantdDocumentModel):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdWebAppDocumentModel')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdWebAppDocumentModel, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
