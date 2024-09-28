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

    next_id = 0

    def __init__(self, quantity: int, side: OrderSide, type: OrderType, time: int, order_id: int = None):

        self.order_id = order_id if order_id is not None else Order.next_id
        Order.next_id += 1

        self.quantity = quantity
        self.side = side
        self.type = type
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
        if self.status == OrderStatus.OPEN:
            self.status = OrderStatus.CANCELED

    def is_active(self):
        return self.status == OrderStatus.OPEN
    
    def is_filled(self):
        return self.status == OrderStatus.FILLED
