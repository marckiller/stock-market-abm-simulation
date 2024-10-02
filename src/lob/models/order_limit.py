from src.lob.models.order_types import OrderType

class LimitOrder(Order):
    
    type = OrderType.LIMIT

    def __init__(self, timestamp: int, quantity: int, issuer_id: int, price: float, expiration_time: float, is_buy: bool, valid: bool = True, id: int = None):
        super().__init__(timestamp, quantity, issuer_id, valid, id)
        self.is_buy = is_buy
        self.price = price
        self.expiration_time = expiration_time

    def __repr__(self):
        return (f"LimitOrder(id={self.id}, timestamp={self.timestamp}, quantity={self.quantity}, "
                f"issuer_id={self.issuer_id}, price={self.price}, expiration_time={self.expiration_time}, "
                f"is_buy={self.is_buy}, valid={self.valid})")
