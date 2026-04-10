from framework.metrics import calculate_metric_score

def evaluate_agent(agent, scores):
    thresholds = {
        "reliability": 0.85,
        "reasoning_quality": 0.80,
        "tool_use_accuracy": 0.80,
        "behavioral_consistency": 0.80
    }

    results = []
    for metric, value in scores.items():
        results.append(calculate_metric_score(metric, value, thresholds.get(metric, 0.75)))

    return {
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "results": results
    }
