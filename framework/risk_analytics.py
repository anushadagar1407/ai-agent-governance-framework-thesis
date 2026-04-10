import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import statistics

@dataclass
class RiskTrend:
    agent_id: str
    risk_score: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    volatility: float
    prediction_7d: float
    alerts: List[str]

class RiskAnalyticsEngine:
    def __init__(self, history_path: str = "risk_history.json"):
        self.history_path = history_path
        self.risk_history: Dict[str, List[Dict]] = self._load_history()
        self.thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 0.95
        }
    
    def _load_history(self) -> Dict[str, List[Dict]]:
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_history(self):
        with open(self.history_path, 'w') as f:
            json.dump(self.risk_history, f, indent=2, default=str)
    
    def calculate_risk_score(self, agent: Dict, evaluations: List[Dict]) -> float:
        """Calculate composite risk score based on multiple factors"""
        base_risk = self._get_base_risk_level(agent.get('risk_level', 'medium'))
        
        # Factor 1: Recent evaluation performance (30%)
        if evaluations:
            recent_scores = [e.get('overall_score', 0.8) for e in evaluations[-5:]]
            performance_factor = 1 - statistics.mean(recent_scores)
        else:
            performance_factor = 0.2
        
        # Factor 2: Agent autonomy level (25%)
        autonomy_map = {"tool": 0.1, "semi-autonomous": 0.5, "autonomous": 0.9}
        autonomy_factor = autonomy_map.get(agent.get('agent_type'), 0.5)
        
        # Factor 3: Tool access breadth (20%)
        tools = agent.get('tools', [])
        tool_risk = min(len(tools) * 0.1, 1.0)
        
        # Factor 4: Historical incidents (25%)
        incidents = self._count_recent_incidents(agent.get('id'))
        incident_factor = min(incidents * 0.2, 1.0)
        
        # Weighted composite
        risk_score = (
            base_risk * 0.4 +
            performance_factor * 0.3 +
            autonomy_factor * 0.15 +
            tool_risk * 0.1 +
            incident_factor * 0.05
        )
        
        return min(risk_score, 1.0)
    
    def _get_base_risk_level(self, risk_level: str) -> float:
        mapping = {
            "low": 0.25,
            "medium": 0.5,
            "high": 0.75,
            "critical": 0.9
        }
        return mapping.get(risk_level.lower(), 0.5)
    
    def _count_recent_incidents(self, agent_id: str, days: int = 30) -> int:
        """Count governance failures in last N days"""
        if agent_id not in self.risk_history:
            return 0
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        incidents = 0
        
        for entry in self.risk_history[agent_id]:
            entry_time = datetime.fromisoformat(entry.get('timestamp', '2000-01-01'))
            if entry_time > cutoff and entry.get('governance_status') == 'fail':
                incidents += 1
        
        return incidents
    
    def analyze_trends(self, agent_id: str) -> RiskTrend:
        """Analyze risk trends and predict future risk"""
        history = self.risk_history.get(agent_id, [])
        
        if len(history) < 3:
            return RiskTrend(
                agent_id=agent_id,
                risk_score=0.5,
                trend_direction="stable",
                volatility=0.0,
                prediction_7d=0.5,
                alerts=["Insufficient data for trend analysis"]
            )
        
        # Calculate trend
        recent_scores = [h.get('risk_score', 0.5) for h in history[-10:]]
        current_score = recent_scores[-1]
        
        if len(recent_scores) >= 3:
            slope = recent_scores[-1] - recent_scores[-3]
            if slope > 0.1:
                trend = "increasing"
            elif slope < -0.1:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Calculate volatility
        volatility = statistics.stdev(recent_scores) if len(recent_scores) > 1 else 0
        
        # Simple linear prediction for 7 days
        if len(recent_scores) >= 3:
            daily_change = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
            prediction = current_score + (daily_change * 7)
            prediction = max(0, min(1, prediction))
        else:
            prediction = current_score
        
        # Generate alerts
        alerts = []
        if current_score > 0.8:
            alerts.append("CRITICAL: Risk score exceeds threshold")
        if trend == "increasing" and current_score > 0.6:
            alerts.append("WARNING: Risk trend is increasing")
        if volatility > 0.2:
            alerts.append("WARNING: High volatility detected")
        
        return RiskTrend(
            agent_id=agent_id,
            risk_score=current_score,
            trend_direction=trend,
            volatility=volatility,
            prediction_7d=prediction,
            alerts=alerts
        )
    
    def record_evaluation(self, agent_id: str, risk_score: float, 
                         governance_status: str, details: Dict):
        """Record evaluation for trend analysis"""
        if agent_id not in self.risk_history:
            self.risk_history[agent_id] = []
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "risk_score": risk_score,
            "governance_status": governance_status,
            "details": details
        }
        
        self.risk_history[agent_id].append(entry)
        
        # Keep only last 100 entries per agent
        self.risk_history[agent_id] = self.risk_history[agent_id][-100:]
        self._save_history()
    
    def get_portfolio_risk(self, agent_ids: List[str]) -> Dict:
        """Calculate overall portfolio risk metrics"""
        if not agent_ids:
            return {"average_risk": 0, "highest_risk": None, "risk_distribution": {}}
        
        scores = []
        distribution = defaultdict(int)
        
        for agent_id in agent_ids:
            trend = self.analyze_trends(agent_id)
            scores.append(trend.risk_score)
            
            # Categorize
            if trend.risk_score < 0.3:
                distribution["low"] += 1
            elif trend.risk_score < 0.6:
                distribution["medium"] += 1
            elif trend.risk_score < 0.8:
                distribution["high"] += 1
            else:
                distribution["critical"] += 1
        
        highest_risk_agent = max(agent_ids, 
                                key=lambda x: self.analyze_trends(x).risk_score)
        
        return {
            "average_risk": statistics.mean(scores),
            "highest_risk": highest_risk_agent,
            "risk_distribution": dict(distribution),
            "total_agents": len(agent_ids)
        }
    
    def generate_risk_report(self, agent_id: str) -> str:
        """Generate human-readable risk report"""
        trend = self.analyze_trends(agent_id)
        
        report = f"""
RISK ANALYSIS REPORT
Agent ID: {agent_id}
Generated: {datetime.utcnow().isoformat()}

CURRENT RISK PROFILE
- Risk Score: {trend.risk_score:.2%} ({self._categorize_risk(trend.risk_score)})
- Trend Direction: {trend.trend_direction.upper()}
- Volatility: {trend.volatility:.2f}
- 7-Day Prediction: {trend.prediction_7d:.2%}

ALERTS
"""
        if trend.alerts:
            for alert in trend.alerts:
                report += f"⚠️  {alert}\n"
        else:
            report += "✅ No active alerts\n"
        
        report += f"""
HISTORICAL DATA POINTS: {len(self.risk_history.get(agent_id, []))}

RECOMMENDATIONS
"""
        if trend.risk_score > 0.8:
            report += "- Immediate review required\n- Consider deactivation\n- Escalate to risk committee\n"
        elif trend.risk_score > 0.6:
            report += "- Increase monitoring frequency\n- Review control effectiveness\n- Schedule risk assessment\n"
        else:
            report += "- Continue standard monitoring\n- Regular scheduled reviews\n"
        
        return report
    
    def _categorize_risk(self, score: float) -> str:
        if score < 0.3:
            return "LOW"
        elif score < 0.6:
            return "MEDIUM"
        elif score < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"
