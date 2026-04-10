#!/usr/bin/env python3
import os
import sys
import pandas as pd

repo_root = os.path.dirname(os.path.abspath(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from framework.agent_registry import AgentRegistry
from framework.governance import GovernanceEngine
from framework.evaluator import AgentEvaluator
from framework.audit_logger import AuditLogger
from framework.models import RiskLevel


def main():
    print("=" * 60)
    print("AI AGENT GOVERNANCE FRAMEWORK - DEMO")
    print("=" * 60)
    
    # Initialize components
    audit_logger = AuditLogger()
    registry = AgentRegistry()
    governance = GovernanceEngine(audit_logger)
    evaluator = AgentEvaluator()
    
    # Load dummy data
    print("\n📊 Loading dummy agents...")
    try:
        agents_df = pd.read_csv("dummy_data/agents.csv")
        print(f"✅ Loaded {len(agents_df)} agents from CSV")
    except FileNotFoundError:
        print("⚠️  dummy_data/agents.csv not found, using default data")
        agents_df = pd.DataFrame([
            {
                "agent_id": "A001",
                "agent_name": "Trading Assistant",
                "agent_type": "semi-autonomous",
                "purpose": "Assist with trading operations",
                "authorized_tools": "market_data,trading_api,news_feed",
                "risk_level": "high"
            }
        ])
    
    # Register agents
    print("\n📝 Registering agents...")
    for _, row in agents_df.iterrows():
        try:
            tools = row["authorized_tools"].split(",") if isinstance(row["authorized_tools"], str) else []
            agent = registry.register_agent(
                agent_id=row["agent_id"],
                name=row["agent_name"],
                agent_type=row["agent_type"],
                purpose=row["purpose"],
                tools=tools,
                risk_level=row["risk_level"]
            )
            print(f"  ✅ Registered: {agent['name']} ({agent['id']}) - Risk: {agent['risk_level']}")
        except Exception as e:
            print(f"  ⚠️  Failed to register {row.get('agent_id')}: {e}")
    
    # Get first agent for demonstration
    agent_row = agents_df.iloc[0]
    agent = registry.get_agent(agent_row["agent_id"])
    
    print(f"\n{'='*60}")
    print(f"EVALUATING AGENT: {agent['name']} ({agent['id']})")
    print(f"{'='*60}")
    
    # Layer 1: Universal Metrics Evaluation
    print("\n🔍 LAYER 1: Universal Metrics Evaluation")
    universal_scores = {
        "reliability": 0.91,
        "transparency": 0.88,
        "accountability": 0.85,
        "safety_score": 0.92
    }
    
    universal_result = evaluator.evaluate_universal(universal_scores)
    print(f"  Overall Score: {universal_result['overall_score']}")
    print(f"  Grade: {universal_result['grade']}")
    print(f"  Status: {'✅ PASS' if universal_result['passed'] else '❌ FAIL'}")
    print("  Details:")
    for detail in universal_result['details']:
        status = "✅" if detail['passed'] else "❌"
        print(f"    {status} {detail['metric']}: {detail['value']:.2f} (threshold: {detail['threshold']})")
    
    # Layer 2: Workflow-Specific Evaluation
    print("\n🔍 LAYER 2: Workflow-Specific Evaluation (Trading)")
    workflow_scores = {
        "execution_speed": 0.96,
        "slippage_control": 0.91,
        "compliance_adherence": 0.97,
        "risk_management": 0.94
    }
    
    workflow_result = evaluator.evaluate_workflow("trading", workflow_scores)
    print(f"  Workflow: {workflow_result['workflow_type']}")
    print(f"  Overall Score: {workflow_result['overall_score']}")
    print(f"  Status: {'✅ PASS' if workflow_result['passed'] else '❌ FAIL'}")
    print("  Details:")
    for detail in workflow_result['details']:
        status = "✅" if detail['passed'] else "❌"
        print(f"    {status} {detail['metric']}: {detail['value']:.2f} (threshold: {detail['threshold']})")
    
    # Comprehensive Evaluation
    print("\n📊 COMPREHENSIVE EVALUATION")
    comprehensive = evaluator.comprehensive_evaluation(
        agent=agent,
        universal_scores=universal_scores,
        workflow_type="trading",
        workflow_scores=workflow_scores
    )
    print(f"  Combined Score: {comprehensive.overall_score}")
    print(f"  Final Status: {comprehensive.status.upper()}")
    
    # Governance Check
    print(f"\n{'='*60}")
    print("GOVERNANCE COMPLIANCE CHECK")
    print(f"{'='*60}")
    
    # Test with insufficient controls (should fail for high-risk)
    print("\n🔒 Test 1: Basic controls only")
    context_basic = {
        "logging": True,
        "approval": False,
        "authorization_count": 1,
        "kill_switch": False
    }
    gov_result = governance.evaluate(agent, context_basic)
    print(f"  Overall Status: {gov_result.overall_status.value.upper()}")
    print(f"  Can Activate: {'✅ YES' if gov_result.overall_status.value == 'pass' else '❌ NO'}")
    print("  Rule Results:")
    for rule in gov_result.rule_results:
        status = "✅" if rule.status.value == "pass" else ("⚠️" if rule.status.value == "conditional" else "❌")
        req = "[REQUIRED]" if rule.required else "[optional]"
        print(f"    {status} {rule.rule_id}: {rule.description} {req} - {rule.status.value}")
    
    # Test with full controls (should pass)
    print("\n🔒 Test 2: Full compliance controls")
    context_full = {
        "logging": True,
        "approval": True,
        "authorization_count": 2,
        "kill_switch": True,
        "compliance_review": True
    }
    gov_result2 = governance.evaluate(agent, context_full)
    print(f"  Overall Status: {gov_result2.overall_status.value.upper()}")
    print(f"  Can Activate: {'✅ YES' if gov_result2.overall_status.value == 'pass' else '❌ NO'}")
    
    # Audit Log Summary
    print(f"\n{'='*60}")
    print("AUDIT LOG SUMMARY")
    print(f"{'='*60}")
    logs = audit_logger.logs
    print(f"  Total Events: {len(logs)}")
    if logs:
        print(f"  Latest Event: {logs[-1]['event_type']} at {logs[-1]['timestamp']}")
        print(f"  Integrity Check: {'✅ VALID' if audit_logger.verify_integrity() else '❌ CORRUPTED'}")
    
    # Registry Summary
    print(f"\n{'='*60}")
    print("REGISTRY SUMMARY")
    print(f"{'='*60}")
    all_agents = registry.list_agents()
    active_agents = registry.list_agents(status="active")
    high_risk = registry.get_agents_by_risk("high")
    print(f"  Total Agents: {len(all_agents)}")
    print(f"  Active Agents: {len(active_agents)}")
    print(f"  High Risk Agents: {len(high_risk)}")
    
    print(f"\n{'='*60}")
    print("DEMO COMPLETE")
    print(f"{'='*60}")
    print("\nFiles generated:")
    print("  - registry_db.json (agent registry)")
    print("  - audit_log.json (audit trail)")


if __name__ == "__main__":
    main()
