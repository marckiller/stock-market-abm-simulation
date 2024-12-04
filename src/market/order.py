class Order:
    def __init__(self, order_id, agent_id, timestamp, side, order_type, quantity, price=None):
        self.order_id = order_id
        self.agent_id = agent_id
        self.timestamp = timestamp
        self.side = side  # 'buy' or 'sell'
        self.order_type = order_type  # 'market' or 'limit'
        self.quantity = quantity
        if order_type == 'limit' and price is None:
            raise ValueError("Price must be provided for limit orders.")
        self.price = price if order_type == 'limit' else None


    def modify_quantity(self, new_quantity=None):
        if new_quantity is not None:
            self.quantity = new_quantity
        else:
            raise ValueError("New quantity must be provided.")

    def __str__(self) -> str:
        return f'Order {self.order_id} ({self.side} {self.quantity} units) from agent {self.agent_id}'
