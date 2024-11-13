from src.order.order import Order, OrderSide, OrderType, OrderStatus
from src.order.order_limit import OrderLimit
from src.order.order_market import OrderMarket


orders = [
    # Limit Buy Orders
    OrderLimit(agent_id=1, ticker='AAPL', price=100.0, quantity=50, side=OrderSide.BUY, time=1),
    OrderLimit(agent_id=2, ticker='AAPL', price=101.0, quantity=30, side=OrderSide.BUY, time=2),
    OrderLimit(agent_id=3, ticker='AAPL', price=99.0, quantity=20, side=OrderSide.BUY, time=3),
    OrderLimit(agent_id=4, ticker='AAPL', price=98.5, quantity=25, side=OrderSide.BUY, time=4),
    OrderLimit(agent_id=5, ticker='AAPL', price=100.5, quantity=10, side=OrderSide.BUY, time=5),

    # Limit Sell Orders
    OrderLimit(agent_id=6, ticker='AAPL', price=102.0, quantity=40, side=OrderSide.SELL, time=6),
    OrderLimit(agent_id=7, ticker='AAPL', price=101.5, quantity=35, side=OrderSide.SELL, time=7),
    OrderLimit(agent_id=8, ticker='AAPL', price=103.0, quantity=15, side=OrderSide.SELL, time=8),
    OrderLimit(agent_id=9, ticker='AAPL', price=102.5, quantity=20, side=OrderSide.SELL, time=9),
    OrderLimit(agent_id=10, ticker='AAPL', price=101.0, quantity=50, side=OrderSide.SELL, time=10),

    # Market Buy Orders
    OrderMarket(agent_id=11, ticker='AAPL', quantity=45, side=OrderSide.BUY, time=11),
    OrderMarket(agent_id=12, ticker='AAPL', quantity=60, side=OrderSide.BUY, time=12),

    # Market Sell Orders
    OrderMarket(agent_id=13, ticker='AAPL', quantity=55, side=OrderSide.SELL, time=13),
    OrderMarket(agent_id=14, ticker='AAPL', quantity=30, side=OrderSide.SELL, time=14),

    # Additional Limit Orders to test matching and order book updates
    OrderLimit(agent_id=15, ticker='AAPL', price=100.0, quantity=25, side=OrderSide.SELL, time=15),
    OrderLimit(agent_id=16, ticker='AAPL', price=99.5, quantity=20, side=OrderSide.SELL, time=16),
    OrderLimit(agent_id=17, ticker='AAPL', price=101.0, quantity=15, side=OrderSide.BUY, time=17),
    OrderLimit(agent_id=18, ticker='AAPL', price=98.0, quantity=35, side=OrderSide.BUY, time=18)
]

from src.lob.lob_limit_order_book import LimitOrderBook
from src.lob.lob_matching_engine import MatchingEngine

lob = LimitOrderBook()
me = MatchingEngine()

events = []
for order in orders:
    time = order.timestamp
    events += me.process_order(order, lob, time, time)

for event in events:
    print(event)