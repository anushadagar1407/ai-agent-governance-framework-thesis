"""
Explainable AI Module for Governance Framework
Provides transparency into agent decisions and evaluations
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib


class ExplanationType(Enum):
    DECISION = "decision"
    EVALUATION = "evaluation"
    GOVERNANCE = "governance"
    RISK = "risk"
    ANOMALY = "anomaly"


@dataclass
class Explanation:
    explanation_id: str
    timestamp: str
    agent_id: str
    explanation_type: ExplanationType
    decision: str
    factors: List[Dict[str, Any]]
    confidence: float
    human_readable: str
    technical_details: Dict
    counterfactual: Optional[str] = None


class ExplainabilityEngine:
    """
    Generates human-readable explanations for AI agent decisions
    and governance evaluations
    """
    
    def __init__(self, storage_path: str = "explanations.json"):
        self.storage_path = storage_path
        self.explanations: List[Explanation] = []
        self._load_explanations()
    
    def _load_explanations(self):
        """Load historical explanations"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.explanations = [Explanation(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.explanations = []
    
    def _save_explanations(self):
        """Save explanations to file"""
        with open(self.storage_path, 'w') as f:
            json.dump([self._explanation_to_dict(e) for e in self.explanations], 
                     f, indent=2, default=str)
    
    def _explanation_to_dict(self, exp: Explanation) -> Dict:
        return {
            "explanation_id": exp.explanation_id,
            "timestamp": exp.timestamp,
            "agent_id": exp.agent_id,
            "explanation_type": exp.explanation_type.value,
            "decision": exp.decision,
            "factors": exp.factors,
            "confidence": exp.confidence,
            "human_readable": exp.human_readable,
            "technical_details": exp.technical_details,
            "counterfactual": exp.counterfactual
        }
    
    def explain_evaluation(self, agent: Dict, evaluation_result: Dict) -> Explanation:
        """Generate explanation for agent evaluation"""
        factors = []
        
        # Analyze each metric
        for detail in evaluation_result.get('details', []):
            factor = {
                "metric": detail['metric'],
                "value": detail['value'],
                "threshold": detail['threshold'],
                "impact": "positive" if detail['passed'] else "negative",
                "weight": detail.get('weight', 0.1),
                "explanation": self._explain_metric(detail)
            }
            factors.append(factor)
        
        # Sort by impact
        factors.sort(key=lambda x: x['weight'], reverse=True)
        
        # Generate human-readable summary
        passed = evaluation_result.get('passed', False)
        score = evaluation_result.get('overall_score', 0)
        grade = evaluation_result.get('grade', 'F')
        
        human_readable = self._generate_evaluation_summary(
            agent, passed, score, grade, factors
        )
        
        explanation = Explanation(
            explanation_id=self._generate_id(),
            timestamp=datetime.utcnow().isoformat(),
            agent_id=agent.get('id', 'unknown'),
            explanation_type=ExplanationType.EVALUATION,
            decision="PASS" if passed else "FAIL",
            factors=factors,
            confidence=score,
            human_readable=human_readable,
            technical_details=evaluation_result,
            counterfactual=self._generate_counterfactual(factors, evaluation_result)
        )
        
        self.explanations.append(explanation)
        self._save_explanations()
        return explanation
    
    def explain_governance_decision(self, agent: Dict, 
                                    governance_result: Dict) -> Explanation:
        """Generate explanation for governance decision"""
        factors = []
        
        for rule in governance_result.get('details', []):
            factor = {
                "rule_id": rule['rule_id'],
                "description": rule['description'],
                "status": rule['status'],
                "required": rule['required'],
                "impact": "critical" if rule['required'] and rule['status'] == 'fail' else "minor"
            }
            factors.append(factor)
        
        passed = governance_result.get('passed', False)
        
        human_readable = self._generate_governance_summary(
            agent, passed, factors
        )
        
        explanation = Explanation(
            explanation_id=self._generate_id(),
            timestamp=datetime.utcnow().isoformat(),
            agent_id=agent.get('id', 'unknown'),
            explanation_type=ExplanationType.GOVERNANCE,
            decision="APPROVED" if passed else "REJECTED",
            factors=factors,
            confidence=1.0 if passed else 0.0,
            human_readable=human_readable,
            technical_details=governance_result,
            counterfactual=self._generate_governance_counterfactual(factors)
        )
        
        self.explanations.append(explanation)
        self._save_explanations()
        return explanation
    
    def explain_risk_score(self, agent: Dict, risk_trend: Any) -> Explanation:
        """Generate explanation for risk scoring"""
        factors = [
            {
                "factor": "base_risk_level",
                "value": agent.get('risk_level', 'medium'),
                "impact": "high",
                "explanation": f"Agent classified as {agent.get('risk_level')} risk"
            },
            {
                "factor": "autonomy_level",
                "value": agent.get('agent_type', 'unknown'),
                "impact": "medium",
                "explanation": f"Agent type: {agent.get('agent_type')}"
            },
            {
                "factor": "tool_access",
                "value": len(agent.get('tools', [])),
                "impact": "medium",
                "explanation": f"Access to {len(agent.get('tools', []))} tools"
            }
        ]
        
        if hasattr(risk_trend, 'trend_direction'):
            factors.append({
                "factor": "trend",
                "value": risk_trend.trend_direction,
                "impact": "high" if risk_trend.trend_direction == "increasing" else "low",
                "explanation": f"Risk trend is {risk_trend.trend_direction}"
            })
        
        human_readable = self._generate_risk_summary(agent, risk_trend, factors)
        
        explanation = Explanation(
            explanation_id=self._generate_id(),
            timestamp=datetime.utcnow().isoformat(),
            agent_id=agent.get('id', 'unknown'),
            explanation_type=ExplanationType.RISK,
            decision=f"RISK_SCORE_{int(risk_trend.risk_score * 100) if hasattr(risk_trend, 'risk_score') else 50}",
            factors=factors,
            confidence=1 - (risk_trend.risk_score if hasattr(risk_trend, 'risk_score') else 0.5),
            human_readable=human_readable,
            technical_details={"risk_trend": risk_trend.__dict__ if hasattr(risk_trend, '__dict__') else {}}
        )
        
        self.explanations.append(explanation)
        self._save_explanations()
        return explanation
    
    def _explain_metric(self, detail: Dict) -> str:
        """Generate explanation for a single metric"""
        metric = detail['metric']
        value = detail['value']
        threshold = detail['threshold']
        passed = detail['passed']
        
        explanations = {
            "reliability": f"System uptime and consistency at {value:.1%}",
            "transparency": f"Decision explainability at {value:.1%}",
            "accountability": f"Audit trail completeness at {value:.1%}",
            "safety_score": f"Safety guardrails effectiveness at {value:.1%}",
            "execution_speed": f"Trade execution latency performance at {value:.1%}",
            "compliance_adherence": f"Regulatory compliance at {value:.1%}",
            "risk_management": f"Risk control adherence at {value:.1%}"
        }
        
        base = explanations.get(metric, f"{metric} at {value:.1%}")
        
        if passed:
            return f"{base} (exceeds threshold of {threshold:.1%})"
        else:
            gap = threshold - value
            return f"{base} (below threshold by {gap:.1%} - needs improvement)"
    
    def _generate_evaluation_summary(self, agent: Dict, passed: bool, 
                                      score: float, grade: str,
                                      factors: List[Dict]) -> str:
        """Generate human-readable evaluation summary"""
        status = "PASSED" if passed else "FAILED"
        
        summary = f"""
EVALUATION REPORT FOR {agent.get('name', 'Unknown Agent')} ({agent.get('id')})
Status: {status} | Score: {score:.1%} | Grade: {grade}

SUMMARY:
The agent has {'met' if passed else 'not met'} the required performance standards.
"""
        
        # Top contributing factors
        summary += "\nKEY FACTORS:\n"
        for i, factor in enumerate(factors[:3], 1):
            emoji = "✅" if factor['impact'] == "positive" else "❌"
            summary += f"{i}. {emoji} {factor['explanation']}\n"
        
        if not passed:
            summary += "\nAREAS FOR IMPROVEMENT:\n"
            failed = [f for f in factors if f['impact'] == "negative"]
            for factor in failed[:3]:
                summary += f"- {factor['metric']}: {factor['explanation']}\n"
        
        return summary
    
    def _generate_governance_summary(self, agent: Dict, passed: bool,
                                      factors: List[Dict]) -> str:
        """Generate human-readable governance summary"""
        status = "APPROVED" if passed else "REJECTED"
        
        summary = f"""
GOVERNANCE DECISION FOR {agent.get('name', 'Unknown Agent')} ({agent.get('id')})
Decision: {status}

COMPLIANCE CHECK RESULTS:
"""
        
        required_passed = sum(1 for f in factors if f['required'] and f['status'] == 'pass')
        required_total = sum(1 for f in factors if f['required'])
        
        summary += f"Required Rules: {required_passed}/{required_total} passed\n"
        
        for factor in factors:
            emoji = "✅" if factor['status'] == 'pass' else "❌"
            req = "[REQUIRED]" if factor['required'] else "[optional]"
            summary += f"{emoji} {factor['rule_id']}: {factor['description']} {req}\n"
        
        if not passed:
            summary += "\nBLOCKING ISSUES:\n"
            blocking = [f for f in factors if f['required'] and f['status'] == 'fail']
            for issue in blocking:
                summary += f"- {issue['description']}\n"
        
        return summary
    
    def _generate_risk_summary(self, agent: Dict, risk_trend: Any, 
                               factors: List[Dict]) -> str:
        """Generate human-readable risk summary"""
        risk_score = getattr(risk_trend, 'risk_score', 0.5)
        trend = getattr(risk_trend, 'trend_direction', 'unknown')
        
        risk_category = "LOW" if risk_score < 0.3 else \
                       "MEDIUM" if risk_score < 0.6 else \
                       "HIGH" if risk_score < 0.8 else "CRITICAL"
        
        summary = f"""
RISK ASSESSMENT FOR {agent.get('name', 'Unknown Agent')} ({agent.get('id')})
Risk Score: {risk_score:.1%} ({risk_category})
Trend: {trend.upper()}

RISK FACTORS:
"""
        for factor in factors:
            emoji = "🔴" if factor['impact'] == "high" else \
                   "🟡" if factor['impact'] == "medium" else "🟢"
            summary += f"{emoji} {factor['factor']}: {factor['explanation']}\n"
        
        if hasattr(risk_trend, 'alerts') and risk_trend.alerts:
            summary += "\nACTIVE ALERTS:\n"
            for alert in risk_trend.alerts:
                summary += f"⚠️  {alert}\n"
        
        return summary
    
    def _generate_counterfactual(self, factors: List[Dict], 
                                  result: Dict) -> str:
        """Generate counterfactual explanation"""
        failed = [f for f in factors if f['impact'] == "negative"]
        
        if not failed:
            return "Agent would fail if: reliability drops below 85%, or safety score below 90%"
        
        counterfactuals = []
        for factor in failed:
            needed = factor['threshold'] - factor['value']
            counterfactuals.append(
                f"If {factor['metric']} were {needed:.1%} higher, "
                f"the agent would pass evaluation"
            )
        
        return " | ".join(counterfactuals) if counterfactuals else "N/A"
    
    def _generate_governance_counterfactual(self, 
                                             factors: List[Dict]) -> str:
        """Generate counterfactual for governance"""
        failed_required = [f for f in factors 
                          if f['required'] and f['status'] == 'fail']
        
        if not failed_required:
            return "Agent would be rejected if: logging disabled, or approval removed"
        
        fixes = [f"enable {f['rule_id'].lower().replace('_', ' ')}" 
                for f in failed_required]
        
        return f"If the agent had: {', '.join(fixes)}, it would be approved"
    
    def _generate_id(self) -> str:
        """Generate unique explanation ID"""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"exp-{timestamp}"
        return f"EXP-{hashlib.md5(hash_input.encode()).hexdigest()[:12].upper()}"
    
    def get_explanations_for_agent(self, agent_id: str) -> List[Explanation]:
        """Get all explanations for a specific agent"""
        return [e for e in self.explanations if e.agent_id == agent_id]
    
    def generate_explanation_report(self, agent_id: str) -> str:
        """Generate comprehensive explanation report"""
        explanations = self.get_explanations_for_agent(agent_id)
        
        if not explanations:
            return f"No explanations found for agent {agent_id}"
        
        report = f"""
EXPLAINABILITY REPORT FOR AGENT {agent_id}
Generated: {datetime.utcnow().isoformat()}
Total Explanations: {len(explanations)}

EXPLANATION HISTORY:
"""
        for exp in explanations[-5:]:  # Last 5
            report += f"""
---
Type: {exp.explanation_type.value}
Time: {exp.timestamp}
Decision: {exp.decision}
Confidence: {exp.confidence:.1%}

{exp.human_readable}
"""
        
        return report
