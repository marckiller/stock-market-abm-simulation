from src.event.event import Event
from src.event.event_types import EventType

class EventOrderAddedBack(Event):

    type = EventType.ORDER_ADDED_BACK
    executable = False

    def __init__(self, timestamp: int, trigger_event_id: int, ticker: str, order_id: int, id: int = None):
        
        super().__init__(timestamp = timestamp, id = id, trigger_event_id = trigger_event_id, ticker = ticker, order_id = order_id)
        self.create_message()

    def process(self):
        pass

    @classmethod
    def csv_attributes(cls):
        return super().csv_attributes() + ["ticker", "order_id"]
    
    def create_message(self):
        return super().create_message() + f" {self.ticker}: Order {self.order_id} added back."