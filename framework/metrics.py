def calculate_metric_score(metric_name, value, threshold):
    return {
        "metric_name": metric_name,
        "value": value,
        "threshold": threshold,
        "passed": value >= threshold
    }
