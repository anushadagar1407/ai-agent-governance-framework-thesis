import os
import sys
import pandas as pd

repo_root = os.path.dirname(os.path.abspath(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

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
agent_row["name"] = agent_row["agent_name"]
agent_row["tools"] = agent_row["authorized_tools"].split(",")

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
