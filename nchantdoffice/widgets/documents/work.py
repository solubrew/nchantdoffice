"""PyfficeWork document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficeWork as BasePyfficeWork
from nchantrs.logging import logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficeWork(NchantdOfficeDocument, BasePyfficeWork):
    """Work document - implements PyfficeWork.
    
    Provides work/project management with task tracking,
    milestones, and collaboration features.
    """
    
    PYTYPE = 'work'
    DEFAULT_TOOLS = [
        {'id': 'add_task', 'icon': 'plus', 'label': 'Add Task', 'method': 'add_task'},
        {'id': 'remove_task', 'icon': 'minus', 'label': 'Remove Task', 'method': 'remove_task'},
        {'id': 'edit_task', 'icon': 'edit', 'label': 'Edit Task', 'method': 'edit_task'},
        {'id': 'add_milestone', 'icon': 'flag', 'label': 'Add Milestone', 'method': 'add_milestone'},
        {'id': 'set_status', 'icon': 'check-circle', 'label': 'Set Status', 'method': 'set_status'},
        {'id': 'assign', 'icon': 'user', 'label': 'Assign', 'method': 'assign_task'},
        {'id': 'set_priority', 'icon': 'arrow-up', 'label': 'Priority', 'method': 'set_priority'},
        {'id': 'add_comment', 'icon': 'comment', 'label': 'Comment', 'method': 'add_comment'},
        {'id': 'export_gantt', 'icon': 'chart-gantt', 'label': 'Export Gantt', 'method': 'export_gantt'},
        {'id': 'timeline', 'icon': 'clock', 'label': 'Timeline', 'method': 'show_timeline'},
    ]
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for work document."""
        return cls.DEFAULT_TOOLS
    
    def add_task(self, title: str, description: str = "") -> Optional[str]:
        """Add a new task to the work."""
        try:
            task_id = f"task_{len(self._tasks)}"
            self._tasks[task_id] = {
                'title': title,
                'description': description,
                'status': 'pending',
                'priority': 'medium',
                'assignee': None,
                'milestone': None,
            }
            return task_id
        except Exception as e:
            logma.error(f"Failed to add task: {e}")
            return None
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the work."""
        try:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to remove task: {e}")
            return False
    
    def edit_task(self, task_id: str, **kwargs) -> bool:
        """Edit a task's properties."""
        try:
            if task_id in self._tasks:
                self._tasks[task_id].update(kwargs)
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to edit task: {e}")
            return False
    
    def add_milestone(self, name: str, date: str) -> Optional[str]:
        """Add a milestone to the work."""
        try:
            milestone_id = f"milestone_{len(self._milestones)}"
            self._milestones[milestone_id] = {
                'name': name,
                'date': date,
                'tasks': [],
            }
            return milestone_id
        except Exception as e:
            logma.error(f"Failed to add milestone: {e}")
            return None
    
    def set_status(self, task_id: str, status: str) -> bool:
        """Set task status (pending, in_progress, completed)."""
        valid_statuses = ['pending', 'in_progress', 'completed', 'blocked']
        if status not in valid_statuses:
            return False
        return self.edit_task(task_id, status=status)
    
    def assign_task(self, task_id: str, assignee: str) -> bool:
        """Assign a task to a user."""
        return self.edit_task(task_id, assignee=assignee)
    
    def set_priority(self, task_id: str, priority: str) -> bool:
        """Set task priority (low, medium, high, critical)."""
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if priority not in valid_priorities:
            return False
        return self.edit_task(task_id, priority=priority)
    
    def add_comment(self, task_id: str, comment: str, author: str) -> bool:
        """Add a comment to a task."""
        try:
            if task_id not in self._tasks:
                return False
            if 'comments' not in self._tasks[task_id]:
                self._tasks[task_id]['comments'] = []
            self._tasks[task_id]['comments'].append({
                'author': author,
                'text': comment,
                'timestamp': self._get_timestamp(),
            })
            return True
        except Exception as e:
            logma.error(f"Failed to add comment: {e}")
            return False
    
    def export_gantt(self, filepath: str) -> bool:
        """Export work data as Gantt chart."""
        try:
            import json
            data = {
                'tasks': self._tasks,
                'milestones': self._milestones,
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logma.error(f"Failed to export Gantt: {e}")
            return False
    
    def show_timeline(self) -> bool:
        """Show work timeline view."""
        logma.info("Showing timeline view")
        return True
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
