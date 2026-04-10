from typing import Dict, Optional
from datetime import datetime
from framework.metrics import MetricsCalculator
from framework.models import (
    UniversalMetrics, 
    WorkflowSpecificMetrics, 
    ComprehensiveEvaluation
)


class AgentEvaluator:
    WORKFLOW_THRESHOLDS = {
        "trading": {
            "execution_speed": 0.95,
            "slippage_control": 0.90,
            "compliance_adherence": 0.98,
            "risk_management": 0.95
        },
        "customer_service": {
            "resolution_rate": 0.85,
            "satisfaction_score": 0.80,
            "escalation_rate": 0.90,
            "response_time": 0.85
        },
        "hr": {
            "bias_mitigation": 0.90,
            "fairness_score": 0.85,
            "privacy_compliance": 0.95,
            "accuracy": 0.80
        },
        "default": {
            "accuracy": 0.80,
            "efficiency": 0.75,
            "quality": 0.80
        }
    }
    
    def __init__(self, calculator: Optional[MetricsCalculator] = None):
        self.calculator = calculator or MetricsCalculator()
    
    def evaluate_universal(self, scores: Dict[str, float]) -> Dict:
        """Evaluate universal metrics (Layer 1)"""
        try:
            metrics = UniversalMetrics(**scores)
        except Exception as e:
            raise ValueError(f"Invalid universal metrics: {e}")
        
        scores_dict = {
            "reliability": metrics.reliability,
            "transparency": metrics.transparency,
            "accountability": metrics.accountability,
            "safety_score": metrics.safety_score
        }
        
        return self.calculator.calculate_overall_score(scores_dict)
    
    def evaluate_workflow(
        self, 
        workflow_type: str, 
        scores: Dict[str, float]
    ) -> Dict:
        """Evaluate workflow-specific metrics (Layer 2)"""
        thresholds = self.WORKFLOW_THRESHOLDS.get(
            workflow_type.lower(), 
            self.WORKFLOW_THRESHOLDS["default"]
        )
        
        results = []
        total_score = 0
        all_passed = True
        
        for metric, value in scores.items():
            threshold = thresholds.get(metric, 0.75)
            passed = value >= threshold
            normalized = min(value / threshold, 1.0) if threshold > 0 else 0
            
            results.append({
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "passed": passed,
                "normalized_score": normalized
            })
            
            total_score += normalized
            if not passed:
                all_passed = False
        
        avg_score = total_score / len(scores) if scores else 0
        
        return {
            "workflow_type": workflow_type,
            "overall_score": round(avg_score, 3),
            "passed": all_passed,
            "details": results
        }
    
    def comprehensive_evaluation(
        self,
        agent: Dict,
        universal_scores: Dict[str, float],
        workflow_type: str,
        workflow_scores: Dict[str, float],
        evaluator_id: str = "system"
    ) -> ComprehensiveEvaluation:
        """Perform two-layer comprehensive evaluation"""
        universal_result = self.evaluate_universal(universal_scores)
        workflow_result = self.evaluate_workflow(workflow_type, workflow_scores)
        
        combined_score = (
            universal_result["overall_score"] * 0.6 + 
            workflow_result["overall_score"] * 0.4
        )
        
        status = "pass"
        if not universal_result["passed"] or not workflow_result["passed"]:
            status = "fail"
        elif combined_score < 0.85:
            status = "conditional"
        
        return ComprehensiveEvaluation(
            agent_id=agent.get("id"),
            agent_name=agent.get("name"),
            universal=UniversalMetrics(**universal_scores),
            workflow_specific=WorkflowSpecificMetrics(
                workflow_type=workflow_type,
                metrics=workflow_scores
            ),
            evaluator_id=evaluator_id,
            overall_score=round(combined_score, 3),
            status=status
        )


def evaluate_agent(agent: Dict, scores: Dict) -> Dict:
    """Backward compatibility function"""
    evaluator = AgentEvaluator()
    
    universal_scores = {
        "reliability": scores.get("reliability", 0.8),
        "transparency": scores.get("transparency", 0.8),
        "accountability": scores.get("accountability", 0.8),
        "safety_score": scores.get("safety_score", 0.8)
    }
    
    result = evaluator.evaluate_universal(universal_scores)
    
    return {
        "agent_id": agent.get("id"),
        "agent_name": agent.get("name"),
        "evaluation_type": "universal",
        "timestamp": datetime.utcnow().isoformat(),
        **result
    }
