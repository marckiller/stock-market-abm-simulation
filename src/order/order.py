from enum import Enum, auto

class OrderSide(Enum):
    BUY = auto()
    SELL = auto()

class OrderType(Enum):
    LIMIT = auto()
    MARKET = auto()

class OrderStatus(Enum):
    OPEN = auto()
    FILLED = auto()
    CANCELED = auto()
    EXPIRED = auto()

class Order:

    ORDER_TYPE = None  #Must be defined in child class

    next_id = 0

    def __init__(self, quantity: int, side: OrderSide, time: int, order_id: int = None):
        if self.ORDER_TYPE is None:
            raise ValueError("ORDER_TYPE must be set in child class.")
        
        if order_id is not None:
            self.order_id = order_id
        else:
            self.order_id = Order.next_id
            Order.next_id += 1 

        self.quantity = quantity
        self.side = side
        self.type = self.ORDER_TYPE
        self.timestamp = time

        self.status = OrderStatus.OPEN

    def execute(self, quantity: int):
        if self.status in [OrderStatus.CANCELED, OrderStatus.EXPIRED]:
            return

        if quantity <= self.quantity:
            self.quantity -= quantity
        else:
            self.quantity = 0

        if self.quantity == 0:
            self.status = OrderStatus.FILLED

    def cancel(self):
        if self.status not in [OrderStatus.FILLED, OrderStatus.EXPIRED]:
            self.status = OrderStatus.CANCELED

    def is_active(self):
        return self.status == OrderStatus.OPEN

    def is_filled(self):
        return self.status == OrderStatus.FILLED