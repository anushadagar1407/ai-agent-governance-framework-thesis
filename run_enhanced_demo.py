#!/usr/bin/env python3
"""
AI Agent Governance Framework - Enhanced Demo
Comprehensive demonstration of all framework capabilities
"""

import os
import sys
import time
import random
import json
from datetime import datetime

repo_root = os.path.dirname(os.path.abspath(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import pandas as pd

# Framework imports
from framework.agent_registry import AgentRegistry
from framework.governance import GovernanceEngine
from framework.evaluator import AgentEvaluator
from framework.audit_logger import AuditLogger
from framework.risk_analytics import RiskAnalyticsEngine
from framework.realtime_monitor import RealtimeMonitor
from framework.compliance_reporter import ComplianceReporter, ReportType
from framework.explainability import ExplainabilityEngine, ExplanationType
from framework.orchestrator import MultiAgentOrchestrator, WorkflowStep, TaskType
from framework.dashboard import DashboardGenerator


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def print_section(title, emoji=""):
    """Print formatted section header"""
    print(f"\n{'='*75}")
    print(f"  {emoji} {title}")
    print(f"{'='*75}")


def print_subsection(title):
    """Print subsection header"""
    print(f"\n  📌 {title}")
    print(f"  {'-'*50}")


def alert_handler(alert_data):
    """Handle real-time alerts"""
    status = alert_data.get('status', 'unknown')
    emoji = "🔴" if status == 'critical' else "🟡" if status == 'warning' else "🔵"
    print(f"    {emoji} ALERT [{alert_data['agent_id']}] {alert_data['metric_type']}: "
          f"{alert_data['value']:.2f} (threshold: {alert_data['threshold']})")


def workflow_step_callback(workflow_id, step_id, result):
    """Callback for workflow step completion"""
    print(f"    ✅ Step {step_id} completed in workflow {workflow_id[:15]}...")


def workflow_completion_callback(workflow_id, results):
    """Callback for workflow completion"""
    print(f"    🎉 Workflow {workflow_id[:15]}... completed with {len(results)} steps")


# ==============================================================================
# MAIN DEMO
# ==============================================================================

def main():
    # Header
    print_section("AI AGENT GOVERNANCE FRAMEWORK - ENHANCED DEMO", "🚀")
    print(f"\n  Timestamp: {datetime.utcnow().isoformat()}")
    print(f"  Python: {sys.version.split()[0]}")
    
    # ==============================================================================
    # PHASE 1: INITIALIZATION
    # ==============================================================================
    print_section("SYSTEM INITIALIZATION", "⚙️")
    
    print("  Initializing core components...")
    
    # Core components
    audit_logger = AuditLogger()
    registry = AgentRegistry()
    governance = GovernanceEngine(audit_logger)
    evaluator = AgentEvaluator()
    
    # Advanced components
    risk_analytics = RiskAnalyticsEngine()
    monitor = RealtimeMonitor()
    reporter = ComplianceReporter(audit_logger, registry, governance)
    xai = ExplainabilityEngine()
    orchestrator = MultiAgentOrchestrator(registry, governance, evaluator)
    
    # Register callbacks
    monitor.add_alert_handler(alert_handler)
    orchestrator.add_step_callback(workflow_step_callback)
    orchestrator.add_completion_callback(workflow_completion_callback)
    
    print("    ✅ Agent Registry (persistent storage)")
    print("    ✅ Governance Engine (7 rule types)")
    print("    ✅ Two-Layer Evaluator (universal + workflow-specific)")
    print("    ✅ Audit Logger (immutable, hash-chained)")
    print("    ✅ Risk Analytics Engine (predictive)")
    print("    ✅ Real-time Monitor (anomaly detection)")
    print("    ✅ Compliance Reporter (automated)")
    print("    ✅ Explainability Engine (XAI)")
    print("    ✅ Multi-Agent Orchestrator (workflows)")
    
    # ==============================================================================
    # PHASE 2: AGENT REGISTRATION
    # ==============================================================================
    print_section("AGENT REGISTRATION & LIFECYCLE", "📝")
    
    # Load or create agents
    try:
        agents_df = pd.read_csv("dummy_data/agents.csv")
        print(f"  Loaded {len(agents_df)} agents from CSV")
    except FileNotFoundError:
        print("  Creating synthetic enterprise agents...")
        agents_df = pd.DataFrame([
            {
                "agent_id": "TRADE-001",
                "agent_name": "High-Frequency Trading Bot",
                "agent_type": "autonomous",
                "purpose": "Execute high-frequency trading strategies with risk controls",
                "authorized_tools": "market_data,trading_api,risk_engine,compliance_checker",
                "risk_level": "critical",
                "department": "Trading"
            },
            {
                "agent_id": "CUST-001",
                "agent_name": "Customer Service Assistant",
                "agent_type": "semi-autonomous",
                "purpose": "Handle customer inquiries and resolve tickets",
                "authorized_tools": "crm_api,knowledge_base,ticketing_system,email_api",
                "risk_level": "medium",
                "department": "Customer Service"
            },
            {
                "agent_id": "HR-001",
                "agent_name": "Resume Screening Agent",
                "agent_type": "tool",
                "purpose": "Screen job applications for bias and qualification",
                "authorized_tools": "hr_system,email_api,analytics",
                "risk_level": "high",
                "department": "HR"
            },
            {
                "agent_id": "FRAUD-001",
                "agent_name": "Fraud Detection System",
                "agent_type": "autonomous",
                "purpose": "Detect and flag suspicious transactions in real-time",
                "authorized_tools": "transaction_db,alert_system,messaging_api",
                "risk_level": "critical",
                "department": "Risk Management"
            }
        ])
    
    registered_agents = []
    skipped_agents = []
    
    for _, row in agents_df.iterrows():
        try:
            tools = row["authorized_tools"].split(",") if isinstance(row["authorized_tools"], str) else []
            agent = registry.register_agent(
                agent_id=row["agent_id"],
                name=row["agent_name"],
                agent_type=row["agent_type"],
                purpose=row["purpose"],
                tools=tools,
                risk_level=row["risk_level"],
                metadata={"department": row.get("department", "Unknown")}
            )
            registered_agents.append(agent)
            
            risk_emoji = "🔴" if agent['risk_level'] == 'critical' else \
                        "🟠" if agent['risk_level'] == 'high' else \
                        "🟡" if agent['risk_level'] == 'medium' else "🟢"
            
            print(f"    {risk_emoji} REGISTERED: {agent['id']}: {agent['name']} [{agent['risk_level'].upper()}]")
            
            # Subscribe to real-time monitoring
            monitor.subscribe(agent['id'])
            
        except ValueError as e:
            if "already exists" in str(e).lower():
                # Agent exists - fetch from registry
                existing_agent = registry.get_agent(row["agent_id"])
                if existing_agent:
                    registered_agents.append(existing_agent)
                    skipped_agents.append(row["agent_id"])
                    
                    risk_emoji = "🔴" if existing_agent['risk_level'] == 'critical' else \
                                "🟠" if existing_agent['risk_level'] == 'high' else \
                                "🟡" if existing_agent['risk_level'] == 'medium' else "🟢"
                    
                    print(f"    {risk_emoji} EXISTS: {existing_agent['id']}: {existing_agent['name']} [{existing_agent['risk_level'].upper()}] (reusing)")
                    
                    # Subscribe to real-time monitoring
                    monitor.subscribe(existing_agent['id'])
            else:
                print(f"    ⚠️  ERROR: {row.get('agent_id')}: {e}")
    
    # Verify we have agents to work with
    if not registered_agents:
        print("\n    ❌ CRITICAL: No agents available for demo!")
        print("    Please delete registry_db.json and try again.")
        return 1
    
    if skipped_agents:
        print(f"\n    ℹ️  Reused {len(skipped_agents)} existing agents from previous run")
    
    # Select primary agent for detailed demo
    critical_agents = registry.get_agents_by_risk("critical")
    high_risk_agents = registry.get_agents_by_risk("high")
    
    # Priority: critical > high > any available
    if critical_agents:
        primary_agent = critical_agents[0]
        print(f"\n  Primary demo agent (CRITICAL): {primary_agent['name']} ({primary_agent['id']})")
    elif high_risk_agents:
        primary_agent = high_risk_agents[0]
        print(f"\n  Primary demo agent (HIGH): {primary_agent['name']} ({primary_agent['id']})")
    elif registered_agents:
        primary_agent = registered_agents[0]
        print(f"\n  Primary demo agent (DEFAULT): {primary_agent['name']} ({primary_agent['id']})")
    else:
        print("\n    ❌ CRITICAL: No agents available for demo!")
        return 1
    
    # ==============================================================================
    # PHASE 3: TWO-LAYER EVALUATION FRAMEWORK
    # ==============================================================================
    print_section("TWO-LAYER EVALUATION FRAMEWORK", "🔍")
    
    print_subsection("Layer 1: Universal Metrics (All Agents)")
    
    universal_scores = {
        "reliability": 0.91,
        "transparency": 0.88,
        "accountability": 0.85,
        "safety_score": 0.92
    }
    
    universal_result = evaluator.evaluate_universal(universal_scores)
    
    print(f"    Overall Score: {universal_result['overall_score']:.3f}")
    print(f"    Grade: {universal_result['grade']}")
    print(f"    Status: {'✅ PASS' if universal_result['passed'] else '❌ FAIL'}")
    print(f"    Weighted Components:")
    for detail in universal_result['details']:
        status = "✅" if detail['passed'] else "❌"
        print(f"      {status} {detail['metric']}: {detail['value']:.2f} "
              f"(weight: {detail['weight']:.0%}, threshold: {detail['threshold']})")
    
    print_subsection("Layer 2: Workflow-Specific Metrics")
    
    # Trading workflow evaluation for primary agent
    workflow_scores = {
        "execution_speed": 0.96,
        "slippage_control": 0.91,
        "compliance_adherence": 0.97,
        "risk_management": 0.94
    }
    
    workflow_result = evaluator.evaluate_workflow("trading", workflow_scores)
    
    print(f"    Workflow Type: TRADING")
    print(f"    Overall Score: {workflow_result['overall_score']:.3f}")
    print(f"    Status: {'✅ PASS' if workflow_result['passed'] else '❌ FAIL'}")
    print(f"    Metrics vs Thresholds:")
    for detail in workflow_result['details']:
        status = "✅" if detail['passed'] else "❌"
        gap = detail['value'] - detail['threshold']
        print(f"      {status} {detail['metric']}: {detail['value']:.2f} "
              f"(threshold: {detail['threshold']}, gap: {gap:+.3f})")
    
    print_subsection("Comprehensive Evaluation (Combined)")
    
    comprehensive = evaluator.comprehensive_evaluation(
        agent=primary_agent,
        universal_scores=universal_scores,
        workflow_type="trading",
        workflow_scores=workflow_scores
    )
    
    combined_weight = "60% Universal + 40% Workflow"
    print(f"    Weighting: {combined_weight}")
    print(f"    Combined Score: {comprehensive.overall_score:.3f}")
    print(f"    Final Status: {comprehensive.status.upper()}")
    print(f"    Evaluator: {comprehensive.evaluator_id}")
    
    # Record for risk analytics
    risk_analytics.record_evaluation(
        primary_agent['id'],
        comprehensive.overall_score,
        comprehensive.status,
        {"workflow": "trading", "layer1_score": universal_result['overall_score'],
         "layer2_score": workflow_result['overall_score']}
    )
    
    # ==============================================================================
    # PHASE 4: GOVERNANCE COMPLIANCE
    # ==============================================================================
    print_section("GOVERNANCE COMPLIANCE ENGINE", "⚖️")
    
    print_subsection("Test 1: Insufficient Controls (Expected: FAIL)")
    
    context_fail = {
        "logging": True,
        "approval": False,  # Missing approval
        "authorization_count": 1,  # Only 1 auth (need 2 for critical)
        "kill_switch": False,  # Missing kill switch
        "compliance_review": False
    }
    
    gov_result_fail = governance.evaluate(primary_agent, context_fail)
    
    print(f"    Overall Status: {gov_result_fail.overall_status.value.upper()}")
    print(f"    Can Activate: {'✅ YES' if gov_result_fail.overall_status.value == 'pass' else '❌ NO'}")
    print(f"    Rules Evaluated: {len(gov_result_fail.rule_results)}")
    
    failed_rules = [r for r in gov_result_fail.rule_results if r.status.value == 'fail']
    if failed_rules:
        print(f"    ❌ Failed Required Rules:")
        for rule in failed_rules:
            if rule.required:
                print(f"      • {rule.rule_id}: {rule.description}")
    
    print_subsection("Test 2: Full Compliance Controls (Expected: PASS)")
    
    context_pass = {
        "logging": True,
        "approval": True,
        "authorization_count": 2,
        "kill_switch": True,
        "compliance_review": True,
        "audit_trail": True
    }
    
    gov_result_pass = governance.evaluate(primary_agent, context_pass)
    
    print(f"    Overall Status: {gov_result_pass.overall_status.value.upper()}")
    print(f"    Can Activate: {'✅ YES' if gov_result_pass.overall_status.value == 'pass' else '❌ NO'}")
    print(f"    All Rules Passed: {len([r for r in gov_result_pass.rule_results if r.status.value == 'pass'])}/{len(gov_result_pass.rule_results)}")
    
    # Show all rules for transparency
    print(f"    Detailed Results:")
    for rule in gov_result_pass.rule_results:
        emoji = "✅" if rule.status.value == 'pass' else "⚠️" if rule.status.value == 'conditional' else "❌"
        req = "[REQ]" if rule.required else "[opt]"
        print(f"      {emoji} {rule.rule_id} {req}: {rule.description} -> {rule.status.value}")
    
    # ==============================================================================
    # PHASE 5: PREDICTIVE RISK ANALYTICS
    # ==============================================================================
    print_section("PREDICTIVE RISK ANALYTICS", "📈")
    
    print_subsection("Simulating Historical Data")
    
    # Generate realistic historical trend (slight degradation)
    print("    Generating 10 days of historical evaluations...")
    base_score = 0.92
    for i in range(10):
        # Simulate slight degradation with noise
        degradation = i * 0.015
        noise = (random.random() - 0.5) * 0.04
        score = max(0.6, min(1.0, base_score - degradation + noise))
        status = "pass" if score > 0.8 else "fail"
        
        risk_analytics.record_evaluation(
            primary_agent['id'],
            score,
            status,
            {"day": i + 1, "scenario": "historical_simulation"}
        )
        print(f"      Day {i+1}: Score={score:.3f}, Status={status}")
    
    print_subsection("Current Risk Analysis")
    
    trend = risk_analytics.analyze_trends(primary_agent['id'])
    
    risk_emoji = "🟢" if trend.risk_score < 0.3 else \
                 "🟡" if trend.risk_score < 0.6 else \
                 "🟠" if trend.risk_score < 0.8 else "🔴"
    
    print(f"    {risk_emoji} Current Risk Score: {trend.risk_score:.2%}")
    print(f"    Trend Direction: {trend.trend_direction.upper()}")
    print(f"    Volatility (σ): {trend.volatility:.4f}")
    print(f"    7-Day Prediction: {trend.prediction_7d:.2%}")
    print(f"    Data Points: {len(risk_analytics.risk_history.get(primary_agent['id'], []))}")
    
    if trend.alerts:
        print(f"    ⚠️  ACTIVE ALERTS:")
        for alert in trend.alerts:
            print(f"      • {alert}")
    else:
        print(f"    ✅ No active alerts")
    
    print_subsection("Portfolio Risk Summary")
    
    all_agent_ids = [a['id'] for a in registered_agents]
    portfolio = risk_analytics.get_portfolio_risk(all_agent_ids)
    
    print(f"    Portfolio Size: {portfolio['total_agents']} agents")
    print(f"    Average Risk: {portfolio['average_risk']:.2%}")
    print(f"    Highest Risk Agent: {portfolio['highest_risk']}")
    print(f"    Risk Distribution:")
    for level, count in portfolio['risk_distribution'].items():
        bar = "█" * count
        print(f"      {level:10}: {bar} ({count})")
    
    # Generate risk report
    print_subsection("Detailed Risk Report")
    risk_report = risk_analytics.generate_risk_report(primary_agent['id'])
    print(risk_report[:800] + "...\n    [Full report saved to system]")
    
    # ==============================================================================
    # PHASE 6: REAL-TIME MONITORING
    # ==============================================================================
    print_section("REAL-TIME MONITORING & ANOMALY DETECTION", "⚡")
    
    print_subsection("Simulating Live Metrics Stream")
    
    metrics_scenarios = [
        ("response_time_ms", 450, "normal"),
        ("cpu_usage", 65, "normal"),
        ("memory_usage", 72, "normal"),
        ("api_calls_per_min", 850, "normal"),
        ("response_time_ms", 520, "warning"),  # Exceeds 500 threshold
        ("error_rate", 0.02, "normal"),
        ("error_rate", 0.18, "critical"),  # Exceeds 0.15 threshold
        ("cpu_usage", 95, "critical"),  # Exceeds 90 threshold
    ]
    
    for metric_type, value, scenario in metrics_scenarios:
        monitor.record_metric(primary_agent['id'], metric_type, value, 
                             context={"scenario": scenario, "source": "simulation"})
        time.sleep(0.1)  # Brief pause for realism
    
    print(f"    Streamed {len(metrics_scenarios)} metric events")
    
    print_subsection("Aggregated Statistics (Last 5 Minutes)")
    
    for metric_type in ["response_time_ms", "error_rate", "cpu_usage"]:
        stats = monitor.get_aggregated_stats(primary_agent['id'], metric_type, window_minutes=5)
        if stats['count'] > 0:
            print(f"    {metric_type}:")
            print(f"      Count: {stats['count']}, Avg: {stats['avg']:.2f}, "
                  f"Current: {stats['current']:.2f}, Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
    
    print_subsection("Dashboard Data")
    
    dashboard_data = monitor.get_dashboard_data()
    print(f"    Active Subscribers: {dashboard_data['total_subscribers']}")
    print(f"    Total Events (buffer): {dashboard_data['total_events']}")
    print(f"    Last Updated: {dashboard_data['timestamp']}")
    
    # ==============================================================================
    # PHASE 7: EXPLAINABILITY (XAI)
    # ==============================================================================
    print_section("EXPLAINABLE AI (XAI)", "🔍")
    
    print_subsection("Explaining Evaluation Decision")
    
    exp_eval = xai.explain_evaluation(primary_agent, universal_result)
    
    print(f"    Explanation ID: {exp_eval.explanation_id}")
    print(f"    Type: {exp_eval.explanation_type.value}")
    print(f"    Decision: {exp_eval.decision}")
    print(f"    Confidence: {exp_eval.confidence:.1%}")
    print(f"    Top Contributing Factors:")
    for i, factor in enumerate(exp_eval.factors[:3], 1):
        impact_emoji = "🟢" if factor['impact'] == "positive" else "🔴"
        print(f"      {i}. {impact_emoji} {factor['metric']}: {factor['explanation'][:60]}...")
    
    print(f"    Counterfactual: {exp_eval.counterfactual[:100]}...")
    
    print_subsection("Explaining Governance Decision")
    
    gov_explained = {
        "passed": gov_result_pass.overall_status.value == "pass",
        "details": [{"rule_id": r.rule_id, "description": r.description, 
                    "status": r.status.value, "required": r.required} 
                   for r in gov_result_pass.rule_results]
    }
    
    exp_gov = xai.explain_governance_decision(primary_agent, gov_explained)
    
    print(f"    Decision: {exp_gov.decision}")
    print(f"    Key Compliance Factors:")
    for factor in exp_gov.factors[:4]:
        req = "[REQ]" if factor.get('required') else "[optional]"
        status = "✅" if factor['status'] == 'pass' else "❌"
        print(f"      {status} {factor['rule_id']} {req}: {factor['description'][:50]}...")
    
    print(f"    What-If Scenario: {exp_gov.counterfactual}")
    
    print_subsection("Explaining Risk Score")
    
    exp_risk = xai.explain_risk_score(primary_agent, trend)
    
    print(f"    Risk Category: {exp_risk.decision}")
    print(f"    Confidence: {exp_risk.confidence:.1%}")
    print(f"    Contributing Factors:")
    for factor in exp_risk.factors:
        impact_emoji = "🔴" if factor['impact'] == "high" else \
                      "🟡" if factor['impact'] == "medium" else "🟢"
        print(f"      {impact_emoji} {factor['factor']}: {factor['explanation']}")
    
     # ==============================================================================
    # PHASE 8: MULTI-AGENT ORCHESTRATION
    # ==============================================================================
    print_section("MULTI-AGENT ORCHESTRATION", "🎛️")
    
    # Check if we have enough agents for workflows
    if len(registered_agents) < 2:
        print("  ⚠️  Not enough agents for multi-agent workflows (need 2+)")
        print("  Skipping orchestration demo...")
    else:
        print_subsection("Creating Document Approval Workflow")
        
        # Create a 3-step workflow: Draft -> Review -> Approve
        workflow_steps = [
            WorkflowStep(
                step_id="draft",
                agent_id=registered_agents[0]['id'],
                task_type=TaskType.SEQUENTIAL,
                action="draft_document",
                parameters={"doc_type": "compliance_report", "template": "standard"},
                dependencies=[],
                timeout_seconds=300
            ),
            WorkflowStep(
                step_id="review",
                agent_id=registered_agents[1]['id'] if len(registered_agents) > 1 else registered_agents[0]['id'],
                task_type=TaskType.SEQUENTIAL,
                action="review_content",
                parameters={"check_bias": True, "check_accuracy": True},
                dependencies=["draft"],
                timeout_seconds=600
            )
        ]
        
        # Add third step if available
        if len(registered_agents) > 2:
            workflow_steps.append(
                WorkflowStep(
                    step_id="approve",
                    agent_id=registered_agents[2]['id'],
                    task_type=TaskType.SEQUENTIAL,
                    action="final_approval",
                    parameters={"require_signature": True},
                    dependencies=["review"],
                    timeout_seconds=120
                )
            )
        
        try:
            workflow_id = orchestrator.create_workflow("Document_Approval_v1", workflow_steps)
            print(f"    Workflow ID: {workflow_id}")
            print(f"    Steps: {len(workflow_steps)} (Sequential)")
            for step in workflow_steps:
                dep_str = f" (depends on: {step.dependencies})" if step.dependencies else ""
                print(f"      • {step.step_id}: {step.action} by {step.agent_id}{dep_str}")
            
            print_subsection("Validating Workflow")
            
            validation = orchestrator.validate_workflow(workflow_id)
            print(f"    Valid: {'✅ YES' if validation['valid'] else '❌ NO'}")
            if validation['errors']:
                print(f"    Errors: {validation['errors']}")
            if validation['warnings']:
                print(f"    Warnings: {len(validation['warnings'])}")
                for w in validation['warnings'][:2]:
                    print(f"      ⚠️  {w[:60]}...")
            
            print_subsection("Workflow Status")
            
            status = orchestrator.get_workflow_status(workflow_id)
            if status:
                print(f"    Status: {status['status']}")
                print(f"    Progress: {status['progress']}")
                print(f"    Created: {status['created_at'][:19]}")
            
            print_subsection("Template-Based Workflow Creation")
            
            # Create from template
            template_agents = [a['id'] for a in registered_agents[:2]]
            template_id = orchestrator.create_template_workflow(
                "incident_response",
                template_agents
            )
            print(f"    Created incident response workflow: {template_id[:25]}...")
            print(f"    Type: Conditional (Detect -> Assess)")
            
            # List all workflows
            all_workflows = orchestrator.list_workflows()
            print(f"    Total Workflows: {len(all_workflows)}")
            for wf in all_workflows[:3]:
                print(f"      • {wf['workflow_id'][:20]}... | {wf['name']} | {wf['status']}")
                
        except Exception as e:
            print(f"    ⚠️  Workflow error: {e}")
            print("    Continuing with demo...")
    
    # ==============================================================================
    # PHASE 9: COMPLIANCE REPORTING
    # ==============================================================================
    print_section("AUTOMATED COMPLIANCE REPORTING", "📋")
    
    print_subsection("Generating Daily Compliance Report")
    
    report = reporter.generate_report(ReportType.DAILY, days_back=1)
    
    print(f"    Report ID: {report.report_id}")
    print(f"    Type: {report.report_type.value.upper()}")
    print(f"    Period: {report.period_start[:10]} to {report.period_end[:10]}")
    print(f"    Regulatory Frameworks: {', '.join(report.regulatory_frameworks)}")
    
    print(f"\n    Executive Summary:")
    summary = report.summary
    print(f"      • Total Agents: {summary['total_agents']}")
    print(f"      • Active: {summary['active_agents']} | Inactive: {summary['inactive_agents']}")
    print(f"      • Governance Evaluations: {summary['governance_evaluations']}")
    print(f"      • Compliance Rate: {summary['compliance_rate']:.1%}")
    print(f"      • Critical Alerts: {summary['critical_alerts']}")
    
    print(f"\n    Risk Distribution:")
    for level, count in report.risk_distribution.items():
        pct = (count / summary['total_agents'] * 100) if summary['total_agents'] > 0 else 0
        print(f"      • {level.upper()}: {count} agents ({pct:.1f}%)")
    
    print(f"\n    Top Recommendations:")
    for i, rec in enumerate(report.recommendations[:3], 1):
        priority = "🔴" if "URGENT" in rec or "CRITICAL" in rec else \
                  "🟡" if "WARNING" in rec else "🟢"
        print(f"      {i}. {priority} {rec[:70]}...")
    
    print_subsection("Exporting Reports")
    
    # Export to Markdown
    md_path = reporter.export_to_markdown(report)
    print(f"    ✅ Markdown report: {md_path}")
    
    # Check regulatory mapping
    mapping = reporter.get_regulatory_mapping("EU_AI_Act")
    print(f"\n    EU AI Act Coverage: {mapping['coverage']:.1%}")
    print(f"    Mapped Requirements: {len(mapping['mappings'])}/{len(mapping['keywords'])}")
    
    # ==============================================================================
    # PHASE 10: INTERACTIVE DASHBOARD
    # ==============================================================================
    print_section("INTERACTIVE DASHBOARD GENERATION", "🎛️")
    
    dashboard = DashboardGenerator()
    
    print("  Generating HTML dashboard...")
    dashboard_file = dashboard.generate_full_dashboard(registry, monitor, risk_analytics, reporter)
    print(f"    ✅ Main dashboard: {dashboard_file}")
    
    print("  Exporting metrics JSON...")
    metrics_file = dashboard.export_metrics_json(registry, monitor)
    print(f"    ✅ Metrics export: {metrics_file}")
    
    print(f"\n  🌐 To view dashboard:")
    print(f"     Open file://{os.path.abspath(dashboard_file)} in your browser")
    print(f"     (Auto-refreshes every 30 seconds)")
    
    # ==============================================================================
    # PHASE 11: AUDIT TRAIL VERIFICATION
    # ==============================================================================
    print_section("AUDIT TRAIL VERIFICATION", "🔐")
    
    logs = audit_logger.logs
    
    print(f"    Total Audit Events: {len(logs)}")
    print(f"    Integrity Verification: {'✅ VALID' if audit_logger.verify_integrity() else '❌ CORRUPTED'}")
    
    if logs:
        # Event type breakdown
        event_types = {}
        for log in logs:
            et = log.get('event_type', 'unknown')
            event_types[et] = event_types.get(et, 0) + 1
        
        print(f"\n    Event Type Distribution:")
        for et, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
            print(f"      • {et}: {count}")
        
        # Show recent events
        print(f"\n    Recent Events (last 3):")
        for log in logs[-3:]:
            ts = log.get('timestamp', 'N/A')
            et = log.get('event_type', 'N/A')
            aid = log.get('agent_id', 'N/A')
            print(f"      [{ts[:19]}] {et} | Agent: {aid}")
    
    # ==============================================================================
    # FINAL SUMMARY
    # ==============================================================================
    print_section("DEMO COMPLETE - SUMMARY", "✅")
    
    print("  📁 Generated Files:")
    generated_files = [
        "registry_db.json",
        "audit_log.json", 
        "risk_history.json",
        "explanations.json",
        "workflows.json",
        f"compliance_reports/{report.report_id}.json",
        f"compliance_reports/{report.report_id}.md",
        "dashboard/index.html",
        "dashboard/metrics.json"
    ]
    for f in generated_files:
        print(f"    • {f}")
    
    print("\n  🎯 Framework Components Demonstrated:")
    components = [
        ("Agent Registry", "Persistent storage with CRUD operations"),
        ("Two-Layer Evaluation", "Universal + Workflow-specific metrics"),
        ("Risk-Based Governance", "7 rule types with risk-level conditioning"),
        ("Predictive Risk Analytics", "Trend analysis + 7-day predictions"),
        ("Real-Time Monitoring", "Live metrics + anomaly detection"),
        ("Explainable AI (XAI)", "Human-readable decision explanations"),
        ("Multi-Agent Orchestration", "Workflow management with dependencies"),
        ("Compliance Reporting", "Automated reports with regulatory mapping"),
        ("Interactive Dashboard", "HTML visualization with auto-refresh"),
        ("Immutable Audit Trail", "Hash-chained, tamper-evident logging")
    ]
    
    for i, (name, desc) in enumerate(components, 1):
        print(f"    {i:2}. ✅ {name:<25} - {desc}")
    
    print(f"\n  📊 Final Statistics:")
    print(f"    • Agents Registered: {len(registered_agents)}")
    print(f"    • Critical Risk: {len([a for a in registered_agents if a['risk_level'] == 'critical'])}")
    print(f"    • Audit Events: {len(logs)}")
    print(f"    • Risk Predictions: {len(risk_analytics.risk_history.get(primary_agent['id'], []))}")
    print(f"    • Explanations Generated: {len(xai.explanations)}")
    print(f"    • Workflows Created: {len(orchestrator.workflows)}")
    
    print(f"\n{'='*75}")
    print("  Thank you for using the AI Agent Governance Framework!")
    print(f"{'='*75}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
