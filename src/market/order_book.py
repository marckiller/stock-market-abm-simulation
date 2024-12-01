from collections import deque, OrderedDict
from src.market.order import Order
from src.market.responses import LimitOrderStoredResponse, OrderCancelledResponse
import bisect
from sortedcontainers import SortedList

class PriceLevel:
    """
    Represents a single price level in the order book.
    Maintains a list of orders (FIFO) and tracks total volume at the price.
    """
    def __init__(self, price):
        self.price = price  # The price of the level
        self.orders = OrderedDict()  # order_id -> Order (FIFO order)
        self.volume = 0  # Total volume at this price level

        #If needed, # of orders can be tracked but logic is not implemented
        #self.num_orders = 0

    def add_order(self, order):
        """
        Adds a new order to the price level.

        Args:
            order (Order): The order to be added.
        """
        if order.order_id not in self.orders:
            self.orders[order.order_id] = order
            self.volume += order.quantity

    def remove_order(self, order_id):
        """
        Removes an order by its ID.

        Args:
            order_id (int): The ID of the order to be removed.

        Returns:
            Order or None: The removed order, or None if not found.
        """
        if order_id in self.orders:
            order = self.orders.pop(order_id)
            self.volume -= order.quantity
            return order
        return None

    def modify_order(self, order_id, new_quantity):
        """
        Modifies the quantity of an order.

        Args:
            order_id (int): The ID of the order to modify.
            new_quantity (int): The new quantity for the order.

        Returns:
            Order or None: The modified order, or None if not found. Order is removed if new_quantity is 0.
        """
        if order_id in self.orders:
            
            order = self.orders[order_id]
            old_quantity = order.quantity
            order.quantity = new_quantity
            self.volume += (new_quantity - old_quantity)

            if new_quantity == 0:
                return self.remove_order(order_id)
            return order
        return None

    def top_order(self):
        """
        Returns the top (oldest) order at this price level.

        Returns:
            Order or None: The top order, or None if no orders exist.
        """
        if self.orders:
            return next(iter(self.orders.values()))
        return None

    def is_empty(self):
        """
        Checks if the price level has no orders.

        Returns:
            bool: True if empty, False otherwise.
        """
        return len(self.orders) == 0


class LimitOrderBook:
    """
    Represents a limit order book, maintaining bids and asks.
    Provides functionality to add, modify, and remove orders, as well as query order book state.
    """
    def __init__(self):
        self.bids = {}  # Price -> PriceLevel for bids
        self.asks = {}  # Price -> PriceLevel for asks
        self.orders_by_id = {}  # Order ID -> Order

        self.sorted_bids = SortedList(key=lambda x: -x)  # Bids prices in descending order
        self.sorted_asks = SortedList()  # Asks prices in ascending order

        self.bids_total_volume = 0  # Total volume for all bid orders
        self.asks_total_volume = 0  # Total volume for all ask orders

    def add_order(self, order):
        """
        Adds a new order to the order book.

        Args:
            order (Order): The order to be added.

        Returns:
            LimitOrderStoredResponse: Confirmation of the added order.
        """
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

        return LimitOrderStoredResponse(order.order_id, order.agent_id, order.quantity)

    def remove_order(self, order_id):
        """
        Removes an order from the order book by its ID.

        Args:
            order_id (int): The ID of the order to be removed.

        Returns:
            OrderCancelledResponse or None: Confirmation of removal or None if order not found.
        """
        if order_id not in self.orders_by_id:
            return None
        
        order = self.orders_by_id[order_id]
        order_side = self.bids if order.side == 'buy' else self.asks
        levels = self.bids if order.side == 'buy' else self.asks
        sorted_prices = self.sorted_bids if order.side == 'buy' else self.sorted_asks

        price_level = levels.get(order.price)
        if not price_level:
            return None

        removed_order = price_level.remove_order(order_id)

        if removed_order:
            if order.side == 'buy':
                self.bids_total_volume -= removed_order.quantity
            else:
                self.asks_total_volume -= removed_order.quantity

            if price_level.is_empty():
                del levels[order.price]
                sorted_prices.remove(order.price)

        del self.orders_by_id[order_id]
        return OrderCancelledResponse(order_id, order.agent_id)

    def modify_order(self, order_id, new_quantity):
        """
        Modifies the quantity of an order in the order book.

        Args:
            order_id (int): The ID of the order to modify.
            new_quantity (int): The new quantity for the order.

        Returns:
            Order or None: The modified order, or None if not found.
        """
        if order_id not in self.orders_by_id:
            return None

        order = self.orders_by_id[order_id]
        levels = self.bids if order.side == 'buy' else self.asks
        price_level = levels.get(order.price)

        if not price_level:
            return None

        old_quantity = order.quantity
        modified_order = price_level.modify_order(order_id, new_quantity)
        
        if not modified_order:
            return None

        if order.side == 'buy':
            self.bids_total_volume += (new_quantity - old_quantity)
        else:
            self.asks_total_volume += (new_quantity - old_quantity)

        if new_quantity == 0:
            modified_order = self.remove_order(order_id)
        
        if price_level.is_empty():
            del levels[order.price]
            if order.side == 'buy':
                self.sorted_bids.remove(order.price)
            else:
                self.sorted_asks.remove(order.price)

        return modified_order

    def get_best_bid(self):
        """
        Returns the highest bid price in the order book.

        Returns:
            float or None: The highest bid price, or None if no bids exist.
        """
        if self.sorted_bids:
            return self.sorted_bids[0]
        return None

    def get_best_ask(self):
        """
        Returns the lowest ask price in the order book.

        Returns:
            float or None: The lowest ask price, or None if no asks exist.
        """
        if self.sorted_asks:
            return self.sorted_asks[0]
        return None

    def top_bid(self):
        """
        Returns the top (oldest) bid order at the highest bid price.

        Returns:
            Order or None: The top bid order, or None if no bids exist.
        """
        best_price = self.get_best_bid()
        if best_price is not None:
            return self.bids[best_price].top_order()
        return None

    def top_ask(self):
        """
        Returns the top (oldest) ask order at the lowest ask price.

        Returns:
            Order or None: The top ask order, or None if no asks exist.
        """
        best_price = self.get_best_ask()
        if best_price is not None:
            return self.asks[best_price].top_order()
        return None

    def get_orders_at_price(self, price, side):
        """
        Returns all orders at a specific price level.

        Args:
            price (float): The price level to query.
            side (str): 'buy' or 'sell' to specify side of the book.

        Returns:
            OrderedDict: A dictionary of order_id -> Order at the price level.
        """
        price_levels = self.bids if side == 'buy' else self.asks
        if price in price_levels:
            return price_levels[price].orders
        return OrderedDict()

    def get_depth(self, side):
        """
        Returns the depth (volume) of the order book.

        Args:
            side (str): 'buy' or 'sell' to specify side of the book.

        Returns:
            dict: A dictionary of price -> volume for all price levels on the given side.
        """
        levels = self.bids if side == 'buy' else self.asks
        return {price: levels[price].volume for price in levels}
    
    def get_total_bid_volume(self):
        """
        Returns the total volume of all bid orders.

        Returns:
            int: The total volume of all bid orders.
        """
        return self.bids_total_volume
    
    def get_total_ask_volume(self):
        """
        Returns the total volume of all ask orders.

        Returns:
            int: The total volume of all ask orders.
        """
        return self.asks_total_volume
