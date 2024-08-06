from src.events.event import Event
from src.lob.models.order import Order
from src.lob.models.order_types import OrderType

class LOB:

    def __init__(self):
        #key: order_id, value: [is_buy, price]
        self.orders = {}

        

    def process_order(self, order: Order) -> list[Event]:
        pass

    def cancel_order(self, order: Order) ->list[Event]:
        pass


    