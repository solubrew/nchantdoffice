# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid: 
	name: AXN and ProjectAXN Dialogs
	description: >
		Dialog classes for creating and editing AXN tasks and ProjectAXN projects.
	authority: document|this
	security: sec|lvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
from os.path import join
import datetime as dt

# ===============================================================================||
from condor import condor
from ogma.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, '_data_', 'dialogs.yaml')


class NchantdAXNTaskDialog:
	"""
	Dialog for creating and editing AXN tasks.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNTaskDialog')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		# Task fields
		self.task_id = None
		self.name = ""
		self.status = "pending"
		self.priority = 2
		self.progress = 0.0
		self.start_date = None
		self.end_date = None
		self.duration_days = 1
		self.assignee = ""
		self.tags = []
		self.notes = ""
		
		# For linking to project
		self.project_id = None
	
	def run(self):
		"""Show the dialog and return the task data."""
		# This would be implemented with the actual GUI framework
		# For now, return the data dict
		return self.getData()
	
	def getData(self):
		"""Get the task data as a dictionary."""
		return {
			'id': self.task_id,
			'name': self.name,
			'status': self.status,
			'priority': self.priority,
			'progress': self.progress,
			'start_date': self.start_date.isoformat() if self.start_date else None,
			'end_date': self.end_date.isoformat() if self.end_date else None,
			'duration_days': self.duration_days,
			'assignee': self.assignee,
			'tags': self.tags,
			'notes': self.notes,
			'project_id': self.project_id,
		}
	
	def loadFromDict(self, data):
		"""Load task data from a dictionary."""
		self.task_id = data.get('id')
		self.name = data.get('name', '')
		self.status = data.get('status', 'pending')
		self.priority = data.get('priority', 2)
		self.progress = data.get('progress', 0.0)
		
		start = data.get('start_date')
		if start:
			self.start_date = dt.datetime.fromisoformat(start) if isinstance(start, str) else start
		
		end = data.get('end_date')
		if end:
			self.end_date = dt.datetime.fromisoformat(end) if isinstance(end, str) else end
		
		self.duration_days = data.get('duration_days', 1)
		self.assignee = data.get('assignee', '')
		self.tags = data.get('tags', [])
		self.notes = data.get('notes', '')


class NchantdAXNProjectDialog:
	"""
	Dialog for creating and editing ProjectAXN projects.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNProjectDialog')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		# Project fields
		self.project_id = None
		self.name = ""
		self.description = ""
		self.status = "planning"
		self.start_date = None
		self.end_date = None
		self.tags = []
		self.notes = ""
	
	def run(self):
		"""Show the dialog and return the project data."""
		return self.getData()
	
	def getData(self):
		"""Get the project data as a dictionary."""
		return {
			'id': self.project_id,
			'name': self.name,
			'description': self.description,
			'status': self.status,
			'start_date': self.start_date.isoformat() if self.start_date else None,
			'end_date': self.end_date.isoformat() if self.end_date else None,
			'tags': self.tags,
			'notes': self.notes,
		}
	
	def loadFromDict(self, data):
		"""Load project data from a dictionary."""
		self.project_id = data.get('id')
		self.name = data.get('name', '')
		self.description = data.get('description', '')
		self.status = data.get('status', 'planning')
		
		start = data.get('start_date')
		if start:
			self.start_date = dt.datetime.fromisoformat(start) if isinstance(start, str) else start
		
		end = data.get('end_date')
		if end:
			self.end_date = dt.datetime.fromisoformat(end) if isinstance(end, str) else end
		
		self.tags = data.get('tags', [])
		self.notes = data.get('notes', '')


class NchantdAXNLinkDialog:
	"""
	Dialog for linking tasks to projects.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNLinkDialog')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		self.selected_task_ids = []
		self.selected_project_id = None
	
	def run(self):
		"""Show the link dialog."""
		return self.getData()
	
	def getData(self):
		"""Get the link data."""
		return {
			'project_id': self.selected_project_id,
			'task_ids': self.selected_task_ids,
		}


class NchantdAXNProgressDialog:
	"""
	Dialog for updating task progress.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNProgressDialog')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		self.task_id = None
		self.progress = 0.0
		self.notes = ""
	
	def run(self):
		"""Show the progress dialog."""
		return self.getData()
	
	def getData(self):
		"""Get progress update data."""
		return {
			'task_id': self.task_id,
			'progress': self.progress,
			'notes': self.notes,
		}


class NchantdAXNImportDialog:
	"""
	Dialog for importing tasks from YAML files.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNImportDialog')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		self.import_path = ""
		self.imported_count = 0
		self.errors = []
	
	def run(self):
		"""Run import and return results."""
		return self.getData()
	
	def getData(self):
		"""Get import results."""
		return {
			'path': self.import_path,
			'count': self.imported_count,
			'errors': self.errors,
		}
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
