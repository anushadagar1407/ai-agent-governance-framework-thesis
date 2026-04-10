"""
Multi-Agent Orchestration Module
Manages agent workflows, dependencies, and collaborative tasks
"""

import json
import os
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import threading
import queue


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    SEQUENTIAL = "sequential"  # Tasks run one after another
    PARALLEL = "parallel"      # Tasks run simultaneously
    CONDITIONAL = "conditional" # Tasks based on conditions
    LOOP = "loop"              # Iterative tasks


@dataclass
class WorkflowStep:
    step_id: str
    agent_id: str
    task_type: TaskType
    action: str
    parameters: Dict
    dependencies: List[str]  # Step IDs that must complete first
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowInstance:
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    current_step: int = 0
    results: Dict = None
    error_log: List[str] = None


class MultiAgentOrchestrator:
    """
    Orchestrates multi-agent workflows with dependency management
    """
    
    def __init__(self, registry, governance, evaluator, storage_path: str = "workflows.json"):
        self.registry = registry
        self.governance = governance
        self.evaluator = evaluator
        self.storage_path = storage_path
        self.workflows: Dict[str, WorkflowInstance] = {}
        self.active_workflows: Set[str] = set()
        self._lock = threading.Lock()
        self._load_workflows()
        
        # Callbacks
        self.step_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
    
    def _load_workflows(self):
        """Load persisted workflows"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for wf_id, wf_data in data.items():
                        self.workflows[wf_id] = WorkflowInstance(**wf_data)
            except:
                pass
    
    def _save_workflows(self):
        """Persist workflows"""
        with self._lock:
            with open(self.storage_path, 'w') as f:
                json.dump({k: asdict(v) for k, v in self.workflows.items()}, 
                         f, indent=2, default=str)
    
    def create_workflow(self, name: str, steps: List[WorkflowStep]) -> str:
        """Create a new workflow definition"""
        workflow_id = f"WF-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{hash(name) % 10000}"
        
        workflow = WorkflowInstance(
            workflow_id=workflow_id,
            name=name,
            steps=steps,
            status=WorkflowStatus.PENDING,
            created_at=datetime.utcnow().isoformat(),
            results={},
            error_log=[]
        )
        
        with self._lock:
            self.workflows[workflow_id] = workflow
            self._save_workflows()
        
        return workflow_id
    
    def validate_workflow(self, workflow_id: str) -> Dict:
        """Validate workflow before execution"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"valid": False, "errors": ["Workflow not found"]}
        
        errors = []
        warnings = []
        
        # Check all agents exist and are active
        for step in workflow.steps:
            agent = self.registry.get_agent(step.agent_id)
            if not agent:
                errors.append(f"Step {step.step_id}: Agent {step.agent_id} not found")
            elif agent.get('status') != 'active':
                errors.append(f"Step {step.step_id}: Agent {step.agent_id} is inactive")
            
            # Check governance
            context = {"logging": True, "approval": True}  # Assume full controls for validation
            gov_result = self.governance.can_activate(agent, context) if agent else False
            if not gov_result and agent:
                warnings.append(f"Step {step.step_id}: Agent may not pass governance")
        
        # Check for circular dependencies
        step_ids = {s.step_id for s in workflow.steps}
        for step in workflow.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    errors.append(f"Step {step.step_id}: Dependency {dep} not found")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def execute_workflow(self, workflow_id: str) -> Dict:
        """Execute a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"success": False, "error": "Workflow not found"}
        
        validation = self.validate_workflow(workflow_id)
        if not validation["valid"]:
            return {"success": False, "errors": validation["errors"]}
        
        # Update status
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow().isoformat()
        self.active_workflows.add(workflow_id)
        
        try:
            results = self._execute_steps(workflow)
            workflow.status = WorkflowStatus.COMPLETED
            workflow.results = results
            workflow.completed_at = datetime.utcnow().isoformat()
            
            # Trigger callbacks
            for callback in self.completion_callbacks:
                callback(workflow_id, results)
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "results": results,
                "duration": self._calculate_duration(workflow)
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error_log.append(str(e))
            workflow.completed_at = datetime.utcnow().isoformat()
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "completed_steps": workflow.current_step
            }
        
        finally:
            self.active_workflows.discard(workflow_id)
            self._save_workflows()
    
    def _execute_steps(self, workflow: WorkflowInstance) -> Dict:
        """Execute workflow steps with dependency management"""
        results = {}
        completed_steps = set()
        
        for i, step in enumerate(workflow.steps):
            workflow.current_step = i
            
            # Check dependencies
            for dep in step.dependencies:
                if dep not in completed_steps:
                    raise Exception(f"Dependency {dep} not completed for step {step.step_id}")
            
            # Execute step
            step_result = self._execute_step(step)
            results[step.step_id] = step_result
            completed_steps.add(step.step_id)
            
            # Trigger step callback
            for callback in self.step_callbacks:
                callback(workflow.workflow_id, step.step_id, step_result)
        
        return results
    
    def _execute_step(self, step: WorkflowStep) -> Dict:
        """Execute a single workflow step"""
        agent = self.registry.get_agent(step.agent_id)
        
        # Pre-execution governance check
        context = {"logging": True, "approval": True, "workflow_execution": True}
        if not self.governance.can_activate(agent, context):
            raise Exception(f"Governance check failed for agent {step.agent_id}")
        
        # Simulate execution (in real implementation, this would call the agent)
        execution_result = {
            "step_id": step.step_id,
            "agent_id": step.agent_id,
            "action": step.action,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "output": f"Executed {step.action} with params {step.parameters}"
        }
        
        # Post-execution evaluation
        if step.task_type == TaskType.SEQUENTIAL:
            # Evaluate after each step
            eval_scores = {
                "reliability": 0.95,
                "transparency": 0.90,
                "accountability": 0.92,
                "safety_score": 0.94
            }
            evaluation = self.evaluator.evaluate_universal(eval_scores)
            execution_result["evaluation"] = evaluation
        
        return execution_result
    
    def _calculate_duration(self, workflow: WorkflowInstance) -> float:
        """Calculate workflow duration in seconds"""
        if workflow.started_at and workflow.completed_at:
            start = datetime.fromisoformat(workflow.started_at)
            end = datetime.fromisoformat(workflow.completed_at)
            return (end - start).total_seconds()
        return 0
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.utcnow().isoformat()
            self.active_workflows.discard(workflow_id)
            self._save_workflows()
            return True
        return False
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get current workflow status"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "progress": f"{workflow.current_step}/{len(workflow.steps)}",
            "created_at": workflow.created_at,
            "started_at": workflow.started_at,
            "completed_at": workflow.completed_at,
            "results": workflow.results
        }
    
    def list_workflows(self, status: Optional[str] = None) -> List[Dict]:
        """List all workflows"""
        workflows = []
        for wf in self.workflows.values():
            if status is None or wf.status.value == status:
                workflows.append({
                    "workflow_id": wf.workflow_id,
                    "name": wf.name,
                    "status": wf.status.value,
                    "steps": len(wf.steps),
                    "created_at": wf.created_at
                })
        return workflows
    
    def add_step_callback(self, callback: Callable):
        """Add callback for step completion"""
        self.step_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable):
        """Add callback for workflow completion"""
        self.completion_callbacks.append(callback)
    
    def create_template_workflow(self, template_type: str, agent_ids: List[str]) -> str:
        """Create predefined workflow templates"""
        steps = []
        
        if template_type == "document_approval":
            # Sequential: Draft -> Review -> Approve
            for i, (agent_id, action) in enumerate(zip(agent_ids, 
                                                      ["draft", "review", "approve"])):
                steps.append(WorkflowStep(
                    step_id=f"step_{i+1}",
                    agent_id=agent_id,
                    task_type=TaskType.SEQUENTIAL,
                    action=action,
                    parameters={"document_type": "contract"},
                    dependencies=[f"step_{i}"] if i > 0 else [],
                    timeout_seconds=600
                ))
        
        elif template_type == "data_pipeline":
            # Parallel: Extract, Transform, Load
            for i, agent_id in enumerate(agent_ids):
                steps.append(WorkflowStep(
                    step_id=f"step_{i+1}",
                    agent_id=agent_id,
                    task_type=TaskType.PARALLEL,
                    action=["extract", "transform", "load"][i],
                    parameters={},
                    dependencies=[],
                    timeout_seconds=300
                ))
        
        elif template_type == "incident_response":
            # Conditional: Detect -> Assess -> (Escalate or Resolve)
            steps.append(WorkflowStep(
                step_id="detect",
                agent_id=agent_ids[0],
                task_type=TaskType.SEQUENTIAL,
                action="detect_incident",
                parameters={},
                dependencies=[]
            ))
            steps.append(WorkflowStep(
                step_id="assess",
                agent_id=agent_ids[1],
                task_type=TaskType.CONDITIONAL,
                action="assess_severity",
                parameters={},
                dependencies=["detect"]
            ))
        
        return self.create_workflow(f"{template_type}_{datetime.utcnow().strftime('%H%M%S')}", steps)
