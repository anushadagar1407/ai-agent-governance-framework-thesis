import json
import os
from typing import Dict, Optional, List
from datetime import datetime
from framework.models import AgentRegistration, RiskLevel, AgentType


class AgentRegistry:
    def __init__(self, storage_path: str = "registry_db.json"):
        self.storage_path = storage_path
        self.agents: Dict[str, Dict] = self._load_agents()
    
    def _load_agents(self) -> Dict[str, Dict]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_agents(self):
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.agents, f, indent=2, default=str)
        except IOError as e:
            raise RuntimeError(f"Failed to save registry: {e}")
    
    def register_agent(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        purpose: str,
        tools: List[str],
        risk_level: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        try:
            registration = AgentRegistration(
                agent_id=agent_id,
                name=name,
                agent_type=agent_type,
                purpose=purpose,
                tools=tools,
                risk_level=risk_level
            )
        except Exception as e:
            raise ValueError(f"Invalid agent registration data: {e}")
        
        if agent_id in self.agents:
            raise ValueError(f"Agent with ID {agent_id} already exists")
        
        agent_data = {
            "id": agent_id,
            "name": name,
            "agent_type": agent_type,
            "purpose": purpose,
            "tools": tools,
            "risk_level": risk_level,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "metadata": metadata or {}
        }
        
        self.agents[agent_id] = agent_data
        self._save_agents()
        return agent_data
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        return self.agents.get(agent_id)
    
    def update_agent(self, agent_id: str, updates: Dict) -> Optional[Dict]:
        if agent_id not in self.agents:
            return None
        
        self.agents[agent_id].update(updates)
        self.agents[agent_id]["updated_at"] = datetime.utcnow().isoformat()
        self._save_agents()
        return self.agents[agent_id]
    
    def deactivate_agent(self, agent_id: str) -> bool:
        if agent_id not in self.agents:
            return False
        self.agents[agent_id]["status"] = "inactive"
        self.agents[agent_id]["updated_at"] = datetime.utcnow().isoformat()
        self._save_agents()
        return True
    
    def list_agents(self, status: Optional[str] = None) -> List[Dict]:
        agents = list(self.agents.values())
        if status:
            agents = [a for a in agents if a.get("status") == status]
        return agents
    
    def get_agents_by_risk(self, risk_level: str) -> List[Dict]:
        return [a for a in self.agents.values() if a.get("risk_level") == risk_level]
    
    def search_agents(self, query: str) -> List[Dict]:
        query = query.lower()
        results = []
        for agent in self.agents.values():
            if (query in agent.get("name", "").lower() or 
                query in agent.get("purpose", "").lower() or
                query in agent.get("id", "").lower()):
                results.append(agent)
        return results
