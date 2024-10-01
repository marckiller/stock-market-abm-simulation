import unittest
from src.order.order import Order, OrderSide, OrderType, OrderStatus
from src.order.order_limit import OrderLimit

class TestOrderLimit(unittest.TestCase):

    def setUp(self):
        import src.order.order
        src.order.order.Order.next_id = 0

    def test_order_limit_initialization_without_expiration(self):
        order = OrderLimit(price=100.5, quantity=10, side=OrderSide.BUY, time=1000)
        self.assertEqual(order.order_id, 0)
        self.assertEqual(order.price, 100.5)
        self.assertEqual(order.quantity, 10)
        self.assertEqual(order.side, OrderSide.BUY)
        self.assertEqual(order.type, OrderType.LIMIT)
        self.assertEqual(order.timestamp, 1000)
        self.assertIsNone(order.expiration_time)
        self.assertEqual(order.status, OrderStatus.OPEN)
        self.assertEqual(Order.next_id, 1)

    def test_order_limit_initialization_with_expiration(self):
        expiration = 1600
        order = OrderLimit(price=101.0, quantity=5, side=OrderSide.SELL, time=1050, expiration_time=expiration)
        self.assertEqual(order.order_id, 0)
        self.assertEqual(order.price, 101.0)
        self.assertEqual(order.quantity, 5)
        self.assertEqual(order.side, OrderSide.SELL)
        self.assertEqual(order.type, OrderType.LIMIT)
        self.assertEqual(order.timestamp, 1050)
        self.assertEqual(order.expiration_time, expiration)
        self.assertEqual(order.status, OrderStatus.OPEN)
        self.assertEqual(Order.next_id, 1)

    def test_order_limit_execute_partial(self):
        order = OrderLimit(price=102.0, quantity=10, side=OrderSide.BUY, time=1100)
        order.execute(3)
        self.assertEqual(order.quantity, 7)
        self.assertEqual(order.status, OrderStatus.OPEN)

    def test_order_limit_execute_full(self):
        order = OrderLimit(price=103.0, quantity=10, side=OrderSide.BUY, time=1150)
        order.execute(10)
        self.assertEqual(order.quantity, 0)
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_limit_execute_over_quantity(self):
        order = OrderLimit(price=104.0, quantity=10, side=OrderSide.BUY, time=1200)
        order.execute(15)
        self.assertEqual(order.quantity, 0)
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_limit_execute_canceled(self):
        order = OrderLimit(price=105.0, quantity=10, side=OrderSide.BUY, time=1250)
        order.cancel()
        order.execute(5)
        self.assertEqual(order.quantity, 10)
        self.assertEqual(order.status, OrderStatus.CANCELED)

    def test_order_limit_execute_expired(self):
        order = OrderLimit(price=106.0, quantity=10, side=OrderSide.BUY, time=1300)
        order.status = OrderStatus.EXPIRED
        order.execute(5)
        self.assertEqual(order.quantity, 10)
        self.assertEqual(order.status, OrderStatus.EXPIRED)

    def test_order_limit_cancel_open(self):
        order = OrderLimit(price=107.0, quantity=10, side=OrderSide.BUY, time=1350)
        order.cancel()
        self.assertEqual(order.status, OrderStatus.CANCELED)

    def test_order_limit_cancel_filled(self):
        order = OrderLimit(price=108.0, quantity=10, side=OrderSide.BUY, time=1400)
        order.execute(10)
        order.cancel()
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_limit_cancel_already_canceled(self):
        order = OrderLimit(price=109.0, quantity=10, side=OrderSide.BUY, time=1450)
        order.cancel()
        order.cancel()
        self.assertEqual(order.status, OrderStatus.CANCELED)

    def test_order_limit_is_active_open(self):
        order = OrderLimit(price=110.0, quantity=10, side=OrderSide.BUY, time=1500)
        self.assertTrue(order.is_active())

    def test_order_limit_is_active_filled(self):
        order = OrderLimit(price=111.0, quantity=10, side=OrderSide.BUY, time=1550)
        order.execute(10)
        self.assertFalse(order.is_active())

    def test_order_limit_is_active_canceled(self):
        order = OrderLimit(price=112.0, quantity=10, side=OrderSide.BUY, time=1600)
        order.cancel()
        self.assertFalse(order.is_active())

    def test_order_limit_is_filled_true(self):
        order = OrderLimit(price=113.0, quantity=10, side=OrderSide.BUY, time=1650)
        order.execute(10)
        self.assertTrue(order.is_filled())

    def test_order_limit_is_filled_false_open(self):
        order = OrderLimit(price=114.0, quantity=10, side=OrderSide.BUY, time=1700)
        self.assertFalse(order.is_filled())

    def test_order_limit_is_filled_false_canceled(self):
        order = OrderLimit(price=115.0, quantity=10, side=OrderSide.BUY, time=1750)
        order.cancel()
        self.assertFalse(order.is_filled())

    def test_order_limit_expire(self):
        order = OrderLimit(price=116.0, quantity=10, side=OrderSide.BUY, time=1800, expiration_time=1900)
        order.expire()
        self.assertEqual(order.status, OrderStatus.EXPIRED)

    def test_order_limit_expire_only_if_open(self):
        order = OrderLimit(price=117.0, quantity=10, side=OrderSide.BUY, time=1850)
        order.execute(10)  # Status FILLED
        order.expire()
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_limit_id_increment(self):
        order1 = OrderLimit(price=118.0, quantity=10, side=OrderSide.BUY, time=1900)
        order2 = OrderLimit(price=119.0, quantity=5, side=OrderSide.SELL, time=1950)
        order3 = OrderLimit(price=120.0, quantity=7, side=OrderSide.BUY, time=2000)
        self.assertEqual(order1.order_id, 0)
        self.assertEqual(order2.order_id, 1)
        self.assertEqual(order3.order_id, 2)
        self.assertEqual(Order.next_id, 3)

    def test_order_limit_id_with_manual_id(self):
        order1 = OrderLimit(price=121.0, quantity=10, side=OrderSide.BUY, time=2050, order_id=100)
        order2 = OrderLimit(price=122.0, quantity=5, side=OrderSide.SELL, time=2100)
        order3 = OrderLimit(price=123.0, quantity=7, side=OrderSide.BUY, time=2150)
        self.assertEqual(order1.order_id, 100)
        self.assertEqual(order2.order_id, 0)
        self.assertEqual(order3.order_id, 1)
        self.assertEqual(Order.next_id, 2)
