# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid: 
	name: NchantdAXN Resources
	description: Resource definitions for NchantdAXN application.
	authority: document|this
	security: sec|lvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
from os.path import join, dirname

# ===============================================================================||
here = join(dirname(__file__), '')

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
# Application Resources
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

NchantdAXNResources = {
	'name': 'NchantdAXN',
	'version': '0.1.0',
	'description': 'AXN Task and ProjectAXN Project Management',
	'author': 'Arthr',
	'icon': 'axn-icon',
	'theme': 'default',
}

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
# Menu Definitions
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

NchantdAXNMenuBar = [
	{
		'label': 'File',
		'items': [
			{'label': 'New Task', 'shortcut': 'Ctrl+N', 'action': 'new_task'},
			{'label': 'New Project', 'shortcut': 'Ctrl+Shift+N', 'action': 'new_project'},
			{'type': 'separator'},
			{'label': 'Import...', 'action': 'import'},
			{'label': 'Export...', 'action': 'export'},
			{'type': 'separator'},
			{'label': 'Exit', 'shortcut': 'Ctrl+Q', 'action': 'exit'},
		]
	},
	{
		'label': 'Edit',
		'items': [
			{'label': 'Edit Task', 'action': 'edit_task'},
			{'label': 'Delete Task', 'action': 'delete_task'},
			{'type': 'separator'},
			{'label': 'Link to Project', 'action': 'link_task'},
			{'label': 'Update Progress', 'action': 'update_progress'},
		]
	},
	{
		'label': 'View',
		'items': [
			{'label': 'Task List', 'action': 'view_tasks'},
			{'label': 'Project List', 'action': 'view_projects'},
			{'label': 'Gantt Chart', 'action': 'view_gantt'},
			{'type': 'separator'},
			{'label': 'Refresh', 'shortcut': 'F5', 'action': 'refresh'},
		]
	},
	{
		'label': 'Help',
		'items': [
			{'label': 'About', 'action': 'about'},
		]
	},
]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
# Toolbar Definitions
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

NchantdAXNToolbar = [
	{'icon': 'document-new', 'tooltip': 'New Task', 'action': 'new_task'},
	{'icon': 'folder-new', 'tooltip': 'New Project', 'action': 'new_project'},
	{'type': 'separator'},
	{'icon': 'import', 'tooltip': 'Import', 'action': 'import'},
	{'icon': 'export', 'tooltip': 'Export', 'action': 'export'},
	{'type': 'separator'},
	{'icon': 'view-list', 'tooltip': 'Task List', 'action': 'view_tasks'},
	{'icon': 'view-grid', 'tooltip': 'Project List', 'action': 'view_projects'},
	{'icon': 'view-gantt', 'tooltip': 'Gantt View', 'action': 'view_gantt'},
	{'type': 'separator'},
	{'icon': 'refresh', 'tooltip': 'Refresh', 'action': 'refresh'},
]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
# Status Icons
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

NchantdAXNStatusIcons = {
	'pending': 'circle-outline',
	'in_progress': 'play',
	'completed': 'check-circle',
	'blocked': 'alert',
	'cancelled': 'close-circle',
}

NchantdAXNPriorityIcons = {
	1: 'priority-low',
	2: 'priority-medium',
	3: 'priority-high',
	4: 'priority-critical',
}

NchantdAXNProjectStatusColors = {
	'planning': '#3498db',
	'active': '#27ae60',
	'on_hold': '#f39c12',
	'completed': '#16a085',
	'cancelled': '#e74c3c',
}

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
# Column Definitions
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

NchantdAXNTaskColumns = [
	{'id': 'status', 'label': '', 'width': 30},
	{'id': 'name', 'label': 'Task', 'width': 250},
	{'id': 'priority', 'label': 'P', 'width': 30},
	{'id': 'progress', 'label': '%', 'width': 50},
	{'id': 'assignee', 'label': 'Assignee', 'width': 100},
	{'id': 'due_date', 'label': 'Due', 'width': 80},
	{'id': 'status_label', 'label': 'Status', 'width': 80},
]

NchantdAXNProjectColumns = [
	{'id': 'name', 'label': 'Project', 'width': 200},
	{'id': 'status', 'label': 'Status', 'width': 80},
	{'id': 'progress', 'label': 'Progress', 'width': 80},
	{'id': 'tasks', 'label': 'Tasks', 'width': 50},
	{'id': 'milestones', 'label': 'Milestones', 'width': 80},
	{'id': 'end_date', 'label': 'End Date', 'width': 80},
]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
