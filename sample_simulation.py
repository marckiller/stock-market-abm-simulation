from src.simulation.simulation import Simulation
import numpy as np

num_fundamentalists = 50
fundamental_mean = 100.0
fundamental_std = 30.0
activation_rate_min = 0.01
activation_rate_max = 0.05

fundamentalists = []
for i in range(1, num_fundamentalists + 1):
    fundamentalists.append({
        "id": 100 + i,
        "type": "fundamentalist",
        "cash": 0,
        "fundamental_value": np.random.normal(fundamental_mean, fundamental_std),
        "activation_rate": np.random.uniform(activation_rate_min, activation_rate_max),
        "max_order_size": 1
    })

config = {
    "market": {
        "ohlcv_periods": [1000],
        "store_tick_data": False,
        "max_ticks": 1000
    },
    "agents": [
        {
            "id": 1,
            "type": "zero_intelligence",
            "cash": 0,
            "max_order_size": 5,
            "limit_order_rate": 0.7,
            "market_order_rate": 0.2,
            "cancellation_rate": 0.1,
            "activation_rate": 0.4
        },
        {
            "id": 4,
            "type": "chartist",
            "cash": 0,
            "activation_rate": 0.1,
            "max_order_size": 5,
            "window": 5
        },
        {
            "id": 4,
            "type": "chartist",
            "cash": 0,
            "activation_rate": 0.1,
            "max_order_size": 5,
            "window": 100
        }
    ] + fundamentalists,
    "time_step": 1,
    "max_time": 10000
}

# Symulacja
simulation = Simulation(config)
simulation.create_agent = lambda agent_config: create_agent(agent_config, simulation.market)
simulation.run()

def summarize_agents_to_file(simulation, filename):
    """
    Summarizes all agents' portfolios and saves to a file.
    Args:
        simulation: The simulation object.
        filename (str): The output file name.
    """
    with open(filename, 'w') as file:
        file.write("===== Agents Portfolio Summary =====\n")
        last_transaction_price = simulation.market.market_data.get_last_transaction_price()
        last_transaction_price = last_transaction_price if last_transaction_price is not None else 0

        for agent in simulation.market.agent_manager.agents.values():
            total_value = agent.get_total_value(last_transaction_price)
            
            file.write(f"\nAgent ID: {agent.agent_id}\n")
            file.write(f"Agent Type: {agent.__class__.__name__}\n")
            file.write(f"Cash: {agent.cash:.2f}\n")
            file.write(f"Holdings: {agent.holdings}\n")
            file.write(f"Total Portfolio Value: {total_value:.2f}\n")
            file.write(f"Pending Limit Orders: {len(agent.pending_limit_orders)}\n")
            file.write("===================================\n")

summarize_agents_to_file(simulation, 'agents_result.txt')

print(simulation.market.market_data.ohlcv_data[1000].tail(10))

import os

ohlcv_data = simulation.market.market_data.ohlcv_data[1000]
results_folder = 'results'
os.makedirs(results_folder, exist_ok=True)
output_file = os.path.join(results_folder, 'ohlcv_data.csv')
ohlcv_data.to_csv(output_file, index=False)
