from src.simulation.simulation import Simulation

#simulation configuration
config = {
    "market": {
        "ohlcv_periods": [10000],
        "store_tick_data": False,
        "max_ticks": 10000
    },
    "agents": [
        {
            "id": 1,
            "type": "zero_intelligence",
            "cash": 0,
            "max_order_size": 5,
            "limit_order_rate": 0.6,
            "market_order_rate": 0.3,
            "cancellation_rate": 0.1,
            "activation_rate": 0.6
        },
         {
            "id": 2,
            "type": "zero_intelligence",
            "cash": 0,
            "max_order_size": 5,
            "limit_order_rate": 0.6,
            "market_order_rate": 0.3,
            "cancellation_rate": 0.1,
            "activation_rate": 0.4
        }
    ],
    "time_step": 1,
    "max_time": 288000
}

simulation = Simulation(config)
simulation.create_agent = lambda agent_config: create_agent(agent_config, simulation.market)
simulation.run()

#ticks = simulation.market.market_data.get_recent_ticks(n=config["market"]["max_ticks"])
#transaction_prices = ticks['transaction_price']

last_transaction_price = simulation.market.market_data.get_last_transaction_price()

agent = simulation.market.agent_manager.agents[1]
total_value = agent.get_total_value(last_transaction_price if last_transaction_price else 0)

print("\n===== Final Portfolio Report =====")
print(f"Agent ID: {agent.agent_id}")
print(f"Cash: {agent.cash:.2f}")
print(f"Holdings: {agent.holdings}")
print(f"Last Transaction Price: {last_transaction_price:.2f}" if last_transaction_price is not None else "No transactions executed.")
print(f"Total Portfolio Value: {total_value:.2f}")
print("===================================")

agent = simulation.market.agent_manager.agents[2]
total_value = agent.get_total_value(last_transaction_price if last_transaction_price else 0)

print("\n===== Final Portfolio Report =====")
print(f"Agent ID: {agent.agent_id}")
print(f"Cash: {agent.cash:.2f}")
print(f"Holdings: {agent.holdings}")
print(f"Last Transaction Price: {last_transaction_price:.2f}" if last_transaction_price is not None else "No transactions executed.")
print(f"Total Portfolio Value: {total_value:.2f}")
print("===================================")

print(simulation.market.market_data.ohlcv_data[10000].tail())
