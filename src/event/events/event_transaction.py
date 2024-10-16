from src.event.event import Event
from src.event.event_types import EventType

class Transaction(Event):

    type = EventType.TRANSACTION
    executable = False

    def __init__(self, timestamp: int, trigger_event_id: int, ticker: str, quantity: int, price: float, id_buyer: int, id_seller: int, id_buy_order: int, id_sell_order: int, id: int = None):
        
        super().__init__(timestamp = timestamp, id = id, trigger_event_id = trigger_event_id, ticker = ticker, quantity = quantity, price = price, id_buyer = id_buyer, id_seller = id_seller, id_buy_order = id_buy_order, id_sell_order = id_sell_order)
        self.create_message()

    def process(self):
        pass

    @classmethod
    def csv_attributes(cls):
        return super().csv_attributes() + ["ticker", "quantity", "price", "id_buyer", "id_seller", "id_buy_order", "id_sell_order"]
    
    def create_message(self):
        return f"Transaction {self.id} occurred at {self.timestamp} for {self.quantity} shares of {self.ticker} at price {self.price} between {self.id_buyer} and {self.id_seller}."