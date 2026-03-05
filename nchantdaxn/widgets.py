# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid: 
	name: AXN and ProjectAXN Widgets
	description: >
		Custom widgets for displaying and interacting with AXN tasks and projects.
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
pxcfg = join(here, '_data_', 'widgets.yaml')


class NchantdAXNTaskWidget:
	"""
	Widget for displaying an AXN task with progress, status, and actions.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNTaskWidget')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		self.task_data = None
		self.task_id = None
		self.name = ""
		self.status = "pending"
		self.priority = 2
		self.progress = 0.0
		self.assignee = ""
		self.due_date = None
		self.tags = []
	
	def setTask(self, task_data):
		"""Set the task data to display."""
		self.task_data = task_data
		if task_data:
			self.task_id = task_data.get('id')
			self.name = task_data.get('name', '')
			self.status = task_data.get('status', 'pending')
			self.priority = task_data.get('priority', 2)
			self.progress = task_data.get('progress', 0.0)
			self.assignee = task_data.get('assignee', '')
			self.tags = task_data.get('tags', [])
			
			end = task_data.get('end_date')
			if end:
				self.due_date = dt.datetime.fromisoformat(end) if isinstance(end, str) else end
	
	def getPriorityIcon(self):
		"""Get icon name for priority level."""
		icons = {
			1: 'priority-low',
			2: 'priority-medium',
			3: 'priority-high',
			4: 'priority-critical',
		}
		return icons.get(self.priority, 'priority-medium')
	
	def getStatusIcon(self):
		"""Get icon name for status."""
		icons = {
			'pending': 'circle-outline',
			'in_progress': 'play',
			'completed': 'check-circle',
			'blocked': 'alert',
			'cancelled': 'close-circle',
		}
		return icons.get(self.status, 'circle-outline')
	
	def getProgressColor(self):
		"""Get color for progress bar."""
		if self.progress >= 100:
			return 'green'
		elif self.progress >= 75:
			return 'light-green'
		elif self.progress >= 50:
			return 'yellow'
		elif self.progress >= 25:
			return 'orange'
		else:
			return 'red'
	
	def isOverdue(self):
		"""Check if task is overdue."""
		if self.due_date and self.status not in ['completed', 'cancelled']:
			return dt.datetime.now() > self.due_date
		return False
	
	def render(self):
		"""Render the widget (placeholder for actual GUI rendering)."""
		return {
			'id': self.task_id,
			'name': self.name,
			'status': self.status,
			'status_icon': self.getStatusIcon(),
			'priority': self.priority,
			'priority_icon': self.getPriorityIcon(),
			'progress': self.progress,
			'progress_color': self.getProgressColor(),
			'assignee': self.assignee,
			'due_date': self.due_date,
			'tags': self.tags,
			'is_overdue': self.isOverdue(),
		}


class NchantdAXNProjectWidget:
	"""
	Widget for displaying a ProjectAXN project with tasks and milestones.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNProjectWidget')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		self.project_data = None
		self.project_id = None
		self.name = ""
		self.description = ""
		self.status = "planning"
		self.progress = 0.0
		self.start_date = None
		self.end_date = None
		self.task_count = 0
		self.completed_count = 0
		self.milestone_count = 0
	
	def setProject(self, project_data):
		"""Set the project data to display."""
		self.project_data = project_data
		if project_data:
			self.project_id = project_data.get('id')
			self.name = project_data.get('name', '')
			self.description = project_data.get('description', '')
			self.status = project_data.get('status', 'planning')
			self.progress = project_data.get('overall_progress', 0.0)
			
			start = project_data.get('start_date')
			if start:
				self.start_date = dt.datetime.fromisoformat(start) if isinstance(start, str) else start
			
			end = project_data.get('end_date')
			if end:
				self.end_date = dt.datetime.fromisoformat(end) if isinstance(end, str) else end
			
			tasks = project_data.get('tasks', {})
			self.task_count = len(tasks)
			self.completed_count = sum(1 for t in tasks.values() if t.get('status') == 'completed')
			self.milestone_count = len(project_data.get('milestones', {}))
	
	def getStatusColor(self):
		"""Get color for project status."""
		colors = {
			'planning': 'blue',
			'active': 'green',
			'on_hold': 'orange',
			'completed': 'dark-green',
			'cancelled': 'red',
		}
		return colors.get(self.status, 'blue')
	
	def render(self):
		"""Render the widget."""
		return {
			'id': self.project_id,
			'name': self.name,
			'description': self.description,
			'status': self.status,
			'status_color': self.getStatusColor(),
			'progress': self.progress,
			'start_date': self.start_date,
			'end_date': self.end_date,
			'task_count': self.task_count,
			'completed_count': self.completed_count,
			'milestone_count': self.milestone_count,
		}


