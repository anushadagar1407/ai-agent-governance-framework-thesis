class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register_agent(self, agent_id, name, agent_type, purpose, tools, risk_level):
        self.agents[agent_id] = {
            "name": name,
            "agent_type": agent_type,
            "purpose": purpose,
            "tools": tools,
            "risk_level": risk_level,
            "status": "active"
        }

    def get_agent(self, agent_id):
        return self.agents.get(agent_id)

    def list_agents(self):
        return self.agents
