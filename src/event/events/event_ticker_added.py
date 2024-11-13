from src.event.event import Event
from src.event.event_types import EventType

class EventTickerAdded(Event):

    type = EventType.TICKER_ADDED
    executable = False

    def __init__(self, timestamp: int, trigger_event_id: int, ticker: str, id: int = None):

        super().__init__(timestamp = timestamp, id = id, trigger_event_id = trigger_event_id, ticker = ticker)
        self.create_message()

    def process(self):
        pass

    @classmethod
    def csv_attributes(cls):
        return super().csv_attributes() + ["ticker"]
    
    def create_message(self):
        return super().create_message() + f"Ticker {self.ticker} added to the market."