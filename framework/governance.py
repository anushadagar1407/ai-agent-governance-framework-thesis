def governance_check(agent, policy_rules):
    issues = []
    if agent["risk_level"] == "high" and "approval" not in policy_rules:
        issues.append("High-risk agent requires explicit approval.")
    if not agent["tools"]:
        issues.append("No tools assigned.")
    return {
        "agent_name": agent["name"],
        "issues": issues,
        "status": "pass" if len(issues) == 0 else "review required"
    }
