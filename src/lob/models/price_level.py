from src.lob.models.order import Order

import heapq

class PriceLevel:

    def __init__(self, price: float):

        self.price = price
        self.volume = 0
        self.num_orders = 0

        #heapq
        self.orders = []

    def add_order(self, order: Order):
        heapq
