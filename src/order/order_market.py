from src.order.order import Order
from src.order.order import OrderSide
from src.order.order import OrderType

class OrderMarket(Order):

    ORDER_TYPE = OrderType.MARKET

    def __init__(self,ticker: str, quantity: int, side: OrderSide, time: int, order_id: int = None):
        super().__init__(ticker, quantity, side, time, order_id)