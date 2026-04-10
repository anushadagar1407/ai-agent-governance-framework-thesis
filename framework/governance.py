from typing import Dict, List, Callable, Optional
from datetime import datetime
from enum import Enum
from framework.models import ComplianceStatus, GovernanceRuleResult, GovernanceEvaluation
from framework.audit_logger import AuditLogger


class GovernanceRule:
    def __init__(
        self, 
        rule_id: str, 
        description: str, 
        check_func: Callable[[Dict, Dict], bool],
        required: bool = True,
        risk_levels: Optional[List[str]] = None
    ):
        self.rule_id = rule_id
        self.description = description
        self.check_func = check_func
        self.required = required
        self.risk_levels = risk_levels or ["low", "medium", "high", "critical"]


class GovernanceEngine:
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.rules: List[GovernanceRule] = []
        self.audit_logger = audit_logger or AuditLogger()
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default governance rules for financial services"""
        self.rules = [
            GovernanceRule(
                "R001",
                "High-risk agents require human approval",
                lambda agent, ctx: not (
                    agent.get('risk_level') == 'high' and 
                    'approval' not in ctx
                ),
                required=True,
                risk_levels=["high", "critical"]
            ),
            GovernanceRule(
                "R002",
                "All agents must have logging enabled",
                lambda agent, ctx: 'logging' in ctx,
                required=True
            ),
            GovernanceRule(
                "R003",
                "Critical agents require dual authorization",
                lambda agent, ctx: not (
                    agent.get('risk_level') == 'critical' and 
                    ctx.get('authorization_count', 0) < 2
                ),
                required=True,
                risk_levels=["critical"]
            ),
            GovernanceRule(
                "R004",
                "Agents with trading purpose require compliance review",
                lambda agent, ctx: not (
                    'trading' in agent.get('purpose', '').lower() and 
                    'compliance_review' not in ctx
                ),
                required=True
            ),
            GovernanceRule(
                "R005",
                "Inactive agents cannot be approved",
                lambda agent, ctx: agent.get('status') != 'inactive',
                required=True
            ),
            GovernanceRule(
                "R006",
                "Agents must have valid version tag",
                lambda agent, ctx: 'version' in agent and agent['version'],
                required=False
            ),
            GovernanceRule(
                "R007",
                "High-risk agents require kill switch capability",
                lambda agent, ctx: not (
                    agent.get('risk_level') in ['high', 'critical'] and 
                    'kill_switch' not in ctx
                ),
                required=True,
                risk_levels=["high", "critical"]
            )
        ]
    
    def add_custom_rule(self, rule: GovernanceRule):
        self.rules.append(rule)
    
    def evaluate(self, agent: Dict, context: Dict) -> GovernanceEvaluation:
        """Evaluate agent against all governance rules"""
        results = []
        overall_status = ComplianceStatus.PASS
        
        for rule in self.rules:
            if agent.get('risk_level') not in rule.risk_levels:
                continue
                
            try:
                passed = rule.check_func(agent, context)
                status = ComplianceStatus.PASS if passed else (
                    ComplianceStatus.FAIL if rule.required else ComplianceStatus.CONDITIONAL
                )
                
                if not passed and rule.required:
                    overall_status = ComplianceStatus.FAIL
                
                results.append(GovernanceRuleResult(
                    rule_id=rule.rule_id,
                    description=rule.description,
                    status=status,
                    required=rule.required
                ))
            except Exception as e:
                results.append(GovernanceRuleResult(
                    rule_id=rule.rule_id,
                    description=rule.description,
                    status=ComplianceStatus.FAIL,
                    required=rule.required,
                    details=str(e)
                ))
                overall_status = ComplianceStatus.FAIL
        
        evaluation = GovernanceEvaluation(
            agent_id=agent.get("id"),
            overall_status=overall_status,
            rule_results=results,
            evaluator_version="1.0.0"
        )
        
        # Audit logging
        self.audit_logger.log_event(
            "governance_evaluation",
            agent.get("id"),
            {
                "overall_status": overall_status.value,
                "rules_checked": len(results),
                "failed_rules": [r.rule_id for r in results if r.status == ComplianceStatus.FAIL]
            }
        )
        
        # Add hash for immutability
        import hashlib
        import json
        
        eval_dict = evaluation.dict()
        eval_dict.pop("entry_hash", None)
        eval_dict.pop("previous_hash", None)
        
        last_log = self.audit_logger.logs[-2] if len(self.audit_logger.logs) > 1 else None
        previous_hash = last_log.get("entry_hash") if last_log else "0"
        
        evaluation.previous_hash = previous_hash
        evaluation.entry_hash = hashlib.sha256(
            json.dumps(eval_dict, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        return evaluation
    
    def can_activate(self, agent: Dict, context: Dict) -> bool:
        """Quick check if agent can be activated"""
        evaluation = self.evaluate(agent, context)
        return evaluation.overall_status == ComplianceStatus.PASS


def governance_check(agent: Dict, checks: List[str]) -> Dict:
    """Backward compatibility function"""
    context = {"checks": checks}
    for check in checks:
        context[check] = True
    
    engine = GovernanceEngine()
    result = engine.evaluate(agent, context)
    
    return {
        "agent_id": result.agent_id,
        "timestamp": result.timestamp.isoformat(),
        "status": result.overall_status.value,
        "checks_performed": len(result.rule_results),
        "passed": result.overall_status == ComplianceStatus.PASS,
        "details": [
            {
                "rule_id": r.rule_id,
                "description": r.description,
                "status": r.status.value,
                "required": r.required
            }
            for r in result.rule_results
        ]
    }
