class Transaction:
    def __init__(self, order_buy_id, order_sell_id, buyer_id, seller_id, price, quantity, timestamp):

        self.order_buy_id = order_buy_id
        self.order_sell_id = order_sell_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp

    def __str__(self) -> str:
        return f'Transaction: {self.quantity} units at {self.price}. Buyer: {self.buyer_id}, Seller: {self.seller_id}'