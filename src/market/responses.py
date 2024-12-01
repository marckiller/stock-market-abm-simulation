class LimitOrderStoredResponse:
    """
    Represents a response indicating that a limit order has been stored.

    Attributes:
        order_id (int): The unique identifier of the order.
        agent_id (int): The identifier of the agent who placed the order.
        quantity (int): The quantity of the order that was stored.
    """
    def __init__(self, order_id, agent_id, quantity):
        """
        Initializes a limit order stored response.

        Args:
            order_id (int): The ID of the stored order.
            agent_id (int): The ID of the agent placing the order.
            quantity (int): The quantity of the order.
        """
        self.order_id = order_id
        self.agent_id = agent_id
        self.quantity = quantity

    def __str__(self) -> str:
        """
        Returns a string representation of the stored response.

        Returns:
            str: A description of the stored response.
        """
        return f'Order {self.order_id} stored for agent {self.agent_id}'


class OrderExecutedResponse:
    """
    Represents a response indicating that an order has been executed.

    Attributes:
        order_id (int): The unique identifier of the executed order.
        agent_id (int): The identifier of the agent involved in the execution.
        remaining_quantity (int): The remaining quantity of the order after execution.
    """
    def __init__(self, order_id, agent_id, remaining_quantity):
        """
        Initializes an order executed response.

        Args:
            order_id (int): The ID of the executed order.
            agent_id (int): The ID of the agent involved in the execution.
            remaining_quantity (int): The remaining quantity after execution.
        """
        self.order_id = order_id
        self.agent_id = agent_id
        self.remaining_quantity = remaining_quantity

    def __str__(self) -> str:
        """
        Returns a string representation of the execution response.

        Returns:
            str: A description of the executed order response.
        """
        return f'Order {self.order_id} executed for agent {self.agent_id}'


class OrderCancelledResponse:
    """
    Represents a response indicating that an order has been cancelled.

    Attributes:
        order_id (int): The unique identifier of the cancelled order.
        agent_id (int): The identifier of the agent who cancelled the order.
    """
    def __init__(self, order_id, agent_id):
        """
        Initializes an order cancelled response.

        Args:
            order_id (int): The ID of the cancelled order.
            agent_id (int): The ID of the agent who cancelled the order.
        """
        self.order_id = order_id
        self.agent_id = agent_id

    def __str__(self) -> str:
        """
        Returns a string representation of the cancellation response.

        Returns:
            str: A description of the cancelled order response.
        """
        return f'Order {self.order_id} cancelled for agent {self.agent_id}'


class Transaction:
    """
    Represents a transaction between a buyer and a seller.

    Attributes:
        order_buy_id (int): The ID of the buy order.
        order_sell_id (int): The ID of the sell order.
        buyer_id (int): The ID of the buyer.
        seller_id (int): The ID of the seller.
        price (float): The transaction price.
        quantity (int): The quantity involved in the transaction.
        timestamp (float): The timestamp of the transaction.
    """
    def __init__(self, order_buy_id, order_sell_id, buyer_id, seller_id, price, quantity, timestamp):
        """
        Initializes a transaction.

        Args:
            order_buy_id (int): The ID of the buy order.
            order_sell_id (int): The ID of the sell order.
            buyer_id (int): The ID of the buyer.
            seller_id (int): The ID of the seller.
            price (float): The price of the transaction.
            quantity (int): The quantity traded.
            timestamp (float): The timestamp of the transaction.
        """
        self.order_buy_id = order_buy_id
        self.order_sell_id = order_sell_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp

    def __str__(self) -> str:
        """
        Returns a string representation of the transaction.

        Returns:
            str: A description of the transaction.
        """
        return f'Transaction: {self.quantity} units at {self.price}. Buyer: {self.buyer_id}, Seller: {self.seller_id}'
