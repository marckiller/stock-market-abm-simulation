from src.market.market_market import Market
from src.event.event import Event
from src.agents.agent_agent import AbstractAgent

class Simulation:

    def __init__(self, config):

        self.config = config
        self.market = Market()
        self.time = 0
        self.agents = {}#id: agent
        self.market_data = {}#ticker: InstrumentData

    def add_agent(self, agent_id: int, agent) -> list[Event]:
        pass

    def add_ticker(self, ticker: str) -> list[Event]:
        pass

    def add_agent_to_market(self) -> list[Event]:
        pass

    def agent_action(self, agent_id: int) -> list[Event]:
        pass

    def get_agent(self, agent_id: int) -> AbstractAgent:
        pass

    def set_time(self, time: int):
        pass




