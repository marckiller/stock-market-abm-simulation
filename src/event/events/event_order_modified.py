from src.event.event import Event
from src.event.event_types import EventType

class EventOrderModified(Event):

    type = EventType.ORDER_MODIFIED
    executable = False

    def __init__(self, timestamp: int, trigger_event_id: int, ticker: str, order_id: int, initial_quantity: int, left_quantity: int, id: int = None):
        
        super().__init__(timestamp = timestamp, id = id, trigger_event_id = trigger_event_id, ticker = ticker, order_id = order_id, initial_quantity = initial_quantity, left_quantity = left_quantity)
        self.create_message()

    def process(self):
        pass

    @classmethod
    def csv_attributes(cls):
        return super().csv_attributes() + ["ticker", "order_id", "initial_quantity", "left_quantity"]
    
    def create_message(self):
        return super().create_message() + f"Order {self.order_id} modified for {self.ticker} from {self.initial_quantity} to {self.left_quantity}."