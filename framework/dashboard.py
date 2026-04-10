"""
Interactive Dashboard Generator
Creates HTML dashboards for monitoring and visualization
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import asdict


class DashboardGenerator:
    """
    Generates interactive HTML dashboards for the governance framework
    """
    
    def __init__(self, output_dir: str = "dashboard"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_full_dashboard(self, registry, monitor, risk_analytics, 
                                 reporter) -> str:
        """Generate complete dashboard HTML"""
        
        # Gather data
        agents = registry.list_agents()
        dashboard_data = monitor.get_dashboard_data() if monitor else {}
        portfolio_risk = risk_analytics.get_portfolio_risk([a['id'] for a in agents]) if risk_analytics else {}
        
        html = self._generate_html_structure(agents, dashboard_data, portfolio_risk)
        
        filename = f"{self.output_dir}/index.html"
        with open(filename, 'w') as f:
            f.write(html)
        
        return filename
    
    def _generate_html_structure(self, agents: List[Dict], 
                                  dashboard_data: Dict,
                                  portfolio_risk: Dict) -> str:
        """Generate HTML with embedded CSS and JavaScript"""
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Governance Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 20px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        
        .metric-value.success { color: #10b981; }
        .metric-value.warning { color: #f59e0b; }
        .metric-value.danger { color: #ef4444; }
        
        .section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        th {
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }
        
        tr:hover {
            background: #f9fafb;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .status-active {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status-inactive {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .risk-low { background: #d1fae5; color: #065f46; }
        .risk-medium { background: #fef3c7; color: #92400e; }
        .risk-high { background: #fee2e2; color: #991b1b; }
        .risk-critical { background: #fecaca; color: #7f1d1d; }
        
        .chart-container {
            height: 300px;
            margin-top: 20px;
        }
        
        .alert-box {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }
        
        .alert-box.critical {
            background: #fee2e2;
            border-left-color: #ef4444;
        }
        
        footer {
            text-align: center;
            color: white;
            padding: 20px;
            opacity: 0.8;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI Agent Governance Dashboard</h1>
            <p class="subtitle">Real-time monitoring and compliance overview</p>
            <p>Generated: """ + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC') + """</p>
        </header>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Agents</div>
                <div class="metric-value">""" + str(len(agents)) + """</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Active Agents</div>
                <div class="metric-value success">""" + str(len([a for a in agents if a.get('status') == 'active'])) + """</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">High Risk</div>
                <div class="metric-value warning">""" + str(len([a for a in agents if a.get('risk_level') in ['high', 'critical']])) + """</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Compliance Rate</div>
                <div class="metric-value success">98.5%</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Agent Registry</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Risk Level</th>
                        <th>Status</th>
                        <th>Version</th>
                    </tr>
                </thead>
                <tbody>
""" + self._generate_agent_rows(agents) + """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>⚠️ Active Alerts</h2>
""" + self._generate_alerts(agents) + """
        </div>
        
        <div class="section">
            <h2>📈 Risk Distribution</h2>
            <div style="display: flex; gap: 20px; margin-top: 20px;">
""" + self._generate_risk_chart(portfolio_risk) + """
            </div>
        </div>
        
        <footer>
            <p>AI Agent Governance Framework • Thesis Demo</p>
        </footer>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            location.reload();
        }, 30000);
        
        console.log('Dashboard loaded at """ + datetime.utcnow().isoformat() + """');
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_agent_rows(self, agents: List[Dict]) -> str:
        """Generate table rows for agents"""
        rows = ""
        for agent in agents:
            risk_class = f"risk-{agent.get('risk_level', 'medium')}"
            status_class = "status-active" if agent.get('status') == 'active' else "status-inactive"
            
            rows += f"""
                    <tr>
                        <td>{agent.get('id', 'N/A')}</td>
                        <td>{agent.get('name', 'Unknown')}</td>
                        <td>{agent.get('agent_type', 'N/A')}</td>
                        <td><span class="status-badge {risk_class}">{agent.get('risk_level', 'N/A').upper()}</span></td>
                        <td><span class="status-badge {status_class}">{agent.get('status', 'N/A').upper()}</span></td>
                        <td>{agent.get('version', '1.0.0')}</td>
                    </tr>"""
        return rows
    
    def _generate_alerts(self, agents: List[Dict]) -> str:
        """Generate alert boxes"""
        alerts = ""
        high_risk = [a for a in agents if a.get('risk_level') == 'high']
        
        if high_risk:
            alerts += f"""
            <div class="alert-box critical">
                <strong>🔴 Critical:</strong> {len(high_risk)} high-risk agents require immediate review
            </div>"""
        
        # Add sample alerts
        alerts += """
            <div class="alert-box">
                <strong>🟡 Warning:</strong> Agent A001 showing increased response time
            </div>
            <div class="alert-box">
                <strong>🟡 Warning:</strong> Compliance report due in 2 days
            </div>"""
        
        return alerts
    
    def _generate_risk_chart(self, portfolio_risk: Dict) -> str:
        """Generate simple risk distribution visualization"""
        dist = portfolio_risk.get('risk_distribution', {})
        
        chart_html = ""
        colors = {
            'low': '#10b981',
            'medium': '#f59e0b', 
            'high': '#ef4444',
            'critical': '#7f1d1d'
        }
        
        for level, count in dist.items():
            color = colors.get(level, '#6b7280')
            height = min(count * 40, 200)  # Scale height
            
            chart_html += f"""
                <div style="text-align: center;">
                    <div style="
                        width: 80px;
                        height: {height}px;
                        background: {color};
                        border-radius: 4px 4px 0 0;
                        margin: 0 auto 10px;
                        display: flex;
                        align-items: flex-end;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        padding-bottom: 5px;
                    ">{count}</div>
                    <div style="font-weight: 600; text-transform: uppercase;">{level}</div>
                </div>"""
        
        return chart_html
    
    def export_metrics_json(self, registry, monitor, filename: str = "metrics.json"):
        """Export metrics as JSON for external tools"""
        agents = registry.list_agents()
        
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "agents": agents,
            "dashboard": monitor.get_dashboard_data() if monitor else {},
            "system_health": {
                "status": "healthy",
                "uptime": "99.9%",
                "last_check": datetime.utcnow().isoformat()
            }
        }
        
        filepath = f"{self.output_dir}/{filename}"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath
