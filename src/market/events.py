from src.market.order import Order
from src.market.transaction import Transaction

class Event:
    def __init__(self, event_type: str, timestamp: int):
        self.event_type = event_type
        self.timestamp = timestamp

class LimitOrderStoredEvent(Event):
    def __init__(self, timestamp, order: Order):
        super().__init__(event_type='limit_order_stored', timestamp=timestamp)
        self.order = order

class OrderExecutedEvent(Event):
    def __init__(self, timestamp, order: Order, executed_quantity: int):
        super().__init__(event_type='order_executed', timestamp=timestamp)
        self.order = order
        self.executed_quantity = executed_quantity

class OrderCancelledEvent(Event):
    def __init__(self, timestamp, order: Order):
        super().__init__(event_type='order_cancelled', timestamp=timestamp)
        self.order = order

class TransactionEvent(Event):
    def __init__(self, timestamp, transaction: Transaction):
        super().__init__(event_type='transaction', timestamp=timestamp)
        self.transaction = transaction

