#!/usr/bin/env python3
import os
import sys
import time
import random

repo_root = os.path.dirname(os.path.abspath(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import pandas as pd
from datetime import datetime

from framework.agent_registry import AgentRegistry
from framework.governance import GovernanceEngine
from framework.evaluator import AgentEvaluator
from framework.audit_logger import AuditLogger
from framework.risk_analytics import RiskAnalyticsEngine
from framework.realtime_monitor import RealtimeMonitor
from framework.compliance_reporter import ComplianceReporter, ReportType


def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def alert_handler(alert_data):
    """Handle real-time alerts"""
    status = alert_data.get('status', 'unknown')
    emoji = "🔴" if status == 'critical' else "🟡" if status == 'warning' else "🔵"
    print(f"{emoji} ALERT [{alert_data['agent_id']}] {alert_data['metric_type']}: "
          f"{alert_data['value']:.2f} (threshold: {alert_data['threshold']})")


def main():
    print_section("🚀 AI AGENT GOVERNANCE FRAMEWORK - ENHANCED DEMO")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Initialize all components
    print("\n📦 Initializing components...")
    audit_logger = AuditLogger()
    registry = AgentRegistry()
    governance = GovernanceEngine(audit_logger)
    evaluator = AgentEvaluator()
    risk_analytics = RiskAnalyticsEngine()
    monitor = RealtimeMonitor()
    reporter = ComplianceReporter(audit_logger, registry, governance)
    
    # Register alert handler
    monitor.add_alert_handler(alert_handler)
    
    # Load and register agents
    print_section("📝 AGENT REGISTRATION")
    try:
        agents_df = pd.read_csv("dummy_data/agents.csv")
        print(f"Loaded {len(agents_df)} agents from CSV")
    except FileNotFoundError:
        print("Creating synthetic agents...")
        agents_df = pd.DataFrame([
            {
                "agent_id": "TRADE-001",
                "agent_name": "High-Frequency Trading Bot",
                "agent_type": "autonomous",
                "purpose": "Execute high-frequency trading strategies",
                "authorized_tools": "market_data,trading_api,risk_engine",
                "risk_level": "critical"
            },
            {
                "agent_id": "CUST-001",
                "agent_name": "Customer Service Assistant",
                "agent_type": "semi-autonomous",
                "purpose": "Handle customer inquiries",
                "authorized_tools": "crm_api,knowledge_base,ticketing_system",
                "risk_level": "medium"
            },
            {
                "agent_id": "HR-001",
                "agent_name": "Resume Screening Agent",
                "agent_type": "tool",
                "purpose": "Screen job applications",
                "authorized_tools": "hr_system,email_api",
                "risk_level": "high"
            }
        ])
    
    registered_agents = []
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
            print(f"  ✅ {agent['id']}: {agent['name']} [{agent['risk_level'].upper()}]")
            
            # Subscribe to monitoring
            monitor.subscribe(agent['id'])
            
        except Exception as e:
            print(f"  ⚠️  Failed: {e}")
    
    # Select primary agent for detailed demo
    primary_agent = registry.get_agents_by_risk("critical")[0] if registry.get_agents_by_risk("critical") else registered_agents[0]
    
    print_section("🔍 TWO-LAYER EVALUATION FRAMEWORK")
    print(f"Evaluating: {primary_agent['name']} ({primary_agent['id']})")
    
    # Layer 1: Universal Metrics
    print("\n📊 Layer 1: Universal Metrics")
    universal_scores = {
        "reliability": 0.91,
        "transparency": 0.88,
        "accountability": 0.85,
        "safety_score": 0.92
    }
    
    universal_result = evaluator.evaluate_universal(universal_scores)
    print(f"  Overall Score: {universal_result['overall_score']:.3f}")
    print(f"  Grade: {universal_result['grade']}")
    print(f"  Status: {'✅ PASS' if universal_result['passed'] else '❌ FAIL'}")
    
    # Layer 2: Workflow-Specific
    print("\n📊 Layer 2: Workflow-Specific Metrics (Trading)")
    workflow_scores = {
        "execution_speed": 0.96,
        "slippage_control": 0.91,
        "compliance_adherence": 0.97,
        "risk_management": 0.94
    }
    
    workflow_result = evaluator.evaluate_workflow("trading", workflow_scores)
    print(f"  Workflow Score: {workflow_result['overall_score']:.3f}")
    print(f"  Status: {'✅ PASS' if workflow_result['passed'] else '❌ FAIL'}")
    
    # Comprehensive
    print("\n📊 Comprehensive Evaluation")
    comprehensive = evaluator.comprehensive_evaluation(
        agent=primary_agent,
        universal_scores=universal_scores,
        workflow_type="trading",
        workflow_scores=workflow_scores
    )
    print(f"  Combined Score: {comprehensive.overall_score:.3f}")
    print(f"  Final Status: {comprehensive.status.upper()}")
    
    # Record for risk analytics
    risk_analytics.record_evaluation(
        primary_agent['id'],
        comprehensive.overall_score,
        comprehensive.status,
        {"workflow": "trading"}
    )
    
    print_section("⚖️  GOVERNANCE COMPLIANCE CHECK")
    
    # Test 1: Insufficient controls
    print("\n🔒 Test 1: Insufficient Controls (Expected: FAIL)")
    context_fail = {
        "logging": True,
        "approval": False,
        "authorization_count": 1,
        "kill_switch": False,
        "compliance_review": False
    }
    gov_result = governance.evaluate(primary_agent, context_fail)
    print(f"  Result: {gov_result.overall_status.value.upper()}")
    print(f"  Failed Rules: {len([r for r in gov_result.rule_results if r.status.value == 'fail'])}")
    
    # Test 2: Full compliance
    print("\n🔒 Test 2: Full Compliance Controls (Expected: PASS)")
    context_pass = {
        "logging": True,
        "approval": True,
        "authorization_count": 2,
        "kill_switch": True,
        "compliance_review": True
    }
    gov_result2 = governance.evaluate(primary_agent, context_pass)
    print(f"  Result: {gov_result2.overall_status.value.upper()}")
    print(f"  Can Activate: {'✅ YES' if gov_result2.overall_status.value == 'pass' else '❌ NO'}")
    
    print_section("📈 PREDICTIVE RISK ANALYTICS")
    
    # Generate some historical data for trend analysis
    print("\n📊 Simulating historical evaluations...")
    for i in range(5):
        score = 0.85 + (random.random() * 0.1) - (i * 0.02)  # Slight declining trend
        risk_analytics.record_evaluation(
            primary_agent['id'],
            score,
            "pass" if score > 0.8 else "fail",
            {"iteration": i}
        )
    
    # Analyze trends
    trend = risk_analytics.analyze_trends(primary_agent['id'])
    print(f"\n  Current Risk Score: {trend.risk_score:.2%}")
    print(f"  Trend Direction: {trend.trend_direction.upper()}")
    print(f"  Volatility: {trend.volatility:.3f}")
    print(f"  7-Day Prediction: {trend.prediction_7d:.2%}")
    
    if trend.alerts:
        print("\n  ⚠️  ALERTS:")
        for alert in trend.alerts:
            print(f"    - {alert}")
    
    # Portfolio risk
    print(f"\n📊 Portfolio Risk Summary")
    portfolio = risk_analytics.get_portfolio_risk([a['id'] for a in registered_agents])
    print(f"  Average Risk: {portfolio['average_risk']:.2%}")
    print(f"  Highest Risk Agent: {portfolio['highest_risk']}")
    print(f"  Risk Distribution: {portfolio['risk_distribution']}")
    
    print_section("⚡ REAL-TIME MONITORING")
    
    # Simulate real-time metrics
    print("\n📡 Simulating real-time metrics...")
    metrics_to_simulate = [
        ("response_time_ms", 450),
        ("error_rate", 0.02),
        ("cpu_usage", 65),
        ("api_calls_per_min", 800)
    ]
    
    for metric_type, base_value in metrics_to_simulate:
        # Add some variation
        value = base_value + (random.random() * base_value * 0.2)
        monitor.record_metric(primary_agent['id'], metric_type, value)
        print(f"  {metric_type}: {value:.2f}")
    
    # Simulate critical alert
    print("\n🔴 Simulating critical alert...")
    monitor.record_metric(primary_agent['id'], "error_rate", 0.18, 
                         context={"alert_type": "spike"})
    
    # Get dashboard data
    dashboard_data = monitor.get_dashboard_data()
    print(f"\n📊 Dashboard Data:")
    print(f"  Subscribers: {dashboard_data['total_subscribers']}")
    print(f"  Total Events: {dashboard_data['total_events']}")
    
    print_section("📋 AUTOMATED COMPLIANCE REPORTING")
    
    # Generate daily report
    print("\n📝 Generating compliance report...")
    report = reporter.generate_report(ReportType.DAILY, days_back=1)
    
    print(f"\n  Report ID: {report.report_id}")
    print(f"  Type: {report.report_type.value}")
    print(f"  Period: {report.period_start[:10]} to {report.period_end[:10]}")
    print(f"\n  Summary:")
    print(f"    - Total Agents: {report.summary['total_agents']}")
    print(f"    - Active: {report.summary['active_agents']}")
    print(f"    - Compliance Rate: {report.summary['compliance_rate']:.1%}")
    print(f"    - Critical Alerts: {report.summary['critical_alerts']}")
    
    print(f"\n  Top Recommendations:")
    for i, rec in enumerate(report.recommendations[:3], 1):
        print(f"    {i}. {rec}")
    
    # Export to markdown
    md_content = reporter.export_to_markdown(report)
    print(f"\n  ✅ Report exported to: compliance_reports/{report.report_id}.md")
    
    print_section("🔐 AUDIT TRAIL VERIFICATION")
    
    logs = audit_logger.logs
    print(f"\n  Total Audit Events: {len(logs)}")
    print(f"  Integrity Check: {'✅ VALID' if audit_logger.verify_integrity() else '❌ CORRUPTED'}")
    
    if logs:
        event_types = {}
        for log in logs:
            et = log.get('event_type', 'unknown')
            event_types[et] = event_types.get(et, 0) + 1
        
        print(f"\n  Event Types:")
        for et, count in event_types.items():
            print(f"    - {et}: {count}")
    
    print_section("✅ DEMO COMPLETE")
    
    print(f"\n📁 Generated Files:")
    print(f"  - registry_db.json")
    print(f"  - audit_log.json")
    print(f"  - risk_history.json")
    print(f"  - compliance_reports/{report.report_id}.json")
    print(f"  - compliance_reports/{report.report_id}.md")
    
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"  ✅ Two-layer evaluation framework")
    print(f"  ✅ Risk-based governance controls")
    print(f"  ✅ Predictive risk analytics")
    print(f"  ✅ Real-time monitoring & alerting")
    print(f"  ✅ Automated compliance reporting")
    print(f"  ✅ Immutable audit trails")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
