import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional


class AuditLogger:
    def __init__(self, log_file: str = "audit_log.json"):
        self.log_file = log_file
        self.logs: List[Dict] = self._load_logs()
    
    def _load_logs(self) -> List[Dict]:
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def _save_logs(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2, default=str)
    
    def _compute_hash(self, entry: Dict) -> str:
        entry_str = json.dumps(entry, sort_keys=True, default=str)
        return hashlib.sha256(entry_str.encode()).hexdigest()
    
    def log_event(self, event_type: str, agent_id: str, details: Dict) -> Dict:
        previous_hash = self.logs[-1]["entry_hash"] if self.logs else "0"
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
            "previous_hash": previous_hash
        }
        
        entry["entry_hash"] = self._compute_hash(entry)
        self.logs.append(entry)
        self._save_logs()
        return entry
    
    def get_agent_history(self, agent_id: str) -> List[Dict]:
        return [log for log in self.logs if log.get("agent_id") == agent_id]
    
    def verify_integrity(self) -> bool:
        for i, log in enumerate(self.logs):
            if i == 0:
                continue
            if log.get("previous_hash") != self.logs[i-1].get("entry_hash"):
                return False
            test_entry = log.copy()
            test_entry.pop("entry_hash")
            computed = self._compute_hash(test_entry)
            if computed != log.get("entry_hash"):
                return False
        return True
