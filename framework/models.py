from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Literal
from enum import Enum
from datetime import datetime


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentType(str, Enum):
    TOOL = "tool"
    SEMI_AUTONOMOUS = "semi-autonomous"
    AUTONOMOUS = "autonomous"


class AgentRegistration(BaseModel):
    agent_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    agent_type: AgentType
    purpose: str
    tools: List[str]
    risk_level: RiskLevel
    
    @validator('tools')
    def validate_tools(cls, v):
        if not v:
            raise ValueError('At least one tool must be authorized')
        return v


class UniversalMetrics(BaseModel):
    reliability: float = Field(..., ge=0, le=1)
    transparency: float = Field(..., ge=0, le=1)
    accountability: float = Field(..., ge=0, le=1)
    safety_score: float = Field(..., ge=0, le=1)


class WorkflowSpecificMetrics(BaseModel):
    workflow_type: str
    metrics: Dict[str, float]


class ComprehensiveEvaluation(BaseModel):
    agent_id: str
    agent_name: str
    universal: UniversalMetrics
    workflow_specific: WorkflowSpecificMetrics
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    evaluator_id: str = "system"
    overall_score: Optional[float] = None
    status: Literal["pass", "fail", "conditional"] = "pass"


class ComplianceStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    PENDING_REVIEW = "pending_review"


class GovernanceRuleResult(BaseModel):
    rule_id: str
    description: str
    status: ComplianceStatus
    required: bool
    details: Optional[str] = None


class GovernanceEvaluation(BaseModel):
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_status: ComplianceStatus
    rule_results: List[GovernanceRuleResult]
    evaluator_version: str = "1.0.0"
    entry_hash: Optional[str] = None
    previous_hash: Optional[str] = None
