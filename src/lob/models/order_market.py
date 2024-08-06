from src.lob.models.order import Order
from src.lob.models.order_types import OrderType

class MarketOrder(Order):

    type = OrderType.MARKET

    def __init__(self, timestamp: int, quantity: int, issuer_id: int, is_buy: bool, valid: bool = True, id: int = None):
        super().__init__(timestamp, quantity, issuer_id, valid, id)
        self.is_buy = is_buy

    def __repr__(self):
        return (f"MarketOrder(id={self.id}, timestamp={self.timestamp}, quantity={self.quantity}, "
                f"issuer_id={self.issuer_id}, is_buy={self.is_buy}, valid={self.valid})")

    