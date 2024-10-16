from enum import Enum, auto

class EventType(Enum):

    #Simulation: executable events
    SIMULATION_START = auto()
    SIMULATION_END = auto()
    AGENT_ACTION = auto()

    #Simulation: non-executable events
    AGENT_ACTION_REJECTED = auto()
    AGENT_ACTION_ACCEPTED = auto()
    
    #Limit order book: executable events
    LIMIT_BUY_ORDER = auto()
    LIMIT_SELL_ORDER = auto()
    MARKET_BUY_ORDER = auto()
    MARKET_SELL_ORDER = auto()
    CANCEL_ORDER = auto()
    EXPIRE_ORDER = auto() 

    #Limit order book: non-executable events
    ORDER_ADDED = auto()
    ORDER_REMOVED = auto()
    ORDER_MODIFIED = auto()
    ORDER_CANCELED = auto()
    ORDER_EXECUTED = auto()
    ORDER_REJECTED = auto()
    TRANSACTION = auto()

    #Market: executable events
    ADD_AGENT = auto()
    REMOVE_AGENT = auto()
    ADD_TICKER = auto()
    REMOVE_TICKER = auto()
    
    #Market: non-executable events
    AGENT_ADDED = auto()
    AGENT_REMOVED = auto()
    TICKER_ADDED = auto()
    TICKER_REMOVED = auto()
    AGENT_ORDER = auto()
    AGENT_TRADE = auto()

    #AbstractEvent type
    ABSTRACT_EVENT = 0