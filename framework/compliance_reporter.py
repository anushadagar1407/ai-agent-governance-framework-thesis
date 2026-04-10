import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import markdown

class ReportType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    INCIDENT = "incident"
    AUDIT = "audit"

@dataclass
class ComplianceReport:
    report_id: str
    report_type: ReportType
    generated_at: str
    period_start: str
    period_end: str
    summary: Dict
    details: List[Dict]
    recommendations: List[str]
    regulatory_frameworks: List[str]
    risk_distribution: Dict

class ComplianceReporter:
    def __init__(self, audit_logger, registry, governance_engine):
        self.audit_logger = audit_logger
        self.registry = registry
        self.governance = governance_engine
        self.reports_dir = "compliance_reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Regulatory framework mappings
        self.framework_mappings = {
            "GDPR": ["data_protection", "privacy", "consent"],
            "MiFID_II": ["trading", "execution", "best_interest"],
            "SOX": ["financial_reporting", "audit_trail", "internal_controls"],
            "EU_AI_Act": ["risk_classification", "transparency", "human_oversight"],
            "NIST_AI_RMF": ["governance", "risk_management", "trustworthiness"]
        }
    
    def generate_report(self, report_type: ReportType, 
                       days_back: int = 1) -> ComplianceReport:
        """Generate a compliance report"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Gather data
        agents = self.registry.list_agents()
        audit_logs = self._get_logs_in_period(start_date, end_date)
        
        # Analyze compliance
        summary = self._generate_summary(agents, audit_logs)
        details = self._generate_details(agents, start_date, end_date)
        recommendations = self._generate_recommendations(summary, details)
        risk_dist = self._calculate_risk_distribution(agents)
        
        report = ComplianceReport(
            report_id=f"RPT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            report_type=report_type,
            generated_at=datetime.utcnow().isoformat(),
            period_start=start_date.isoformat(),
            period_end=end_date.isoformat(),
            summary=summary,
            details=details,
            recommendations=recommendations,
            regulatory_frameworks=["EU_AI_Act", "NIST_AI_RMF", "GDPR"],
            risk_distribution=risk_dist
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _get_logs_in_period(self, start: datetime, end: datetime) -> List[Dict]:
        """Get audit logs within time period"""
        logs = []
        for log in self.audit_logger.logs:
            log_time = datetime.fromisoformat(log.get('timestamp', '2000-01-01'))
            if start <= log_time <= end:
                logs.append(log)
        return logs
    
    def _generate_summary(self, agents: List[Dict], 
                         audit_logs: List[Dict]) -> Dict:
        """Generate executive summary"""
        total_agents = len(agents)
        active_agents = len([a for a in agents if a.get('status') == 'active'])
        
        # Governance checks
        gov_failures = len([l for l in audit_logs 
                          if l.get('event_type') == 'governance_evaluation' 
                          and l.get('details', {}).get('overall_status') == 'fail'])
        
        # Risk distribution
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for agent in agents:
            level = agent.get('risk_level', 'medium')
            risk_counts[level] = risk_counts.get(level, 0) + 1
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "inactive_agents": total_agents - active_agents,
            "governance_evaluations": len([l for l in audit_logs 
                                         if l.get('event_type') == 'governance_evaluation']),
            "governance_failures": gov_failures,
            "compliance_rate": 1 - (gov_failures / max(len(audit_logs), 1)),
            "risk_distribution": risk_counts,
            "critical_alerts": len([l for l in audit_logs 
                                  if 'critical' in str(l.get('details', {})).lower()])
        }
    
    def _generate_details(self, agents: List[Dict], 
                         start: datetime, end: datetime) -> List[Dict]:
        """Generate detailed agent-level compliance data"""
        details = []
        
        for agent in agents:
            agent_id = agent.get('id')
            
            # Get recent evaluations
            agent_logs = [l for l in self.audit_logger.logs 
                         if l.get('agent_id') == agent_id]
            
            recent_evals = [l for l in agent_logs 
                          if datetime.fromisoformat(l.get('timestamp', '2000-01-01')) >= start]
            
            # Calculate metrics
            total_checks = len(recent_evals)
            failed_checks = len([e for e in recent_evals 
                               if e.get('details', {}).get('overall_status') == 'fail'])
            
            details.append({
                "agent_id": agent_id,
                "agent_name": agent.get('name'),
                "risk_level": agent.get('risk_level'),
                "status": agent.get('status'),
                "version": agent.get('version'),
                "total_evaluations": total_checks,
                "failed_evaluations": failed_checks,
                "pass_rate": 1 - (failed_checks / max(total_checks, 1)),
                "last_evaluation": recent_evals[-1].get('timestamp') if recent_evals else None,
                "compliance_gaps": self._identify_gaps(agent, recent_evals)
            })
        
        return details
    
    def _identify_gaps(self, agent: Dict, evaluations: List[Dict]) -> List[str]:
        """Identify compliance gaps for an agent"""
        gaps = []
        
        # Check for missing controls based on risk level
        risk = agent.get('risk_level', 'medium')
        
        if risk in ['high', 'critical']:
            # Check if kill switch is documented
            if not agent.get('metadata', {}).get('kill_switch_configured'):
                gaps.append("Kill switch not documented")
            
            # Check for human oversight
            if not any('approval' in str(e.get('details', {})) for e in evaluations[-5:]):
                gaps.append("Recent human oversight not recorded")
        
        # Check version currency
        if agent.get('version') == '1.0.0' and len(evaluations) > 10:
            gaps.append("Agent version may need update")
        
        return gaps
    
    def _generate_recommendations(self, summary: Dict, 
                                   details: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on summary
        if summary['compliance_rate'] < 0.95:
            recommendations.append(
                f"URGENT: Compliance rate ({summary['compliance_rate']:.1%}) below threshold. "
                "Review governance controls immediately."
            )
        
        if summary['risk_distribution'].get('critical', 0) > 0:
            recommendations.append(
                f"Critical risk agents detected ({summary['risk_distribution']['critical']}). "
                "Immediate risk committee review required."
            )
        
        # Based on details
        low_performers = [d for d in details if d['pass_rate'] < 0.8]
        if low_performers:
            recommendations.append(
                f"{len(low_performers)} agents with <80% pass rate require attention: "
                f"{', '.join([d['agent_id'] for d in low_performers[:3]])}"
            )
        
        # General recommendations
        if summary['inactive_agents'] > summary['active_agents'] * 0.1:
            recommendations.append(
                "Consider decommissioning inactive agents to reduce attack surface"
            )
        
        recommendations.append(
            "Schedule quarterly review of all high and critical risk agents"
        )
        
        return recommendations
    
    def _calculate_risk_distribution(self, agents: List[Dict]) -> Dict:
        """Calculate current risk distribution"""
        dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for agent in agents:
            level = agent.get('risk_level', 'medium')
            dist[level] = dist.get(level, 0) + 1
        return dist
    
    def _save_report(self, report: ComplianceReport):
        """Save report to file"""
        filename = f"{self.reports_dir}/{report.report_id}.json"
        with open(filename, 'w') as f:
            json.dump(report.__dict__, f, indent=2, default=str)
    
    def export_to_markdown(self, report: ComplianceReport) -> str:
        """Export report as Markdown for human reading"""
        md = f"""# Compliance Report: {report.report_type.value.upper()}
        
