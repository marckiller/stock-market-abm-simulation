from src.order.order import Order
from src.order.order import OrderSide
from src.order.order import OrderType
from src.order.order import OrderStatus

class OrderLimit(Order):

    ORDER_TYPE = OrderType.LIMIT

    def __init__(self, price: float, quantity: int, side: OrderSide, time: int, expiration_time: int = None, order_id: int = None):

        if price <= 0:
            raise ValueError("Price must be positive")

        super().__init__(quantity, side, time, order_id)

        self.price = price
        self.expiration_time = expiration_time

    def expire(self):
        if self.status == OrderStatus.OPEN:
            self.status = OrderStatus.EXPIRED
