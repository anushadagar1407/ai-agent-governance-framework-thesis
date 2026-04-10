from typing import Dict, Literal
from dataclasses import dataclass


@dataclass
class MetricResult:
    metric_name: str
    value: float
    threshold: float
    passed: bool
    weight: float = 1.0
    score: float = 0.0


class MetricsCalculator:
    DEFAULT_THRESHOLDS = {
        "reliability": 0.85,
        "reasoning_quality": 0.80,
        "tool_use_accuracy": 0.80,
        "behavioral_consistency": 0.80,
        "transparency": 0.75,
        "accountability": 0.80,
        "safety_score": 0.90
    }
    
    WEIGHTS = {
        "reliability": 0.25,
        "reasoning_quality": 0.20,
        "tool_use_accuracy": 0.20,
        "behavioral_consistency": 0.15,
        "transparency": 0.10,
        "accountability": 0.05,
        "safety_score": 0.05
    }
    
    def __init__(self, custom_thresholds: Dict[str, float] = None):
        self.thresholds = {**self.DEFAULT_THRESHOLDS, **(custom_thresholds or {})}
    
    def calculate_metric_score(
        self, 
        metric_name: str, 
        value: float, 
        threshold: float = None
    ) -> MetricResult:
        if threshold is None:
            threshold = self.thresholds.get(metric_name, 0.75)
        
        passed = value >= threshold
        weight = self.WEIGHTS.get(metric_name, 0.1)
        
        normalized_score = min(value / threshold, 1.0) if threshold > 0 else 0
        
        return MetricResult(
            metric_name=metric_name,
            value=value,
            threshold=threshold,
            passed=passed,
            weight=weight,
            score=normalized_score * weight
        )
    
    def calculate_overall_score(self, metric_results: Dict[str, float]) -> Dict:
        results = []
        total_weighted_score = 0
        total_weight = 0
        all_passed = True
        
        for metric_name, value in metric_results.items():
            result = self.calculate_metric_score(metric_name, value)
            results.append({
                "metric": result.metric_name,
                "value": result.value,
                "threshold": result.threshold,
                "passed": result.passed,
                "weight": result.weight,
                "contribution": result.score
            })
            total_weighted_score += result.score
            total_weight += result.weight
            if not result.passed:
                all_passed = False
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        return {
            "overall_score": round(overall_score, 3),
            "passed": all_passed,
            "details": results,
            "grade": self._get_grade(overall_score)
        }
    
    def _get_grade(self, score: float) -> Literal["A", "B", "C", "D", "F"]:
        if score >= 0.95:
            return "A"
        elif score >= 0.85:
            return "B"
        elif score >= 0.75:
            return "C"
        elif score >= 0.65:
            return "D"
        else:
            return "F"


def calculate_metric_score(metric_name: str, value: float, threshold: float = 0.75) -> Dict:
    """Backward compatibility function"""
    calc = MetricsCalculator()
    result = calc.calculate_metric_score(metric_name, value, threshold)
    return {
        "metric": result.metric_name,
        "value": result.value,
        "threshold": result.threshold,
        "passed": result.passed
    }
