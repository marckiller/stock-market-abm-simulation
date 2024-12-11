from src.market.market import Market

from src.agents.agents.zero_intelligence_agent import ZeroIntelligenceAgent
from src.agents.agents.fundamentalist_agent import FundamentalistAgent
from src.agents.agents.chartist_agent import ChartistAgent

class Simulation:
    def __init__(self, config):
        self.config = config
        self.current_time = 0

        self.market = Market(config["market"])
        
        for agent_config in config["agents"]:
            agent = self.create_agent(agent_config)
            self.market.register_agent(agent)

        self.time_step = config.get("time_step", 1)
        self.max_time = config.get("max_time", 100)

    def create_agent(self, agent_config):

        if agent_config["type"] == "zero_intelligence":
            return ZeroIntelligenceAgent(
                agent_id=agent_config["id"],
                initial_cash=agent_config["cash"],
                market=self.market,
                max_order_size=agent_config["max_order_size"],
                limit_order_rate=agent_config["limit_order_rate"],
                market_order_rate=agent_config["market_order_rate"],
                cancellation_rate=agent_config["cancellation_rate"],
                activation_rate=agent_config["activation_rate"]
            )
        
        if agent_config["type"] == "fundamentalist":
            return FundamentalistAgent(
                agent_id=agent_config["id"],
                initial_cash=agent_config["cash"],
                market=self.market,
                fundamental_value=agent_config["fundamental_value"],
                activation_rate=agent_config["activation_rate"],
                max_order_size=agent_config["max_order_size"]
            )
        elif agent_config["type"] == "chartist":
            return ChartistAgent(
                agent_id=agent_config["id"],
                initial_cash=agent_config["cash"],
                market=self.market,
                activation_rate=agent_config["activation_rate"],
                max_order_size=agent_config["max_order_size"],
                window=agent_config["window"]
            )

        else:
                raise ValueError(f"Unknown agent type: {agent_config['type']}")

    def run(self):
        while self.market.agent_manager.time_queue:
            next_time = self.market.agent_manager.time_queue[0][0]
            if next_time > self.max_time:
                break

            self.current_time = next_time
            self.market.time = self.current_time

            if self.current_time % 1000 == 0:
                print(f"Time: {self.current_time} ({self.current_time / self.max_time:.2%})")

            self.market.agent_manager.step(self.current_time)

        print("END OF SIMULATION")

    def get_agent_stats(self):
        stats = []
        for agent_id, agent in self.market.agent_manager.agents.items():
            stats.append({
                "agent_id": agent_id,
                "cash": agent.cash,
                "holdings": agent.holdings,
                "total_value": agent.get_total_value(self.market.market_data.mid_price)
            })
        return stats
