import pandas as pd
from framework.agent_registry import AgentRegistry
from framework.governance import governance_check
from framework.evaluator import evaluate_agent

agents = pd.read_csv("dummy_data/agents.csv")
print("Dummy agents loaded:")
print(agents)

registry = AgentRegistry()
for _, row in agents.iterrows():
    registry.register_agent(
        row["agent_id"],
        row["agent_name"],
        row["agent_type"],
        row["purpose"],
        row["authorized_tools"].split(","),
        row["risk_level"]
    )

agent_row = agents.iloc[0].to_dict()
agent_row["id"] = agent_row["agent_id"]

scores = {
    "reliability": 0.91,
    "reasoning_quality": 0.84,
    "tool_use_accuracy": 0.88,
    "behavioral_consistency": 0.86
}

evaluation = evaluate_agent(agent_row, scores)
governance = governance_check(agent_row, ["logging", "approval"])

print("\nEvaluation output:")
print(evaluation)

print("\nGovernance output:")
print(governance)
