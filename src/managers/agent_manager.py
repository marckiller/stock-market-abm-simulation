import heapq
from src.agents.agent_time_activated import TimeActivatedAgent
from src.agents.agent_condition_activated import ConditionActivatedAgent

from src.market.transaction import Transaction

class AgentManager:
    def __init__(self, market, market_data_manager, indicator_manager):
        self.market = market
        self.market_data_manager = market_data_manager
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

    def get_agent(self, agent_id):
        return self.agents.get(agent_id)

    #handing events that effect agents assets

    def handle_transaction(self, transaciton: Transaction):
        """money and holdings transfer between buyer and seller"""

        buyer = self.get_agent(transaciton.buyer_id)
        seller = self.get_agent(transaciton.seller_id)

        if buyer:
            buyer.deduct_cash(transaction.price * transaction.quantity)
            buyer.add_holdings(transaction.quantity)

        if seller:
            seller.add_cash(transaction.price * transaction.quantity)
            seller.deduct_holdings(transaction.quantity)

    def handle_order_executed(self, order_id, order_type, executed_quantity):

        #TODO: 
        agent = self.get_agent(order_id)
        if agent:
            order = agent.pending_limit_orders.get(order_id)
            if order:
                if order.quantity == 0:
                    agent.remove_pending_limit_order(order_id)
    
    def handle_order_stored(self, order):
        agent = self.get_agent(order.agent_id)
        if agent:
            agent.pending_limit_orders[order.order_id] = order

