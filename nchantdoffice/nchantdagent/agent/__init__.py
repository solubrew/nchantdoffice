# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name: NchantdAgent Brain
    description: >
        Agent brain components for automation and decision making
    version: 0.3.0
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

# ======================================3rd Party Library Modules=====================================================||

# ====================================================================================================================||


class AgentBrain:
    """
    Core agent brain for NchantdAgent.
    Handles reasoning, decision making, and task orchestration.
    """
    
    def __init__(self, name: str = "agent"):
        self.name = name
        self.state: Dict[str, Any] = {}
        self.context: List[Dict] = []
        self.capabilities: List[str] = []
        
    def add_capability(self, capability: str):
        """Add a capability to the agent"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            
    def remove_capability(self, capability: str):
        """Remove a capability"""
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            
    def has_capability(self, capability: str) -> bool:
        """Check if agent has a capability"""
        return capability in self.capabilities
    
    def add_context(self, context: Dict):
        """Add context to the agent's memory"""
        self.context.append({
            **context,
            "timestamp": datetime.now().isoformat()
        })
        
    def clear_context(self):
        """Clear context memory"""
        self.context.clear()
        
    def get_recent_context(self, n: int = 10) -> List[Dict]:
        """Get recent context items"""
        return self.context[-n:]
    
    def think(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Process a thought/prompt.
        
        Args:
            prompt: Input prompt
            context: Additional context
            
        Returns:
            Agent response
        """
        # Add to context
        self.add_context({
            "role": "user",
            "content": prompt,
            "context": context or {}
        })
        
        # For now, return a placeholder
        # Full implementation would use LLM or rule-based reasoning
        response = f"Agent thought: {prompt}"
        
        self.add_context({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def execute_task(self, task: Dict) -> Dict:
        """
        Execute a task.
        
        Args:
            task: Task specification
            
        Returns:
            Task result
        """
        task_type = task.get("type")
        task_data = task.get("data", {})
        
        result = {
            "task": task_type,
            "success": False,
            "result": None,
            "error": None
        }
        
        # Task execution logic
        if task_type == "query":
            result["result"] = self._execute_query(task_data)
            result["success"] = True
        elif task_type == "store":
            result["result"] = self._execute_store(task_data)
            result["success"] = True
        elif task_type == "analyze":
            result["result"] = self._execute_analyze(task_data)
            result["success"] = True
        else:
            result["error"] = f"Unknown task type: {task_type}"
            
        return result
    
    def _execute_query(self, data: Dict) -> Any:
        """Execute a query task"""
        # Placeholder - would query storage
        return {"query": data.get("query"), "results": []}
    
    def _execute_store(self, data: Dict) -> Any:
        """Execute a store task"""
        # Placeholder - would store data
        return {"stored": True, "key": data.get("key")}
    
    def _execute_analyze(self, data: Dict) -> Any:
        """Execute an analysis task"""
        # Placeholder - would analyze data
        return {"analysis": "completed"}
    
    def get_state(self) -> Dict:
        """Get agent state"""
        return {
            "name": self.name,
            "capabilities": self.capabilities,
            "context_length": len(self.context),
            "state": self.state
        }
    
    def set_state(self, key: str, value: Any):
        """Set agent state"""
        self.state[key] = value
        
    def get_state_value(self, key: str, default: Any = None) -> Any:
        """Get agent state value"""
        return self.state.get(key, default)


class AgentTask:
    """Task representation for agent execution"""
    
    def __init__(self, task_id: str, task_type: str, data: Dict):
        self.task_id = task_id
        self.task_type = task_type
        self.data = data
        self.status = "pending"
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.completed_at = None
        
    def mark_started(self):
        """Mark task as started"""
        self.status = "running"
        
    def mark_completed(self, result: Any):
        """Mark task as completed"""
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.now()
        
    def mark_failed(self, error: str):
        """Mark task as failed"""
        self.status = "failed"
        self.error = error
        self.completed_at = datetime.now()
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


# ====================================================================================================================||
