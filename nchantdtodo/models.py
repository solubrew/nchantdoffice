# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid: <^(UUID)^>
	name:
	description: >
	expirary: <[expiration]>
	version: <[version]>
	path: <[LEXIvrs]>
	outline: <[outline]>
	authority: document|this
	security: sec|lvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
from os.path import abspath, dirname, exists, join
import uuid
import datetime as dt

# ===============================================================================||
import simplejson as j
from pandas import DataFrame

# ===============================================================================||
from condor import condor  # ||
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.models import models, treemodels
from nchantrs.models.tabsetmodels import NchantdTabSetModel
from nchantrs.dstruct.trees import NchantdTreeGenerator
from nchantrs.libraries import qpandas
from ogma.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), '')  # ||
log = False
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, '_data_', 'models.yaml')

class NTDAppModel(NchantdCloakModel):
	"""
	Initializes an instance of NTDAppModel.

	:param parent: (optional) Parent object.
	:type parent: object
	:param cfg: (optional) Configuration dictionary.
	:type cfg: dict
	"""
	
	def __init__(self, parent=None, cfg={}):
		"""
		Initializes an instance of the NTDAppModel class.

		:param parent: The parent object (default is None).
		:param cfg: A dictionary containing configuration settings (default is an empty dictionary).

		"""
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NTDAppModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: logma.info(f"NTDAppModel Config\n {self.config.dikt.keys()}")
		super(NTDAppModel, self).__init__(parent)

	def buildModel(self):
		""" """
		return self

class NTDTreeModel(treemodels.NchantdTreeModel):
	"""
	:class:`NTDTreeModel`

	An Outlined but dynamic set of tree nodes based on data from the database

	"""
	def __init__(self, parent=None, root=None, cfg={}):
		"""
		Initializes an instance of the NTDTreeModel class.

		:param parent: The parent widget. Defaults to None.
		:type parent: object, optional
		:param root: The root object. Defaults to None.
		:type root: object, optional
		:param cfg: The configuration dictionary. Defaults to an empty dictionary.
		:type cfg: dict, optional
		"""
		self.config = condor.instruct(pxcfg).select('NTDTreeModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDTreeModel, self).__init__(parent, root, 'nchantdtodos')
		if log: logma.info(f'TODOTreeModel\n {self.src}')
		self.today = None

	def initData(self):
		""" """
		#self.genTreeNodes()
	


	def initModel(self):
		""""""
		super().initModel()
		self.buildNodes()
		return self
	
	def setToday(self, nid):
		"""
		Sets the current date as today and updates the action node if necessary.

		:param nid: The unique identifier of the action node.
		:return: None
		"""
		self.now = dt.datetime.now()
		if self.today != self.now.strftime('%Y-%m-%d'):
			self.updateActionNode(nid)
		self.today = self.now.strftime('%Y-%m-%d')
		return self
	
	def updateActionNode(self, nid):
		"""
		Update the action node with the given nid.

		:param nid: The ID of the node to update.
		:return: None
		"""
		
		self.deleteChildren(1)
		logma.info(f"Create Today Node")
		self.addNode(nid, self.today, 'livenode', 1, 0, self.nodebase, 'NTDActionTabSet', 1)
		self.addTab()
		return self
	
	def updateTimeline(self):
		""""""
		self.now = dt.datetime.now()
		return self

#TODO: 2024-06-23 need to integrate into application configuration
# was getting by with a generic TabSet Widget when tabs data
# was being handled by the tree logic
class NTDTabSetModel(NchantdTabSetModel):
	""""""
	def __init__(self, parent, cfg):
		""""""
		self.config = condor.instruct(pxcfg).select('NTDTabSetModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDTabSetModel, self).__init__(parent, cfg)

	def initModel(self, pos, node='1', newInstance=False):
		""""""
		super().initModel(pos, node, newInstance)
		return self

	def initNTDAddConcernTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDAddEventTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDAddResourceTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDAddTaskTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDAdministrateConcernsTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDAdministrateEventsTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDAdministrateResourcesTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDDaily15MinTrackerTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDDailyTaskTrackerTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDHistoryTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDOperationsSummaryTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDProjectsSummaryTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDRecentCompletedTasksTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNTDWeekly1DayTrackerTabModel(self, pid):
		""""""
		tabs = []
		return tabs

	def initNchantdNEWSTabModel(self, pid):
		""""""
		tabs = []
		return tabs



class NTDConcernModel():
	""""""
	def __init__(self):
		""""""

	def deleteConcern(self):
		""""""
	
	def getConcerns(self):
		""""""
	
	def newConcern(self):
		""""""

	def selectConcern(self):
		""""""

	def updateConcern(self):
		""""""



class NTDDailyTrackerModel():
	""""""
	
	def __init__(self):
		""""""


class NTDTaskModel():
	""""""
	
	def __init__(self):
		""""""

class NTDEventModel():
	""""""
	
	def __init__(self):
		""""""


class NTDprojectModel():
	""""""
	
	def __init__(self):
		""""""


class NTDProjectsModel():
	""""""
	
	def __init__(self):
		""""""


class NTDOperationModel():
	""""""
	
	def __init__(self):
		""""""


class NTDOperationsModel():
	""""""
	
	def __init__(self):
		""""""


class NTDSplitTaskModel():
	""""""
	
	def __init__(self):
		""""""


class NTDCalendarModel():
	""""""
	
	def __init__(self):
		""""""