class NchantdAXNTaskListWidget:
	"""
	Widget for displaying a list of AXN tasks with filtering and sorting.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNTaskListWidget')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		self.tasks = []
		self.filter_status = None
		self.filter_priority = None
		self.filter_assignee = None
		self.sort_by = 'priority'
		self.sort_desc = True
	
	def setTasks(self, tasks):
		"""Set the tasks to display."""
		self.tasks = tasks
	
	def filter(self, status=None, priority=None, assignee=None):
		"""Apply filters to task list."""
		self.filter_status = status
		self.filter_priority = priority
		self.filter_assignee = assignee
		return self.getFilteredTasks()
	
	def getFilteredTasks(self):
		"""Get tasks matching current filters."""
		result = self.tasks
		
		if self.filter_status:
			result = [t for t in result if t.get('status') == self.filter_status]
		
		if self.filter_priority:
			result = [t for t in result if t.get('priority') == self.filter_priority]
		
		if self.filter_assignee:
			result = [t for t in result if t.get('assignee') == self.filter_assignee]
		
		return result
	
	def sort(self, by='priority', descending=True):
		"""Sort the task list."""
		self.sort_by = by
		self.sort_desc = descending
		return self.getSortedTasks()
	
	def getSortedTasks(self):
		"""Get sorted tasks."""
		if not self.tasks:
			return []
		
		reverse = self.sort_desc
		if self.sort_by == 'priority':
			return sorted(self.tasks, key=lambda t: t.get('priority', 0), reverse=reverse)
		elif self.sort_by == 'status':
			return sorted(self.tasks, key=lambda t: t.get('status', ''), reverse=reverse)
		elif self.sort_by == 'due_date':
			return sorted(
				self.tasks,
				key=lambda t: t.get('end_date', ''),
				reverse=reverse
			)
		elif self.sort_by == 'name':
			return sorted(self.tasks, key=lambda t: t.get('name', '').lower(), reverse=reverse)
		
		return self.tasks


class NchantdAXNProjectListWidget:
	"""
	Widget for displaying a list of ProjectAXN projects.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNProjectListWidget')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		self.projects = []
		self.filter_status = None
	
	def setProjects(self, projects):
		"""Set the projects to display."""
		self.projects = projects
	
	def filter(self, status=None):
		"""Filter projects by status."""
		self.filter_status = status
		if status:
			return [p for p in self.projects if p.get('status') == status]
		return self.projects
	
	def getActiveProjects(self):
		"""Get active projects."""
		return [p for p in self.projects if p.get('status') == 'active']
	
	def getPlanningProjects(self):
		"""Get planning projects."""
		return [p for p in self.projects if p.get('status') == 'planning']


class NchantdAXNGanttWidget:
	"""
	Widget for displaying tasks in a Gantt chart view.
	"""
	
	def __init__(self, parent=None, cfg={}):
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdAXNGanttWidget')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		
		self.tasks = []
		self.show_milestones = True
		self.show_dependencies = True
		self.start_date = None
		self.end_date = None
	
	def setTasks(self, tasks):
		"""Set tasks to display in Gantt."""
		self.tasks = tasks
		self.calculateDateRange()
	
	def calculateDateRange(self):
		"""Calculate the date range for the Gantt view."""
		dates = []
		for task in self.tasks:
			start = task.get('start_date')
			if start:
				if isinstance(start, str):
					start = dt.datetime.fromisoformat(start)
				dates.append(start)
			
			end = task.get('end_date')
			if end:
				if isinstance(end, str):
					end = dt.datetime.fromisoformat(end)
				dates.append(end)
		
		if dates:
			self.start_date = min(dates)
			self.end_date = max(dates)
	
	def getTaskBar(self, task):
		"""Get Gantt bar data for a task."""
		start = task.get('start_date')
		end = task.get('end_date')
		
		if isinstance(start, str):
			start = dt.datetime.fromisoformat(start)
		if isinstance(end, str):
			end = dt.datetime.fromisoformat(end)
		
		# Calculate position and width relative to date range
		if self.start_date and self.end_date:
			total_days = (self.end_date - self.start_date).days or 1
			
			if start:
				start_offset = (start - self.start_date).days
			else:
				start_offset = 0
			
			if start and end:
				duration = (end - start).days + 1
			else:
				duration = 1
		else:
			start_offset = 0
			duration = 1
			total_days = 1
		
		return {
			'id': task.get('id'),
			'name': task.get('name', ''),
			'start_offset': start_offset,
			'duration': duration,
			'progress': task.get('progress', 0),
			'status': task.get('status', 'pending'),
		}
	
	def render(self):
		"""Render the Gantt chart data."""
		return {
			'tasks': [self.getTaskBar(t) for t in self.tasks],
			'start_date': self.start_date,
			'end_date': self.end_date,
			'show_milestones': self.show_milestones,
			'show_dependencies': self.show_dependencies,
		}
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