**Report ID:** {report.report_id}  
**Generated:** {report.generated_at}  
**Period:** {report.period_start} to {report.period_end}

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Agents | {report.summary['total_agents']} |
| Active Agents | {report.summary['active_agents']} |
| Compliance Rate | {report.summary['compliance_rate']:.1%} |
| Governance Failures | {report.summary['governance_failures']} |
| Critical Alerts | {report.summary['critical_alerts']} |

### Risk Distribution
"""
        for level, count in report.risk_distribution.items():
            md += f"- **{level.upper()}**: {count} agents\n"
        
        md += "\n## Detailed Findings\n\n"
        md += "| Agent ID | Name | Risk Level | Pass Rate | Status |\n"
        md += "|----------|------|------------|-----------|--------|\n"
        
        for detail in report.details:
            status_emoji = "✅" if detail['pass_rate'] >= 0.9 else "⚠️" if detail['pass_rate'] >= 0.7 else "❌"
            md += f"| {detail['agent_id']} | {detail['agent_name']} | "
            md += f"{detail['risk_level']} | {detail['pass_rate']:.1%} | {status_emoji} |\n"
        
        md += "\n## Recommendations\n\n"
        for i, rec in enumerate(report.recommendations, 1):
            md += f"{i}. {rec}\n"
        
        md += f"\n## Regulatory Frameworks\n"
        for framework in report.regulatory_frameworks:
            md += f"- {framework}\n"
        
        md += "\n---\n*This report was automatically generated by the AI Agent Governance Framework*"
        
        # Save markdown version
        md_filename = f"{self.reports_dir}/{report.report_id}.md"
        with open(md_filename, 'w') as f:
            f.write(md)
        
        return md
    
    def get_regulatory_mapping(self, framework: str) -> Dict:
        """Get mapping of framework requirements to implemented controls"""
        if framework not in self.framework_mappings:
            return {}
        
        keywords = self.framework_mappings[framework]
        
        # Check which keywords are covered in governance rules
        covered = []
        for rule in self.governance.rules:
            rule_text = f"{rule.rule_id} {rule.description}".lower()
            for keyword in keywords:
                if keyword.lower() in rule_text:
                    covered.append({
                        "keyword": keyword,
                        "rule_id": rule.rule_id,
                        "covered": True
                    })
                    break
        
        return {
            "framework": framework,
            "keywords": keywords,
            "coverage": len(covered) / len(keywords) if keywords else 0,
            "mappings": covered
        }
