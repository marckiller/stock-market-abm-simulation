#limit order book
from src.lob.lob_limit_order_book import LimitOrderBook
from src.lob.lob_matching_engine import MatchingEngine

#orders
from src.order.order import Order

#agents
from src.agents.agent_agent import AbstractAgent

#events
from src.event.event import Event
from src.event.events.event_ticker_added import EventTickerAdded
from src.event.events.event_agent_registered import EventAgentRegistered
from src.event.events.event_order_executed import EventOrderExecuted

from src.event.event_types import EventType
from src.event.events.event_order_added import EventOrderAdded

#other market components
from src.market.market_data import MarketData

class Market:

    def __init__(self):
        self.matching_engine = MatchingEngine()

        self.instruments = {}#ticker: LimitOrderBook
        self.market_data = MarketData(['AAPL'], [10])
        
        self.agents = {}#id: agent

    def add_instrument(self, ticker: str, timestamp: int, trigger_event_id: int) -> list[Event]:

        if ticker in self.instruments:
            raise ValueError(f"Instrument {ticker} already exists.")
        
        self.instruments[ticker] = LimitOrderBook()
        return [EventTickerAdded(timestamp, trigger_event_id, ticker)]
    
    def add_agent(self, agent: AbstractAgent, timestamp: int, trigger_event_id: int) -> list[Event]:

        if agent.id in self.agents:
            raise ValueError(f"Agent {agent.id} already exists.")
        
        self.agents[agent.id] = agent
        return [EventAgentRegistered(timestamp, trigger_event_id, agent.id)]
    
    def execute_order(self, order: Order, timestamp: int, trigger_event_id: int) -> list[Event]:

        if order.ticker not in self.instruments:
            raise ValueError(f"Instrument {order.ticker} does not exist.")
        
        events = self.matching_engine.process_order(order, self.instruments[order.ticker], timestamp, trigger_event_id)

        for event in events:
            
            #adding pending orders to agents portfolio if order is stored in the lob
            if event.type == EventType.ORDER_ADDED:
                #do it only if the order was active order and not one that was already in a book
                if event.order_id == order.order_id:
                    self.agents[order.agent_id].add_pending_order(order)
            
            #removing pending orders from agents portfolio if order is removed from the lob
            elif event.type == EventType.ORDER_EXECUTED:
                #do it when the order was executed but not active (those are not in the portfolio)
                if event.order_id != order.order_id:
                    self.agents[event.agent_id].remove_pending_order(event.order_id)

            elif event.type == EventType.ORDER_MODIFIED:
                pass

        return events

    def cancel_order(self, order_id: int, ticker: str, timestamp: int, trigger_event_id: int) -> list[Event]:
        if ticker not in self.instruments:
            raise ValueError(f"Instrument {ticker} does not exist.")
        
        return self.instruments[ticker].remove_order_by_id(order_id, timestamp, trigger_event_id)


