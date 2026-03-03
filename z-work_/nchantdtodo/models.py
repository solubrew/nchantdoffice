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

# Pyffice for document automation
try:
    from pyffice.text import PyfficeScript
    PYFFICE_AVAILABLE = True
except ImportError:
    PYFFICE_AVAILABLE = False
    PyfficeScript = None

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
	"""
	Model for managing concerns with Pyffice integration.
	
	Uses Pyffice for document handling, serialization, and export.
	"""
	
	def __init__(self):
		"""Initialize concern model with Pyffice document support."""
		self.concerns = []
		if PYFFICE_AVAILABLE:
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def newConcern(self, name, code, description=""):
		"""
		Create a new concern.
		
		Args:
			name: Concern name
			code: Concern code
			description: Concern description
		
		Returns:
			Concern dictionary
		"""
		concern_id = str(uuid.uuid4())
		concern = {
			'id': concern_id,
			'name': name,
			'code': code,
			'description': description,
			'created_at': dt.datetime.now().isoformat()
		}
		
		if PYFFICE_AVAILABLE and description:
			concern['_document'] = PyfficeScript(description)
		
		self.concerns.append(concern)
		return concern
	
	def getConcerns(self):
		"""Get all concerns."""
		return self.concerns
	
	def selectConcern(self, concern_id):
		"""Select a concern by ID."""
		for c in self.concerns:
			if c['id'] == concern_id:
				return c
		return None
	
	def updateConcern(self, concern_id, data):
		"""
		Update a concern.
		
		Args:
			concern_id: Concern ID
			data: Fields to update
		
		Returns:
			Updated concern
		"""
		concern = self.selectConcern(concern_id)
		if concern:
			concern.update(data)
			if 'description' in data and PYFFICE_AVAILABLE:
				concern['_document'] = PyfficeScript(data['description'])
		return concern
	
	def deleteConcern(self, concern_id):
		"""Delete a concern by ID."""
		self.concerns = [c for c in self.concerns if c['id'] != concern_id]
	
	def to_json(self):
		"""Export concerns as JSON."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.concerns, indent=2))
			return doc.to_string()
		return j.dumps(self.concerns, indent=2)
	
	def to_yaml(self):
		"""Export concerns as YAML."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.concerns))
			return doc.to_yaml_string()
		import yaml
		return yaml.dump(self.concerns)
	
	def summarize(self, format="text"):
		"""Get summary of concerns."""
		summary = {
			'total': len(self.concerns),
			'concerns': self.concerns
		}
		
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(summary))
			return doc.to_summary(format=format)
		
		if format == "json":
			return j.dumps(summary, indent=2)
		return str(summary)



