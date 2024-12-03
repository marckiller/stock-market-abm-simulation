from collections import deque, OrderedDict
from src.market.order import Order

import bisect
from sortedcontainers import SortedList

class PriceLevel:
    def __init__(self, price):
        self.price = price
        self.orders = OrderedDict()
        self.volume = 0

    def add_order(self, order):
        if order.order_id not in self.orders:
            self.orders[order.order_id] = order
            self.volume += order.quantity

    def remove_order(self, order_id):
        if order_id in self.orders:
            order = self.orders.pop(order_id)
            self.volume -= order.quantity
            return order
        return None

    def modify_order(self, order_id, new_quantity):

        if order_id in self.orders:
            
            order = self.orders[order_id]
            old_quantity = order.quantity
            order.quantity = new_quantity
            self.volume += (new_quantity - old_quantity)

            return order
        
        return None

    def top_order(self):
        
        if self.orders:
            return next(iter(self.orders.values()))
        return None

    def is_empty(self):
        return len(self.orders) == 0

class LimitOrderBook:

    def __init__(self):

        self.bids = {}  # Price -> PriceLevel for bids
        self.asks = {}  # Price -> PriceLevel for asks
        self.orders_by_id = {}  # Order ID -> Order

        self.sorted_bids = SortedList(key=lambda x: -x)  # Bids prices in descending order
        self.sorted_asks = SortedList()  # Asks prices in ascending order

        self.bids_total_volume = 0  # Total volume for all bid orders
        self.asks_total_volume = 0  # Total volume for all ask orders

    def add_order(self, order: Order):

        levels = self.bids if order.side == 'buy' else self.asks
        sorted_prices = self.sorted_bids if order.side == 'buy' else self.sorted_asks

        if order.price not in levels:
            levels[order.price] = PriceLevel(order.price)
            sorted_prices.add(order.price)

        levels[order.price].add_order(order)
        self.orders_by_id[order.order_id] = order

        if order.side == 'buy':
            self.bids_total_volume += order.quantity
        else:
            self.asks_total_volume += order.quantity

        return True

    def modify_order(self, order_id, new_quantity):
        """Setting quantity to 0 will remove the order from the book."""

        if order_id not in self.orders_by_id:
            return

        order = self.orders_by_id[order_id]
        levels = self.bids if order.side == 'buy' else self.asks
        price_level = levels.get(order.price)

        if not price_level:
            return

        old_quantity = order.quantity
        price_level.modify_order(order_id, new_quantity)

        if new_quantity == 0:
            sorted_prices = self.sorted_bids if order.side == 'buy' else self.sorted_asks
            self._remove_order_and_cleanup(order, levels, price_level, sorted_prices)

        else:
            if order.side == 'buy':
                self.bids_total_volume += (new_quantity - old_quantity)
            else:
                self.asks_total_volume += (new_quantity - old_quantity)

        return order

    def _remove_order_and_cleanup(self, order, levels, price_level, sorted_prices):

        removed_order = price_level.remove_order(order.order_id)

        if removed_order:
            if order.side == 'buy':
                self.bids_total_volume -= removed_order.quantity
            else:
                self.asks_total_volume -= removed_order.quantity

            if price_level.is_empty():
                del levels[order.price]
                sorted_prices.remove(order.price)

            del self.orders_by_id[order.order_id]

    def remove_order(self, order_id):
        
        if order_id not in self.orders_by_id:
            return

        order = self.orders_by_id[order_id]
        levels = self.bids if order.side == 'buy' else self.asks
        sorted_prices = self.sorted_bids if order.side == 'buy' else self.sorted_asks
        price_level = levels.get(order.price)

        if price_level:
            self._remove_order_and_cleanup(order, levels, price_level, sorted_prices)

        return order

    def get_best_bid(self):
        if self.sorted_bids:
            return self.sorted_bids[0]
        return None

    def get_best_ask(self):
        if self.sorted_asks:
            return self.sorted_asks[0]
        return None

    def top_bid(self):
        best_price = self.get_best_bid()
        if best_price is not None:
            return self.bids[best_price].top_order()
        return None

    def top_ask(self):
        best_price = self.get_best_ask()
        if best_price is not None:
            return self.asks[best_price].top_order()
        return None

    def get_orders_at_price(self, price, side):
        price_levels = self.bids if side == 'buy' else self.asks
        if price in price_levels:
            return price_levels[price].orders
        return OrderedDict()

    def get_depth(self, side):
        levels = self.bids if side == 'buy' else self.asks
        return {price: levels[price].volume for price in levels}
    
    def get_total_bid_volume(self):
        return self.bids_total_volume
    
    def get_total_ask_volume(self):
        return self.asks_total_volume
    
    def get_volume_at_price(self, price, side):
        levels = self.bids if side == 'buy' else self.asks
        if price in levels:
            return levels[price].volume
        return 0
