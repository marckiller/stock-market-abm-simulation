from enum import Enum

class RequestType(Enum):

    LIMIT_SELL = 1
    LIMIT_BUY = 2
    MARKET_SELL = 3
    MARKET_BUY = 4
    CANCEL = 5
