from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, agent_id, initial_cash, market, indicator_manager):
        self.agent_id = agent_id
        self.cash = initial_cash
        self.market = market
        self.indicator_manager = indicator_manager
        self.active = True
        self.holdings = 0  #quantity of stock held
        
        #order_id -> {order_id: order} 
        #keep reference to order stored in the book to 
        #skip the process of manual modification of pending orders
        self.pending_limit_orders = {}
    
    @abstractmethod
    def activate(self, current_time):
        pass

    def modify_pending_limit_orders(self, order_id, side, price, quantity):
        if order_id in self.pending_limit_orders:
            self.pending_limit_orders[order_id] = {
                'side': side,
                'price': price,
                'quantity': quantity
            }

    def remove_pending_limit_order(self, order_id):
        if order_id in self.pending_limit_orders:
            del self.pending_limit_orders[order_id]

    def add_cash(self, cash):
        self.cash += cash

    def deduct_cash(self, cash):
        self.cash -= cash

    def add_holding(self, quantity):
        self.holdings += quantity

    def deduct_holding(self, quantity):
        self.holdings -= quantity

    def get_holding_value(self, current_price):
        return self.holdings * current_price
    
    def get_total_value(self, current_price):
        return self.cash + self.get_holding_value(current_price)