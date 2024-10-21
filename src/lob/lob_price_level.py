from collections import deque
from typing import Deque, Optional, Iterator, List, Tuple
from src.order.order import OrderType
from src.order.order_limit import OrderLimit

class PriceLevel:
    def __init__(self, price: float):
        self.number_of_orders = 0
        self.volume = 0
        self.price = price
        self.orders: Deque[OrderLimit] = deque()
        self.last_partial_order_id: Optional[int] = None

    def add(self, order: OrderLimit):
        if order.type != OrderType.LIMIT:
            raise ValueError("PriceLevel accepts only LIMIT orders")
        if order.price != self.price:
            raise ValueError("PriceLevel accepts only orders with the same price")

        if order.order_id == self.last_partial_order_id:
            self.orders.appendleft(order)
            
        else:
            self.orders.append(order)

        self.last_partial_order_id = None #give only 'one chance' for partial order to go back

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

    def is_empty(self) -> bool:
        return not bool(self.orders)

    def __iter__(self) -> Iterator[OrderLimit]:
        return iter(self.orders)

    def __len__(self) -> int:
        return self.number_of_orders

    def __repr__(self) -> str:
        return f"PriceLevel(price={self.price}, orders={len(self.orders)}, volume={self.volume})"

    def pop_orders_to_meet_demand(self, demand: int) -> List[Tuple[OrderLimit, int]]:
        fulfilled_orders = []
        remaining_demand = demand

        while self.orders and remaining_demand > 0:
            order = self.orders.popleft()
            self.number_of_orders -= 1

            if order.quantity <= remaining_demand:
                fulfilled_orders.append((order, order.quantity))
                remaining_demand -= order.quantity
                self.volume -= order.quantity
                
            else:
                fulfilled_orders.append((order, remaining_demand))
                self.volume -= order.quantity
                self.last_partial_order_id = order.order_id
                remaining_demand = 0
                return fulfilled_orders

        self.last_partial_order_id = None
        return fulfilled_orders

    def get_volume(self) -> int:
        return self.volume
