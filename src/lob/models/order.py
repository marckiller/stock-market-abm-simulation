from src.lob.models.order_types import OrderType

class Order:

    next_id = 0
    type = OrderType.ABSTRACT_ORDER

    def __init__(self, timestamp: int, quantity: int, issuer_id: int, valid: bool = True, id: int = None):

        if id:
            self.id = id
        else: 
            self.id = Order.next_id
            Order.next_id += 1

        self.timestamp = timestamp
        self.quantity = quantity
        self.issuer_id = issuer_id
        self.valid = valid

    def sub_quantity(self, quantity: int) -> int:
 
        if self.quantity - quantity < 0:
            raise ValueError
        
        self.quantity -= quantity

        if self.quantity == 0:
            self.valid = False

        return self.quantity
    
    def close(self) -> int:

        self.valid = False
        return self.quantity
    
    