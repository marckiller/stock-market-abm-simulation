import heapq
from src.agents.agent_time_activated import TimeActivatedAgent
from src.agents.agent_condition_activated import ConditionActivatedAgent

class AgentManager:
    def __init__(self, market, indicator_manager):
        self.market = market
        self.indicator_manager = indicator_manager
        self.agents = {}
        self.time_queue = []
        self.condition_agents = []

    def register_agent(self, agent):
        self.agents[agent.agent_id] = agent

        if isinstance(agent, TimeActivatedAgent):
            heapq.heappush(self.time_queue, (agent.next_activation_time, agent.agent_id))
            
        elif isinstance(agent, ConditionActivatedAgent):
            self.condition_agents.append(agent)

    def activate_time_agents(self, current_time):
        while self.time_queue and self.time_queue[0][0] <= current_time:
            _, agent_id = heapq.heappop(self.time_queue)
            agent = self.agents.get(agent_id)
            if agent and agent.active:
                agent.activate(current_time)
                heapq.heappush(self.time_queue, (agent.next_activation_time, agent_id))

    def activate_condition_agents(self, current_time):
        for agent in self.condition_agents:
            if agent.active:
                agent.check_condition_and_activate(current_time)

    def step(self, current_time):
        self.activate_time_agents(current_time)
        self.activate_condition_agents(current_time)