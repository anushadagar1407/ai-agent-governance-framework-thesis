import asyncio
import json
import time
from typing import Dict, List, Callable, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import deque
import threading

@dataclass
class MetricEvent:
    timestamp: str
    agent_id: str
    metric_type: str
    value: float
    threshold: float
    status: str  # "normal", "warning", "critical"
    context: Dict

class RealtimeMonitor:
    def __init__(self, window_size: int = 1000):
        self.event_buffer: deque = deque(maxlen=window_size)
        self.alert_handlers: List[Callable] = []
        self.metric_thresholds: Dict[str, Dict] = {}
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.subscribers: Set[str] = set()
        self.anomaly_detector = AnomalyDetector()
        
        # Default thresholds
        self._set_default_thresholds()
    
    def _set_default_thresholds(self):
        self.metric_thresholds = {
            "response_time_ms": {"warning": 500, "critical": 2000},
            "error_rate": {"warning": 0.05, "critical": 0.15},
            "cpu_usage": {"warning": 70, "critical": 90},
            "memory_usage": {"warning": 80, "critical": 95},
            "api_calls_per_min": {"warning": 1000, "critical": 5000},
            "failed_governance_checks": {"warning": 1, "critical": 3}
        }
    
    def subscribe(self, agent_id: str):
        """Subscribe an agent to monitoring"""
        self.subscribers.add(agent_id)
    
    def unsubscribe(self, agent_id: str):
        """Unsubscribe an agent from monitoring"""
        self.subscribers.discard(agent_id)
    
    def record_metric(self, agent_id: str, metric_type: str, 
                     value: float, context: Optional[Dict] = None):
        """Record a real-time metric"""
        if agent_id not in self.subscribers:
            return
        
        thresholds = self.metric_thresholds.get(metric_type, 
                                               {"warning": float('inf'), "critical": float('inf')})
        
        # Determine status
        if value >= thresholds["critical"]:
            status = "critical"
        elif value >= thresholds["warning"]:
            status = "warning"
        else:
            status = "normal"
        
        event = MetricEvent(
            timestamp=datetime.utcnow().isoformat(),
            agent_id=agent_id,
            metric_type=metric_type,
            value=value,
            threshold=thresholds["warning"],
            status=status,
            context=context or {}
        )
        
        self.event_buffer.append(event)
        
        # Check for anomalies
        if self.anomaly_detector.is_anomaly(agent_id, metric_type, value):
            self._trigger_alert(event, is_anomaly=True)
        
        # Trigger alert if critical or warning
        if status in ["critical", "warning"]:
            self._trigger_alert(event)
    
    def _trigger_alert(self, event: MetricEvent, is_anomaly: bool = False):
        """Trigger all registered alert handlers"""
        alert_data = asdict(event)
        alert_data["is_anomaly"] = is_anomaly
        
        for handler in self.alert_handlers:
            try:
                handler(alert_data)
            except Exception as e:
                print(f"Alert handler error: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add an alert handler callback"""
        self.alert_handlers.append(handler)
    
    def get_agent_metrics(self, agent_id: str, metric_type: Optional[str] = None,
                         last_n: int = 100) -> List[MetricEvent]:
        """Get recent metrics for an agent"""
        results = []
        for event in reversed(self.event_buffer):
            if event.agent_id == agent_id:
                if metric_type is None or event.metric_type == metric_type:
                    results.append(event)
                if len(results) >= last_n:
                    break
        return results
    
    def get_aggregated_stats(self, agent_id: str, 
                            metric_type: str,
                            window_minutes: int = 5) -> Dict:
        """Get aggregated statistics for a metric"""
        cutoff = datetime.utcnow().timestamp() - (window_minutes * 60)
        values = []
        
        for event in self.event_buffer:
            event_time = datetime.fromisoformat(event.timestamp).timestamp()
            if (event.agent_id == agent_id and 
                event.metric_type == metric_type and 
                event_time > cutoff):
                values.append(event.value)
        
        if not values:
            return {"count": 0, "avg": 0, "min": 0, "max": 0, "status": "no_data"}
        
        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "current": values[-1],
            "status": "active"
        }
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Start background monitoring thread"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self, interval: int):
        """Background monitoring loop"""
        while self.running:
            self._check_health()
            time.sleep(interval)
    
    def _check_health(self):
        """Periodic health check"""
        for agent_id in self.subscribers:
            # Check if agent has recent metrics
            recent = self.get_agent_metrics(agent_id, last_n=1)
            if not recent:
                # No recent metrics - agent might be down
                self._trigger_alert(MetricEvent(
                    timestamp=datetime.utcnow().isoformat(),
                    agent_id=agent_id,
                    metric_type="heartbeat",
                    value=0,
                    threshold=1,
                    status="critical",
                    context={"reason": "no_heartbeat"}
                ))
    
    def export_metrics(self, filepath: str):
        """Export all metrics to JSON"""
        data = [asdict(event) for event in self.event_buffer]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_dashboard_data(self) -> Dict:
        """Get data for real-time dashboard"""
        # Aggregate by agent and metric type
        agent_stats = {}
        
        for event in self.event_buffer:
            aid = event.agent_id
            if aid not in agent_stats:
                agent_stats[aid] = {
                    "metrics": {},
                    "latest_event": None,
                    "alert_count": 0
                }
            
            if event.status in ["warning", "critical"]:
                agent_stats[aid]["alert_count"] += 1
            
            agent_stats[aid]["metrics"][event.metric_type] = {
                "value": event.value,
                "status": event.status,
                "timestamp": event.timestamp
            }
            agent_stats[aid]["latest_event"] = event.timestamp
        
        return {
            "total_subscribers": len(self.subscribers),
            "total_events": len(self.event_buffer),
            "agent_stats": agent_stats,
            "timestamp": datetime.utcnow().isoformat()
        }


class AnomalyDetector:
    """Simple anomaly detection using statistical methods"""
    
    def __init__(self, window_size: int = 100):
        self.history: Dict[str, List[float]] = {}
        self.window_size = window_size
    
    def is_anomaly(self, agent_id: str, metric_type: str, 
                   value: float, threshold_std: float = 3.0) -> bool:
        """Detect if value is anomalous based on historical data"""
        key = f"{agent_id}:{metric_type}"
        
        if key not in self.history:
            self.history[key] = []
        
        history = self.history[key]
        
        # Need minimum data points
        if len(history) < 10:
            self.history[key].append(value)
            return False
        
        import statistics
        mean = statistics.mean(history)
        std = statistics.stdev(history) if len(history) > 1 else 0
        
        # Z-score based anomaly detection
        if std == 0:
            is_anomaly = abs(value - mean) > 0.01
        else:
            z_score = abs(value - mean) / std
            is_anomaly = z_score > threshold_std
        
        # Update history
        self.history[key].append(value)
        if len(self.history[key]) > self.window_size:
            self.history[key].pop(0)
        
        return is_anomaly
