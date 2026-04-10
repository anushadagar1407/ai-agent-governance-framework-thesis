# Data Dictionary

## agents.csv
- agent_id: Unique agent identifier.
- agent_name: Human-readable name.
- agent_type: Tool, assistant, or autonomous agent.
- workflow: Business workflow name.
- purpose: Intended use case.
- authorized_tools: Approved tools.
- risk_level: Low, medium, or high.
- status: Active, pilot, or inactive.

## evaluations.csv
- evaluation_id: Unique evaluation record.
- agent_id: Related agent.
- metric_name: Metric being measured.
- score: Metric result.
- threshold: Pass threshold.
- passed: yes/no result.
- run_date: Date of evaluation.
