import random
from src.agents.agent_time_activated import TimeActivatedAgent

class FundamentalistAgent(TimeActivatedAgent):
    def __init__(self, agent_id, initial_cash, market, fundamental_value, activation_rate, max_order_size):
        super().__init__(agent_id, initial_cash, market, market.indicator_manager, activation_rate)
        self.fundamental_value = fundamental_value
        self.max_order_size = max_order_size

    def activate(self, current_time):
        best_bid = self.market.order_book.get_best_bid()
        best_ask = self.market.order_book.get_best_ask()
        mid_price = self.market.market_data.calculate_mid_price(best_bid, best_ask)

        if mid_price is None:
            mid_price = self.market.market_data.get_last_transaction_price() or 100.0

        if mid_price < self.fundamental_value - 0.5:
            order_size = random.randint(1, self.max_order_size)
            self.market.place_order(
                agent_id=self.agent_id,
                order_type='limit',
                side='buy',
                quantity=order_size,
                price=mid_price
            )
        elif mid_price > self.fundamental_value + 0.5:
            order_size = random.randint(1, self.max_order_size)
            self.market.place_order(
                agent_id=self.agent_id,
                order_type='limit',
                side='sell',
                quantity=order_size,
                price=mid_price
            )

        self.update_activation_time()