class NTDDailyTrackerModel():
	"""
	Model for daily time tracking with Pyffice integration.
	"""
	
	def __init__(self):
		"""Initialize daily tracker model."""
		self.tracking_entries = []
		if PYFFICE_AVAILABLE:
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def addEntry(self, task_id, start_time, end_time, notes=""):
		"""Add a time tracking entry."""
		entry_id = str(uuid.uuid4())
		entry = {
			'id': entry_id,
			'task_id': task_id,
			'start_time': start_time,
			'end_time': end_time,
			'notes': notes,
			'created_at': dt.datetime.now().isoformat()
		}
		if PYFFICE_AVAILABLE and notes:
			entry['_document'] = PyfficeScript(notes)
		self.tracking_entries.append(entry)
		return entry
	
	def getEntries(self, date=None):
		"""Get tracking entries, optionally filtered by date."""
		if date:
			date_str = date if isinstance(date, str) else date.strftime('%Y-%m-%d')
			return [e for e in self.tracking_entries if e.get('start_time', '').startswith(date_str)]
		return self.tracking_entries
	
	def to_json(self):
		"""Export as JSON."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.tracking_entries, indent=2))
			return doc.to_string()
		return j.dumps(self.tracking_entries, indent=2)


class NTDTaskModel():
	"""
	Model for managing tasks with Pyffice integration.
	
	Uses Pyffice for document handling, serialization, and export.
	"""
	
	def __init__(self):
		"""Initialize task model with Pyffice document support."""
		self.tasks = []
		if PYFFICE_AVAILABLE:
			# Pyffice document for task notes/descriptions
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def createTask(self, name, due_date, estimated_hours, description=""):
		"""
		Create a new task with Pyffice document handling.
		
		Args:
			name: Task name
			due_date: Due date
			estimated_hours: Estimated hours
			description: Task description/notes
		
		Returns:
			Task dictionary
		"""
		task_id = str(uuid.uuid4())
		task = {
			'id': task_id,
			'name': name,
			'due_date': due_date,
			'estimated_hours': estimated_hours,
			'description': description,
			'status': 'pending',
			'completed': False
		}
		
		# Use Pyffice for description handling
		if PYFFICE_AVAILABLE and description:
			self.document = PyfficeScript(description)
			task['_document'] = self.document
		
		self.tasks.append(task)
		return task
	
	def getTask(self, task_id):
		"""Get task by ID."""
		for task in self.tasks:
			if task['id'] == task_id:
				return task
		return None
	
	def updateTask(self, task_id, data):
		"""
		Update task with Pyffice export capabilities.
		
		Args:
			task_id: Task ID
			data: Fields to update
		
		Returns:
			Updated task
		"""
		task = self.getTask(task_id)
		if task:
			task.update(data)
			# Update Pyffice document if description changed
			if 'description' in data and PYFFICE_AVAILABLE:
				task['_document'] = PyfficeScript(data['description'])
		return task
	
	def deleteTask(self, task_id):
		"""Delete a task by ID."""
		self.tasks = [t for t in self.tasks if t['id'] != task_id]
	
	def completeTask(self, task_id):
		"""Mark task as complete."""
		task = self.getTask(task_id)
		if task:
			task['completed'] = True
			task['status'] = 'completed'
		return task
	
	def getTasks(self, filters={}):
		"""
		Get tasks with optional filters.
		
		Returns:
			List of tasks (or Pyffice serialized if requested)
		"""
		result = self.tasks
		
		if filters.get('status'):
			result = [t for t in result if t.get('status') == filters['status']]
		if filters.get('completed') is not None:
			result = [t for t in result if t.get('completed') == filters['completed']]
		
		return result
	
	def to_json(self):
		"""
		Export all tasks as JSON (via Pyffice).
		
		Returns:
			JSON string
		"""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.tasks, indent=2))
			return doc.to_string()
		return j.dumps(self.tasks, indent=2)
	
	def to_yaml(self):
		"""
		Export all tasks as YAML (via Pyffice).
		
		Returns:
			YAML string
		"""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.tasks))
			return doc.to_yaml_string()
		import yaml
		return yaml.dump(self.tasks)
	
	def save_tasks(self, filepath):
		"""
		Save tasks to file (via Pyffice).
		
		Args:
			filepath: Path to save
		"""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.tasks))
			doc.save(filepath)
		else:
			with open(filepath, 'w') as f:
				j.dump(self.tasks, f, indent=2)
	
	def load_tasks(self, filepath):
		"""
		Load tasks from file (via Pyffice).
		
		Args:
			filepath: Path to load from
		"""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript('')
			doc.open_file(filepath)
			self.tasks = j.loads(doc.content)
		else:
			with open(filepath, 'r') as f:
				self.tasks = j.load(f)
	
	def summarize_tasks(self, format="text"):
		"""
		Get summary of tasks in various formats.
		
		Args:
			format: Output format (text, json, yaml, md)
		
		Returns:
			Summary string
		"""
		summary_data = {
			'total_tasks': len(self.tasks),
			'completed': len([t for t in self.tasks if t.get('completed')]),
			'pending': len([t for t in self.tasks if not t.get('completed')]),
			'tasks': self.tasks
		}
		
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(summary_data))
			return doc.to_summary(format=format)
		
		if format == "json":
			return j.dumps(summary_data, indent=2)
		elif format == "yaml":
			import yaml
			return yaml.dump(summary_data)
		elif format == "md":
			md = f"# Task Summary\n\n"
			md += f"- Total: {summary_data['total_tasks']}\n"
			md += f"- Completed: {summary_data['completed']}\n"
			md += f"- Pending: {summary_data['pending']}\n"
			return md
		return str(summary_data)


class NTDprojectModel():
	"""
	Model for managing projects with Pyffice integration.
	"""
	
	def __init__(self):
		"""Initialize project model."""
		self.projects = []
		if PYFFICE_AVAILABLE:
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def createProject(self, name, description=""):
		"""Create a new project."""
		project_id = str(uuid.uuid4())
		project = {
			'id': project_id,
			'name': name,
			'description': description,
			'created_at': dt.datetime.now().isoformat(),
			'status': 'active'
		}
		if PYFFICE_AVAILABLE and description:
			project['_document'] = PyfficeScript(description)
		self.projects.append(project)
		return project
	
	def getProjects(self):
		"""Get all projects."""
		return self.projects
	
	def updateProject(self, project_id, data):
		"""Update a project."""
		for p in self.projects:
			if p['id'] == project_id:
				p.update(data)
				if 'description' in data and PYFFICE_AVAILABLE:
					p['_document'] = PyfficeScript(data['description'])
				return p
		return None
	
	def deleteProject(self, project_id):
		"""Delete a project."""
		self.projects = [p for p in self.projects if p['id'] != project_id]
	
	def to_json(self):
		"""Export projects as JSON."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.projects, indent=2))
			return doc.to_string()
		return j.dumps(self.projects, indent=2)
	
	def to_yaml(self):
		"""Export projects as YAML."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.projects))
			return doc.to_yaml_string()
		import yaml
		return yaml.dump(self.projects)


class NTDProjectsModel():
	"""
	Model for managing project collections.
	"""
	
	def __init__(self):
		"""Initialize projects collection model."""
		self.projects = []
		if PYFFICE_AVAILABLE:
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def addProject(self, project):
		"""Add a project to collection."""
		self.projects.append(project)
	
	def getProjects(self):
		"""Get all projects."""
		return self.projects
	
	def to_json(self):
		"""Export as JSON."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.projects, indent=2))
			return doc.to_string()
		return j.dumps(self.projects, indent=2)


