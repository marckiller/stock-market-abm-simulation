from typing import Dict, Optional, List, Tuple
import bisect

from src.order.order import Order, OrderType, OrderStatus, OrderSide
from src.order.order_limit import OrderLimit
from src.lob.lob_price_level import PriceLevel

class LimitOrderBook:

    def __init__(self):
        self.bids: Dict[float, PriceLevel] = {}
        self.asks: Dict[float, PriceLevel] = {}

        self.sorted_bids: List[float] = [] #negative prices for bids
        self.sorted_asks: List[float] = []

        self.order_map: Dict[int, Tuple[PriceLevel, OrderLimit]] = {}

    def add(self, order: OrderLimit):
        if order.type != OrderType.LIMIT:
            raise ValueError("LimitOrderBook accepts only LIMIT orders")
        
        if order.side == OrderSide.BUY:
            price = -order.price #negative prices for bids
            target_side = self.bids
            sorted_prices = self.sorted_bids
        else:
            price = order.price
            target_side = self.asks
            sorted_prices = self.sorted_asks

        if price not in target_side:
            target_side[price] = PriceLevel(order.price)
            bisect.insort_left(sorted_prices, price)

        target_side[price].add(order)
        self.order_map[order.order_id] = (target_side[price], order)

    def best_bid(self) -> Optional[float]:
        if self.sorted_bids:
            #returning negative price for bids
            return -self.sorted_bids[0]
        return None

    def best_ask(self) -> Optional[float]:
        return self.sorted_asks[0] if self.sorted_asks else None

    def get_price_level_volume(self, price: float, side: OrderSide) -> Optional[int]:
        if side == OrderSide.BUY:
            target_side = self.bids
            price_key = -price
        else:
            target_side = self.asks
            price_key = price

        if price_key in target_side:
            return target_side[price_key].volume
        return 0

    def pop_orders_from_given_price_level_to_meet_demand(self, price: float, side: OrderSide, demand: int) -> List[Tuple[OrderLimit, int]]:
        if side == OrderSide.BUY:
            target_side = self.bids
            sorted_prices = self.sorted_bids
            price_key = -price 
        else:
            target_side = self.asks
            sorted_prices = self.sorted_asks
            price_key = price

        if price_key in target_side:
            price_level = target_side[price_key]
            orders = price_level.pop_orders_to_meet_demand(demand)

            #Remove orders from maps 
            for order, _ in orders:
                if order.order_id in self.order_map:
                    del self.order_map[order.order_id]

            #If price level is empty and there is no expected partial order, remove it from the book
            if price_level.is_empty() and price_level.last_partial_order_id is None:
                del target_side[price_key]
                sorted_prices.remove(price_key)

            return orders
        return []

    def remove_order_by_id(self, order_id: int) -> None:
        try:
            price_level, order = self.order_map[order_id]
            price_level.remove(order)
            del self.order_map[order_id]

            if price_level.is_empty():
                if order.side == OrderSide.BUY:
                    price_key = -price_level.price
                    del self.bids[price_key]
                    self.sorted_bids.remove(price_key)
                else:
                    price_key = price_level.price
                    del self.asks[price_key]
                    self.sorted_asks.remove(price_key)
        except KeyError:
            raise ValueError(f"No Order with id {order_id} in LimitOrderBook")

    def get_order(self, order_id: int) -> Optional[OrderLimit]:
        """Pobiera zlecenie z order_map na podstawie order_id."""
        entry = self.order_map.get(order_id)
        if entry:
            _, order = entry
            return order
        return None

    def __repr__(self):
        return f"LimitOrderBook(bids={len(self.bids)}, asks={len(self.asks)})"
