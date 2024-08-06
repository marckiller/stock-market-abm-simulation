from enum import Enum

class OrderType(Enum):

    ABSTRACT_ORDER = 0
    LIMIT = 1
    MARKET = 2