import random
import numpy as np
from src.agents.agent_time_activated import TimeActivatedAgent

class ZeroIntelligenceAgent(TimeActivatedAgent):
    def __init__(self, agent_id, initial_cash, market, max_order_size, limit_order_rate, market_order_rate, cancellation_rate, activation_rate):
        """
        Initializes a Zero-Intelligence Agent.
        Args:
            agent_id (str): Unique identifier for the agent.
            initial_cash (float): Starting cash balance for the agent.
            market (Market): Reference to the market object.
            max_order_size (int): Maximum number of shares per order.
            limit_order_rate (float): Probability of placing a limit order.
            market_order_rate (float): Probability of placing a market order.
            cancellation_rate (float): Probability of canceling a limit order.
            activation_rate (float): Rate parameter for exponential distribution determining activation time.
        """
        super().__init__(agent_id, initial_cash, market, market.indicator_manager, activation_rate)
        self.max_order_size = max_order_size
        self.limit_order_rate = limit_order_rate
        self.market_order_rate = market_order_rate
        self.cancellation_rate = cancellation_rate
        self.activation_rate = activation_rate
        self.next_activation_time = self._generate_next_activation_time()

    def activate(self, current_time):
        """
        Activates the agent and performs one action based on probabilities:
        - Places a limit order.
        - Places a market order.
        - Cancels a limit order.
        """
        # Normalize probabilities to ensure only one action is chosen
        total_rate = self.limit_order_rate + self.market_order_rate + self.cancellation_rate
        rand = random.uniform(0, total_rate)

        if rand < self.limit_order_rate:
            self.place_limit_order()
        elif rand < self.limit_order_rate + self.market_order_rate:
            self.place_market_order()
        else:
            self.cancel_random_limit_order()

        # Schedule next activation
        self.next_activation_time = self._generate_next_activation_time()

    def place_limit_order(self):
        """
        Places a limit order with random attributes.
        """
        order_size = random.randint(1, self.max_order_size)
        side = random.choice(['buy', 'sell'])

        best_bid = self.market.order_book.get_best_bid()
        best_ask = self.market.order_book.get_best_ask()
        last_transaction_price = self.market.market_data.get_last_transaction_price()

        if side == 'buy':
            if best_ask is not None:
                price = random.uniform(max(0, best_ask - 10), best_ask)
            elif last_transaction_price is not None:
                price = random.uniform(max(0, last_transaction_price - 5), last_transaction_price + 5)
            else:
                price = random.uniform(50, 150)
        else:
            if best_bid is not None:
                price = random.uniform(best_bid, best_bid + 10)
            elif last_transaction_price is not None:
                price = random.uniform(max(0, last_transaction_price - 5), last_transaction_price + 5)
            else:
                price = random.uniform(50, 150)

        self.market.place_order(
            agent_id=self.agent_id,
            order_type='limit',
            side=side,
            quantity=order_size,
            price=price
        )

    def place_market_order(self):
        """
        Places a market order with random size.
        """
        order_size = random.randint(1, self.max_order_size)
        side = random.choice(['buy', 'sell'])

        self.market.place_order(
            agent_id=self.agent_id,
            order_type='market',
            side=side,
            quantity=order_size
        )

    def cancel_random_limit_order(self):
        """
        Cancels a random limit order from the agent's pending orders.
        """
        if not self.pending_limit_orders:
            return

        order_id = random.choice(list(self.pending_limit_orders.keys()))
        self.market.cancel_order(order_id)
