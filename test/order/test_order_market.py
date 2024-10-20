import unittest
from src.order.order import OrderSide, OrderType, OrderStatus, Order
from src.order.order_market import OrderMarket

class TestOrderMarket(unittest.TestCase):

    def setUp(self):
        Order.next_id = 0
        OrderMarket.next_id = 0

    def test_order_market_initialization(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1000)
        self.assertEqual(order.order_id, 0)
        self.assertEqual(order.quantity, 15)
        self.assertEqual(order.side, OrderSide.SELL)
        self.assertEqual(order.type, OrderType.MARKET)
        self.assertEqual(order.timestamp, 1000)
        self.assertEqual(order.status, OrderStatus.OPEN)
        self.assertEqual(Order.next_id, 1)

    def test_order_market_execute_partial(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1050)
        order.execute(5)
        self.assertEqual(order.quantity, 10)
        self.assertEqual(order.status, OrderStatus.OPEN)

    def test_order_market_execute_full(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1100)
        order.execute(15)
        self.assertEqual(order.quantity, 0)
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_market_execute_over_quantity(self):
        order = OrderMarket(ticker='AAPL',quantity=15, side=OrderSide.SELL, time=1150)
        order.execute(20)
        self.assertEqual(order.quantity, 0)
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_market_execute_canceled(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1200)
        order.cancel()
        order.execute(5)
        self.assertEqual(order.quantity, 15)
        self.assertEqual(order.status, OrderStatus.CANCELED)

    def test_order_market_execute_expired(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1250)
        order.status = OrderStatus.EXPIRED
        order.execute(5)
        self.assertEqual(order.quantity, 15)
        self.assertEqual(order.status, OrderStatus.EXPIRED)

    def test_order_market_cancel_open(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1300)
        order.cancel()
        self.assertEqual(order.status, OrderStatus.CANCELED)

    def test_order_market_cancel_filled(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1350)
        order.execute(15)
        order.cancel()
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_market_cancel_already_canceled(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1400)
        order.cancel()
        order.cancel()
        self.assertEqual(order.status, OrderStatus.CANCELED)

    def test_order_market_is_active_open(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1450)
        self.assertTrue(order.is_active())

    def test_order_market_is_active_filled(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1500)
        order.execute(15)
        self.assertFalse(order.is_active())

    def test_order_market_is_active_canceled(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1550)
        order.cancel()
        self.assertFalse(order.is_active())

    def test_order_market_is_filled_true(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1600)
        order.execute(15)
        self.assertTrue(order.is_filled())

    def test_order_market_is_filled_false_open(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1650)
        self.assertFalse(order.is_filled())

    def test_order_market_is_filled_false_canceled(self):
        order = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1700)
        order.cancel()
        self.assertFalse(order.is_filled())

    def test_order_market_id_increment(self):
        order1 = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1750)
        order2 = OrderMarket(ticker='AAPL', quantity=10, side=OrderSide.BUY, time=1800)
        order3 = OrderMarket(ticker='AAPL', quantity=5, side=OrderSide.SELL, time=1850)
        self.assertEqual(order1.order_id, 0)
        self.assertEqual(order2.order_id, 1)
        self.assertEqual(order3.order_id, 2)
        self.assertEqual(Order.next_id, 3)

    def test_order_market_id_with_manual_id(self):
        order1 = OrderMarket(ticker='AAPL', quantity=15, side=OrderSide.SELL, time=1900, order_id=100)
        order2 = OrderMarket(ticker='AAPL', quantity=10, side=OrderSide.BUY, time=1950)
        order3 = OrderMarket(ticker='AAPL', quantity=5, side=OrderSide.SELL, time=2000)
        self.assertEqual(order1.order_id, 100)
        self.assertEqual(order2.order_id, 0)
        self.assertEqual(order3.order_id, 1)
        self.assertEqual(Order.next_id, 2)