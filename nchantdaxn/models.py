# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid: 
	name: AXN and ProjectAXN Data Models
	description: >
		Models for managing AXN tasks and ProjectAXN projects within the Nchantrs
		framework. Provides integration between ProjectAXN YAML stores and Nchantrs
		tree/tab models.
	expirary: 
	version: 0.0.0.0.0.0
	path: nchantdaxn.models
	outline: >
		- NchantdAXNModel: Main application model
		- NchantdAXNTreeModel: Tree view for tasks/projects
		- NchantdAXNTabSetModel: Tab-based detail views
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
from condor import condor
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.models import models, treemodels
from nchantrs.models.tabsetmodels import NchantdTabSetModel
from nchantrs.dstruct.trees import NchantdTreeGenerator
from nchantrs.libraries import qpandas
from ogma.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, '_data_', 'models.yaml')

# Import ProjectAXN models
import sys
sys.path.insert(0, '/home/solubrew/.arthr/workspace/projectaxn')
from projectaxn.models.task import AXNTask, AXNTaskStatus, AXNTaskPriority
from projectaxn.models.project import ProjectAXNProject, ProjectStatus


class NchantdAXNModel(NchantdCloakModel):
	"""
	Main application model for NchantdAXN.
	Manages AXN tasks and ProjectAXN projects with YAML-based storage.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: logma.info(f"NchantdAXNModel Config\n {self.config.dikt.keys()}")
		super(NchantdAXNModel, self).__init__(parent)
		
		# Initialize stores
		self.task_store = None
		self.project_store = None
		self.link_store = None
	
	def buildModel(self):
		"""Initialize the model and stores."""
		self.initStores()
		return self
	
	def initStores(self):
		"""Initialize ProjectAXN YAML stores."""
		try:
			from projectaxn.yaml_store import TaskStore, ProjectStore, LinkStore
			
			# Get paths from config
			axn_path = self.config.dikt.get('axn_path', '/home/solubrew/.arthr/workspace/axn')
			shared_path = self.config.dikt.get('shared_path', axn_path)
			
			self.task_store = TaskStore(shared_path)
			self.project_store = ProjectStore(shared_path)
			self.link_store = LinkStore(shared_path)
			
			logma.info(f"NchantdAXN Stores initialized from {shared_path}")
		except Exception as e:
			logma.error(f"Failed to initialize stores: {e}")
	
	def getTasks(self, filters=None):
		"""Get all tasks with optional filtering."""
		if not self.task_store:
			return []
		return self.task_store.list_tasks(filters)
	
	def getProjects(self):
		"""Get all projects."""
		if not self.project_store:
			return []
		return self.project_store.list_projects()
	
	def getTask(self, task_id):
		"""Get a specific task."""
		if not self.task_store:
			return None
		return self.task_store.get_task(task_id)
	
	def getProject(self, project_id):
		"""Get a specific project."""
		if not self.project_store:
			return None
		return self.project_store.get_project(project_id)
	
	def getTasksForProject(self, project_id):
		"""Get all tasks linked to a project."""
		if not self.link_store:
			return []
		task_ids = self.link_store.get_linked_task_ids(project_id)
		return [self.getTask(tid) for tid in task_ids if self.getTask(tid)]


class NchantdAXNTreeModel(treemodels.NchantdTreeModel):
	"""
	Tree model for displaying AXN tasks and projects in a hierarchical view.
	"""
	def __init__(self, parent=None, root=None, cfg={}):
		self.config = condor.instruct(pxcfg).select('NchantdAXNTreeModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdAXNTreeModel, self).__init__(parent, root, 'nchantdaxn')
		if log: logma.info(f'AXNTreeModel')
		self.app_model = None
	
	def initData(self):
		"""Initialize tree data from AXN stores."""
		pass
	
	def initModel(self):
		"""Build the tree nodes."""
		super().initModel()
		self.buildNodes()
		return self
	
	def buildNodes(self):
		"""Build tree nodes from projects and tasks."""
		if not self.app_model:
			return
		
		# Add Projects node
		self.addNode('projects', 'Projects', 'groupnode', 0, 0, self.nodebase, 'NchantdAXNProjectTabSet', 0)
		
		# Add Tasks node
		self.addNode('tasks', 'Tasks', 'groupnode', 0, 0, self.nodebase, 'NchantdAXNTaskTabSet', 0)
		
		# Load projects
		projects = self.app_model.getProjects()
		for proj in projects:
			self.addNode(
				proj.get('id', ''),
				proj.get('name', 'Unnamed'),
				'livenode',
				1, 0,
				'projects',
				'NchantdAXNProjectDetailTabSet',
				1
			)
		
		# Load tasks
		tasks = self.app_model.getTasks()
		for task in tasks:
			# Determine status icon
			status = task.get('status', 'pending')
			icon = 'checkbox-checked' if status == 'completed' else 'checkbox-unchecked'
			
			self.addNode(
				task.get('id', ''),
				task.get('name', 'Unnamed'),
				'livenode',
				1, 0,
				'tasks',
				'NchantdAXNTaskDetailTabSet',
				1
			)
		
		self.addTab()
		return self
	
	def refresh(self):
		"""Refresh the tree from stores."""
		self.deleteChildren(1)
		self.buildNodes()
		return self


class NchantdAXNTabSetModel(NchantdTabSetModel):
	"""
	Tab set model for AXN detail views.
	"""
	def __init__(self, parent, cfg):
		self.config = condor.instruct(pxcfg).select('NchantdAXNTabSetModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdAXNTabSetModel, self).__init__(parent, cfg)
	
	def initModel(self, pos, node='1', newInstance=False):
		super().initModel(pos, node, newInstance)
		return self
	
	def initAXNSummaryTabModel(self, pid):
		"""Summary tab for AXN overview."""
		tabs = []
		return tabs
	
	def initAXNProjectListTabModel(self, pid):
		"""Project list tab."""
		tabs = []
		return tabs
	
	def initAXNTaskListTabModel(self, pid):
		"""Task list tab."""
		tabs = []
		return tabs
	
	def initAXNProjectDetailTabModel(self, pid):
		"""Project detail tab."""
		tabs = []
		return tabs
	
	def initAXNTaskDetailTabModel(self, pid):
		"""Task detail tab."""
		tabs = []
		return tabs
	
	def initAXNTimelineTabModel(self, pid):
		"""Timeline/Gantt tab."""
		tabs = []
		return tabs
	
	def initAXNMilestonesTabModel(self, pid):
		"""Milestones tab."""
		tabs = []
		return tabs


# Lightweight model classes for direct use
class NchantdAXNTaskModel:
	"""Wrapper for AXNTask in Nchantrs context."""
	
	def __init__(self, task_data=None):
		self._task = None
		if task_data:
			if isinstance(task_data, dict):
				self._task = AXNTask.from_dict(task_data)
			elif isinstance(task_data, AXNTask):
				self._task = task_data
	
	@property
	def task(self):
		return self._task
	
	def to_dict(self):
		if self._task:
			return self._task.to_dict()
		return {}
	
	@classmethod
	def from_dict(cls, data):
		return cls(AXNTask.from_dict(data))


class NchantdAXNProjectModel:
	"""Wrapper for ProjectAXNProject in Nchantrs context."""
	
	def __init__(self, project_data=None):
		self._project = None
		if project_data:
			if isinstance(project_data, dict):
				self._project = ProjectAXNProject.from_dict(project_data)
			elif isinstance(project_data, ProjectAXNProject):
				self._project = project_data
	
	@property
	def project(self):
		return self._project
	
	def to_dict(self):
		if self._project:
			return self._project.to_dict()
		return {}
	
	@classmethod
	def from_dict(cls, data):
		return cls(ProjectAXNProject.from_dict(data))
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
