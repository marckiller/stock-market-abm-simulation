from enum import Enum, auto

class AgentTypes(Enum):

    MARKET_MAKER = auto()
    MARKET_TAKER = auto()
    NOISE = auto()
    CHARTIST = auto()
    FUNDAMENTALIST = auto()