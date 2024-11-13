from typing import Dict, Optional, List, Tuple
import bisect

from src.order.order import OrderSide
from src.order.order_limit import OrderLimit
from src.lob.lob_price_level import PriceLevel

from src.event.event import Event
from src.event.events.event_order_added import EventOrderAdded
from src.event.events.event_order_removed import EventOrderRemoved

class LimitOrderBook:

    def __init__(self):
        self.bids: Dict[float, PriceLevel] = {}
        self.asks: Dict[float, PriceLevel] = {}

        self.sorted_bids: List[float] = [] #negative prices for bids
        self.sorted_asks: List[float] = []

        self.order_map: Dict[int, Tuple[PriceLevel, OrderLimit]] = {}
        
        self.last_popped_order_id = None

    def add_bid(self, order: OrderLimit, timestamp: int, trigger_event_id: int) -> List[Event]:

        if order.side!= OrderSide.BUY:
            raise ValueError("Order side must be BUY")
        
        price = -order.price #negative for bids so that they are sorted in descending order

        if price not in self.bids:
            self.bids[price] = PriceLevel(price)
            bisect.insort(self.sorted_bids, price)

        if order.order_id == self.last_popped_order_id:
            self.bids[price].add_to_front(order)
        else:
            self.bids[price].add(order)
        
        self.last_popped_order_id = None
        self.order_map[order.order_id] = (self.bids[price], order)
        return [EventOrderAdded(timestamp=timestamp, trigger_event_id=trigger_event_id, ticker=order.ticker, order_id = order.order_id)]
    
    def add_ask(self, order: OrderLimit, timestamp: int, trigger_event_id: int) -> List[Event]:

        if order.side!= OrderSide.SELL:
            raise ValueError("Order side must be SELL")
        
        price = order.price

        if price not in self.asks:
            self.asks[price] = PriceLevel(price)
            bisect.insort(self.sorted_asks, price)

        if order.order_id == self.last_popped_order_id:
            self.asks[price].add_to_front(order)
        else:
            self.asks[price].add(order)
        
        self.last_popped_order_id = None
        self.order_map[order.order_id] = (self.asks[price], order)
        return [EventOrderAdded(timestamp=timestamp, trigger_event_id=trigger_event_id, ticker=order.ticker, order_id = order.order_id)]
    
    def best_ask(self) -> Optional[float]:
        while self.sorted_asks:
            best_price = self.sorted_asks[0]
            if best_price in self.asks:
                return best_price
            self.sorted_asks.pop(0)
        return None

    def best_bid(self) -> Optional[float]:
        while self.sorted_bids:
            best_price = -self.sorted_bids[0]
            if -best_price in self.bids:
                return best_price
            self.sorted_bids.pop(0)
        return None
    
    def get_price_level_volume(self, price: float, side: OrderSide) -> int:
        if side == OrderSide.BUY:
            price_level = self.bids.get(-price)
        else:
            price_level = self.asks.get(price)
        
        if price_level is not None:
            return price_level.volume
        return 0
    
    def pop_top_ask_at_price(self, price: float, timestamp: int, trigger_event_id: int) -> Tuple[OrderLimit, List[Event]]:
        price_level = self.asks[price]
        order = price_level.pop_first_order()

        if price_level.is_empty():
            del self.asks[price]
            self.sorted_asks.remove(price)

        del self.order_map[order.order_id]
        return order, [EventOrderRemoved(timestamp=timestamp, trigger_event_id=trigger_event_id, ticker=order.ticker, order_id = order.order_id)]
    
    def remove_order_by_id(self, order_id: int, timestamp: int, trigger_event_id: int) -> List[Event]:
        try:
            price_level, order = self.order_map[order_id]
            price_level.remove(order)
            del self.order_map[order_id]

            if price_level.is_empty():
                if order.side == OrderSide.BUY:
                    del self.bids[-price_level.price]
                    self.sorted_bids.remove(-price_level.price)
                else:
                    del self.asks[price_level.price]
                    self.sorted_asks.remove(price_level.price)
            return [EventOrderRemoved(timestamp=timestamp, trigger_event_id=trigger_event_id, ticker=order.ticker, order_id = order.order_id)]
        
        except KeyError:
            raise ValueError(f"No Order with id {order_id} in the book")