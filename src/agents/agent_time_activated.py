import numpy as np
from src.agents.base_agent import BaseAgent

class TimeActivatedAgent(BaseAgent):
    def __init__(self, agent_id, initial_cash, market, indicator_manager, activation_rate, **kwargs):
        """
        Initializes a Time-Activated Agent.
        Args:
            agent_id (str): Unique identifier for the agent.
            initial_cash (float): Initial cash balance for the agent.
            market (Market): Reference to the market object.
            indicator_manager: Reference to the indicator manager.
            activation_rate (float): Rate parameter for exponential distribution.
            **kwargs: Additional arguments for specific agent types.
        """
        super().__init__(agent_id, initial_cash, market, indicator_manager)
        self.activation_rate = activation_rate
        self.next_activation_time = self._generate_next_activation_time()

    def _generate_next_activation_time(self):
        current_time = self.market.get_current_time()
        next_time = current_time + np.random.exponential(scale=1 / self.activation_rate)
        return int(round(next_time))

    def activate(self, current_time):
        raise NotImplementedError("Subclasses must implement the `activate` method.")

    def update_activation_time(self):
        self.next_activation_time = self._generate_next_activation_time()
