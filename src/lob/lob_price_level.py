from collections import deque
from typing import Deque, Optional, Iterator
from src.order.order import OrderType
from src.order.order_limit import OrderLimit

class PriceLevel:
    def __init__(self, price: float):
        self.number_of_orders = 0
        self.volume = 0
        self.price = price
        self.orders: Deque[OrderLimit] = deque()

    def add(self, order: OrderLimit):
        if order.type != OrderType.LIMIT:
            raise ValueError("PriceLevel accepts only LIMIT orders")
        if order.price != self.price:
            raise ValueError("PriceLevel accepts only orders with the same price")

        self.orders.append(order)
        self.number_of_orders += 1
        self.volume += order.quantity

    def add_to_front(self, order: OrderLimit):
        if order.type != OrderType.LIMIT:
            raise ValueError("PriceLevel accepts only LIMIT orders")
        if order.price != self.price:
            raise ValueError("PriceLevel accepts only orders with the same price")

        self.orders.appendleft(order)
        self.number_of_orders += 1
        self.volume += order.quantity

    def remove(self, order: OrderLimit) -> OrderLimit:
        try:
            self.orders.remove(order)
            self.number_of_orders -= 1
            self.volume -= order.quantity
            return order
        except ValueError:
            raise ValueError(f"No Order with id {order.order_id} in PriceLevel {self.price}")

    def get_first(self) -> Optional[OrderLimit]:
        try:
            return self.orders[0]
        except IndexError:
            return None

    def pop_first_order(self) -> Optional[OrderLimit]:
        if not self.orders:
            return None

        order = self.orders.popleft()
        self.number_of_orders -= 1
        self.volume -= order.quantity
        return order

    def is_empty(self) -> bool:
        return not bool(self.orders)

    def __iter__(self) -> Iterator[OrderLimit]:
        return iter(self.orders)

    def __len__(self) -> int:
        return self.number_of_orders

    def __repr__(self) -> str:
        return f"PriceLevel(price={self.price}, orders={len(self.orders)}, volume={self.volume})"

    def get_volume(self) -> int:
        return self.volume