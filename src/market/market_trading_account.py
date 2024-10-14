from typing import Dict, Any, Optional

class TradingAccount:

    def __init__(self):
        self.balance: float = 0.0
        self.pending_orders: Dict[int, Dict[str, Any]] = {}
    
    def add_pending_limit_order(self, id: int, ticker: str, side: str, price: float, expiration_time: Optional[int] = None) -> None:
        if id in self.pending_orders:
            raise ValueError(f"Order with id {id} already exists.")
        
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be either 'BUY' or 'SELL'.")
        
        order = {
            'id': id,
            'ticker': ticker,
            'side': side,
            'price': price,
            'expiration_time': expiration_time
        }
        
        self.pending_orders[id] = order
        print(f"Added pending limit order: {order}")
    
    def remove_pending_order(self, id: int) -> None:
        if id not in self.pending_orders:
            raise KeyError(f"Order with id {id} does not exist.")
        
        removed_order = self.pending_orders.pop(id)
        print(f"Removed pending order: {removed_order}")
    
    def add_funds(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Amount to add cannot be negative.")
        
        self.balance += amount
        print(f"Added funds: {amount}. New balance: {self.balance}")
    
    def remove_funds(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Amount to remove cannot be negative.")
        
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        
        self.balance -= amount
        print(f"Removed funds: {amount}. New balance: {self.balance}")
    
    def __str__(self) -> str:
        orders = "\n".join([f"ID: {order['id']}, Ticker: {order['ticker']}, Side: {order['side']}, Price: {order['price']}, Expiration: {order['expiration_time']}" 
                            for order in self.pending_orders.values()])
        return f"TradingAccount:\nBalance: {self.balance}\nPending Orders:\n{orders if orders else 'None'}"
