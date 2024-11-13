from src.event.event import Event
from src.event.event_types import EventType

class EventOrderExecuted(Event):

    type = EventType.ORDER_EXECUTED
    executable = False

    def __init__(self, timestamp: int, trigger_event_id: int, ticker: str, order_id: int, agent_id: int, id: int = None):
        
        super().__init__(timestamp = timestamp, id = id, trigger_event_id = trigger_event_id, ticker = ticker, order_id = order_id, agent_id = agent_id)
        self.create_message()

    def process(self):
        pass

    @classmethod
    def csv_attributes(cls):
        return super().csv_attributes() + ["ticker", "order_id", "agent_id"]
    
    def create_message(self):
        return super().create_message() + f"{self.ticker}: Order {self.order_id} (issuer: {self.agent_id}) executed."
    