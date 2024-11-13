from abc import ABC, abstractmethod
from typing import Dict
from src.order.order import Order

from src.market.market_data import MarketData
from src.market.market_trading_account import TradingAccount

class AbstractAgent(ABC):

    next_id = 1  # "Agent 0" is the simulation itself

    def __init__(self):
        self.id = AbstractAgent.next_id
        AbstractAgent.next_id += 1
        self.money = 0.0

        # Agents hold references to Order objects
        # TODO: consider keeping copies of order data instead of references
        # or making Order objects immutable/read-only
        self.pending_limit_orders: Dict[int, Order] = {}
        
    def add_pending_order(self, order: Order):
        """
        Adds an Order object to the agent's pending limit orders.

        :param order: The Order object to be added.
        """
        self.pending_limit_orders[order.order_id] = order
        # Debug statement (optional)
        print(f"Agent {self.id}: Added pending order with ID {order.order_id}.")

    def remove_pending_order(self, order_id: int):
        """
        Removes an Order from the agent's pending limit orders by its ID.

        :param order_id: The ID of the Order to be removed.
        """
        if order_id in self.pending_limit_orders:
            del self.pending_limit_orders[order_id]
            # Debug statement (optional)
            print(f"Agent {self.id}: Removed pending order with ID {order_id}.")
        else:
            print(f"Agent {self.id}: Order with ID {order_id} not found in pending orders.")

    def add_money(self, amount: float):
        """
        Adds money to the agent's balance.

        :param amount: The amount of money to add.
        """
        if amount < 0:
            raise ValueError("Amount to add cannot be negative.")
        self.money += amount
        # Debug statement (optional)
        print(f"Agent {self.id}: Added {amount} to balance. New balance: {self.money}.")

    def remove_money(self, amount: float):
        """
        Removes money from the agent's balance.

        :param amount: The amount of money to remove.
        """
        if amount < 0:
            raise ValueError("Amount to remove cannot be negative.")
        if self.money >= amount:
            self.money -= amount
            # Debug statement (optional)
            print(f"Agent {self.id}: Removed {amount} from balance. New balance: {self.money}.")
        else:
            raise ValueError(f"Agent {self.id}: Insufficient funds to remove {amount}.")

    @abstractmethod
    def act(self, time: int, market_data: MarketData, portfolio: TradingAccount):
        pass