class NTDOperationModel():
	"""
	Model for managing operations.
	"""
	
	def __init__(self):
		"""Initialize operation model."""
		self.operations = []
		if PYFFICE_AVAILABLE:
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def createOperation(self, name, description=""):
		"""Create a new operation."""
		op_id = str(uuid.uuid4())
		operation = {
			'id': op_id,
			'name': name,
			'description': description,
			'created_at': dt.datetime.now().isoformat()
		}
		if PYFFICE_AVAILABLE and description:
			operation['_document'] = PyfficeScript(description)
		self.operations.append(operation)
		return operation
	
	def getOperations(self):
		"""Get all operations."""
		return self.operations
	
	def to_json(self):
		"""Export as JSON."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.operations, indent=2))
			return doc.to_string()
		return j.dumps(self.operations, indent=2)


class NTDOperationsModel():
	"""
	Model for managing operations collections.
	"""
	
	def __init__(self):
		"""Initialize operations collection model."""
		self.operations = []
		if PYFFICE_AVAILABLE:
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def addOperation(self, operation):
		"""Add an operation."""
		self.operations.append(operation)
	
	def getOperations(self):
		"""Get all operations."""
		return self.operations


class NTDSplitTaskModel():
	"""
	Model for managing task splits.
	"""
	
	def __init__(self):
		"""Initialize split task model."""
		self.splits = []
		if PYFFICE_AVAILABLE:
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def splitTask(self, task_id, split_count):
		"""Split a task into subtasks."""
		split_id = str(uuid.uuid4())
		split = {
			'id': split_id,
			'parent_task_id': task_id,
			'split_count': split_count,
			'created_at': dt.datetime.now().isoformat()
		}
		self.splits.append(split)
		return split
	
	def getSplits(self, task_id):
		"""Get splits for a task."""
		return [s for s in self.splits if s['parent_task_id'] == task_id]


class NTDCalendarModel():
	"""
	Model for calendar functionality with Pyffice integration.
	"""
	
	def __init__(self):
		"""Initialize calendar model."""
		self.events = []
		if PYFFICE_AVAILABLE:
			self.document = PyfficeScript("")
		else:
			self.document = None
	
	def createEvent(self, name, start_time, end_time, location=""):
		"""Create a new event."""
		event_id = str(uuid.uuid4())
		event = {
			'id': event_id,
			'name': name,
			'start_time': start_time,
			'end_time': end_time,
			'location': location,
			'created_at': dt.datetime.now().isoformat()
		}
		self.events.append(event)
		return event
	
	def getEvents(self, start_date=None, end_date=None):
		"""Get events in date range."""
		result = self.events
		if start_date:
			result = [e for e in result if e.get('start_time') >= start_date]
		if end_date:
			result = [e for e in result if e.get('start_time') <= end_date]
		return result
	
	def getEventsForDate(self, date):
		"""Get events for a specific date."""
		date_str = date if isinstance(date, str) else date.strftime('%Y-%m-%d')
		return [e for e in self.events if e.get('start_time', '').startswith(date_str)]
	
	def getEventsForWeek(self, week_start):
		"""Get events for a week."""
		# Simplified implementation
		return self.events
	
	def getEventsForMonth(self, year, month):
		"""Get events for a month."""
		month_str = f"{year}-{month:02d}"
		return [e for e in self.events if e.get('start_time', '').startswith(month_str)]
	
	def updateEvent(self, event_id, data):
		"""Update an event."""
		for e in self.events:
			if e['id'] == event_id:
				e.update(data)
				return e
		return None
	
	def deleteEvent(self, event_id):
		"""Delete an event."""
		self.events = [e for e in self.events if e['id'] != event_id
	
	def to_json(self):
		"""Export events as JSON."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.events, indent=2))
			return doc.to_string()
		return j.dumps(self.events, indent=2)
	
	def to_yaml(self):
		"""Export events as YAML."""
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(self.events))
			return doc.to_yaml_string()
		import yaml
		return yaml.dump(self.events)
	
	def summarize(self, format="text"):
		"""Get calendar summary."""
		summary = {
			'total_events': len(self.events),
			'events': self.events
		}
		
		if PYFFICE_AVAILABLE:
			doc = PyfficeScript(j.dumps(summary))
			return doc.to_summary(format=format)
		
		if format == "json":
			return j.dumps(summary, indent=2)
		elif format == "md":
			md = f"# Calendar Summary\n\n- Total Events: {len(self.events)}\n"
			return md
		return str(summary)