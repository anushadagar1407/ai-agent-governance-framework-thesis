#!/usr/bin/env python3
import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from framework.agent_registry import AgentRegistry
from framework.governance import GovernanceEngine
from framework.evaluator import AgentEvaluator
from framework.audit_logger import AuditLogger


def main():
    print("Quick Sample Run\n")
    
    # Initialize
    registry = AgentRegistry()
    governance = GovernanceEngine()
    evaluator = AgentEvaluator()
    
    # Register an agent
    agent = registry.register_agent(
        agent_id="A001",
        name="Coding Assistant",
        agent_type="semi-autonomous",
        purpose="code suggestions",
        tools=["git", "python", "docs"],
        risk_level="medium"
    )
    print(f"Registered: {agent['name']} ({agent['id']})")
    
    # Evaluate
    universal_scores = {
        "reliability": 0.91,
        "transparency": 0.85,
        "accountability": 0.88,
        "safety_score": 0.90
    }
    
    result = evaluator.evaluate_universal(universal_scores)
    print(f"\nEvaluation Score: {result['overall_score']}")
    print(f"Grade: {result['grade']}")
    
    # Governance check
    context = {"logging": True, "approval": True}
    gov = governance.evaluate(agent, context)
    print(f"\nGovernance: {gov.overall_status.value}")
    
    print("\n✅ Sample run complete")


if __name__ == "__main__":
    main()
