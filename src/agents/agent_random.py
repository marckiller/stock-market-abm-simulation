from src.agents.agent_agent import AbstractAgent

import random

class RandomAgent(AbstractAgent):
    def __init__(self, limit_order_intensity, market_order_intensity, cancellation_intensity,
                 typical_order_size, max_price_range):
        super().__init__()
        self.limit_order_intensity = limit_order_intensity
        self.market_order_intensity = market_order_intensity
        self.cancellation_intensity = cancellation_intensity
        self.typical_order_size = typical_order_size
        self.max_price_range = max_price_range

    def act(self, market_data, portfolio):
        action_probability = random.random()

        if action_probability < self.limit_order_intensity:
            self._place_limit_order(market_data)
        elif action_probability < self.limit_order_intensity + self.market_order_intensity:
            self._place_market_order(market_data)
        elif action_probability < self.limit_order_intensity + self.market_order_intensity + self.cancellation_intensity:
            self._cancel_order(portfolio)

    def _place_limit_order(self, market_data):
        instrument_id = random.choice(market_data.get_all_instruments())
        order_size = self._generate_order_size()
        side = random.choice(['buy', 'sell'])
        proposed_price = self._generate_price_for_limit_order(instrument_id, side, market_data)
        # Tutaj dodaj logikę składania zlecenia limit
        print(f"Agent {self.id} składa zlecenie limit {side}: {order_size} jednostek po cenie {proposed_price} na {instrument_id}")

    def _place_market_order(self, market_data):
        instrument_id = random.choice(market_data.get_all_instruments())
        order_size = self._generate_order_size()
        side = random.choice(['buy', 'sell'])
        # Tutaj dodaj logikę składania zlecenia market
        print(f"Agent {self.id} składa zlecenie market {side}: {order_size} jednostek na {instrument_id}")

    def _cancel_order(self, portfolio):
        if portfolio.orders:  # Załóżmy, że portfolio ma atrybut 'orders'
            order_id = random.choice(list(portfolio.orders.keys()))
            print(f"Agent {self.id} anuluje zlecenie o ID: {order_id}")
            portfolio.cancel_order(order_id)

    def _generate_order_size(self):
        lower, upper = 1, 10 * self.typical_order_size
        mu, sigma = self.typical_order_size, self.typical_order_size / 2
        size = truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma).rvs()
        return max(1, int(size))

    def _generate_price_for_limit_order(self, instrument_id, side, market_data):
        # Zakładając, że market_data może dostarczyć best_bid i best_ask
        instrument_data = market_data.get_instrument_data(instrument_id)
        if instrument_data is None or not instrument_data.best_bids or not instrument_data.best_asks:
            return None  # Lub ustaw cenę domyślną

        best_bid = instrument_data.best_bids[-1][1]
        best_ask = instrument_data.best_asks[-1][1]

        if side == 'buy':
            min_price = best_ask - self.max_price_range
            max_price = best_ask
            price = random.uniform(min_price, max_price)
        else:
            min_price = best_bid
            max_price = best_bid + self.max_price_range
            price = random.uniform(min_price, max_price)

        return round(price, 2)
