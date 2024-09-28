from src.order.order import Order
from src.order.order import OrderSide
from src.order.order import OrderType
from src.order.order import OrderStatus

class OrderMarket(Order):

    def __init__(self, quantity: int, side: OrderSide, time: int, order_id: int = None):
        super().__init__(quantity, side, OrderType.MARKET, time, order_id)