import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from framework.agent_registry import AgentRegistry
from framework.governance import governance_check
from framework.evaluator import evaluate_agent

registry = AgentRegistry()

registry.register_agent(
    "A001",
    "Coding Assistant",
    "semi-autonomous",
    "code suggestions",
    ["git", "python", "docs"],
    "medium"
)

agent = registry.get_agent("A001")
agent["id"] = "A001"

scores = {
    "reliability": 0.91,
    "reasoning_quality": 0.84,
    "tool_use_accuracy": 0.88,
    "behavioral_consistency": 0.86
}

evaluation = evaluate_agent(agent, scores)
governance = governance_check(agent, ["logging", "approval"])

print("Evaluation:", evaluation)
print("Governance:", governance)
