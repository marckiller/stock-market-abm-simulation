class Order:
    """
    Represents an individual order in the market.

    Attributes:
        order_id (int): Unique identifier for the order.
        agent_id (int): Identifier for the agent who placed the order.
        timestamp (float): The time the order was placed.
        side (str): Specifies whether the order is a 'buy' or 'sell'.
        order_type (str): Specifies the type of order ('market' or 'limit').
        quantity (int): The number of units for the order.
        price (float or None): The price for the order (only for limit orders).
    """
    def __init__(self, order_id, agent_id, timestamp, side, order_type, quantity, price=None):
        """
        Initializes a new order.

        Args:
            order_id (int): The unique identifier for the order.
            agent_id (int): The agent placing the order.
            timestamp (float): The timestamp of the order.
            side (str): 'buy' or 'sell'.
            order_type (str): 'market' or 'limit'.
            quantity (int): Number of units in the order.
            price (float or None, optional): The price for limit orders. Defaults to None for market orders.
        """
        self.order_id = order_id
        self.agent_id = agent_id
        self.timestamp = timestamp
        self.side = side  # 'buy' or 'sell'
        self.order_type = order_type  # 'market' or 'limit'
        self.quantity = quantity
        if order_type == 'limit' and price is None:
            raise ValueError("Price must be provided for limit orders.")
        self.price = price if order_type == 'limit' else None


    def modify_order(self, new_quantity=None):
        """
        Modifies the quantity of the order.

        Args:
            new_quantity (int, optional): The new quantity for the order.

        Raises:
            ValueError: If new_quantity is not provided.
        """
        if new_quantity is not None:
            self.quantity = new_quantity
        else:
            raise ValueError("New quantity must be provided.")

    def __str__(self) -> str:
        """
        Returns a string representation of the order.

        Returns:
            str: A string describing the order.
        """
        return f'Order {self.order_id} ({self.side} {self.quantity} units) from agent {self.agent_id}'
