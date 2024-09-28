from src.order.order import Order
from src.order.order import OrderSide
from src.order.order import OrderType
from src.order.order import OrderStatus

class OrderLimit(Order):

    def __init__(self, price: float, quantity: int, side: OrderSide, time: int, expiraton_time: int = None, order_id: int = None):

        super().__init__(quantity, side, OrderType.LIMIT, time, order_id)

        self.price = price
        self.expiration_time = expiraton_time

    def expire(self):
        if self.status == OrderStatus.OPEN:
            self.status = OrderStatus.EXPIRED
