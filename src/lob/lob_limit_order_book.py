from src.order.order import Order, OrderType
from src.lob.lob_price_level import PriceLevel

from typing import Dict, Optional
from src.order.order import Order, OrderStatus
from src.lob.lob_price_level import PriceLevel
from collections import defaultdict
import bisect

class LimitOrderBook:

    def __init__(self):
        self.price_levels: Dict[float, PriceLevel] = {}
        self.sorted_prices: list = []
        self.order_map: Dict[int, (PriceLevel, Order)] = {}

    def add(self, order: Order):
        pass

    def remove_by_id(self, order_id: int, status: OrderStatus):
        pass




