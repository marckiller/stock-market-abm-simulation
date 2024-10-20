import unittest
from src.order.order import Order, OrderSide, OrderType, OrderStatus

class OrderDummy(Order):
    ORDER_TYPE = None

class TestOrderInitialization(unittest.TestCase):
    
    def setUp(self):
        Order.next_id = 0

    def test_order_initialization_without_order_type(self):
        with self.assertRaises(ValueError) as context:
            OrderDummy(ticker='AAPL', quantity=10, side=OrderSide.BUY, time=1000)
        self.assertEqual(str(context.exception), "ORDER_TYPE must be set in child class.")

class TestOrderBehavior(unittest.TestCase):
    
    def setUp(self):
        Order.next_id = 0

    def test_order_execute_canceled(self):
        from src.order.order_limit import OrderLimit
        order = OrderLimit(ticker='AAPL', price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order.cancel()
        order.execute(5)
        self.assertEqual(order.quantity, 10)
        self.assertEqual(order.status, OrderStatus.CANCELED)

    def test_order_execute_filled(self):
        from src.order.order_limit import OrderLimit
        order = OrderLimit(ticker='AAPL', price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order.execute(10)
        self.assertEqual(order.quantity, 0)
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_cancel_filled(self):
        from src.order.order_limit import OrderLimit
        order = OrderLimit(ticker='AAPL', price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order.execute(10)
        order.cancel()
        self.assertEqual(order.status, OrderStatus.FILLED)

    def test_order_is_active_open(self):
        from src.order.order_limit import OrderLimit
        order = OrderLimit(ticker='AAPL', price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        self.assertTrue(order.is_active())

    def test_order_is_active_canceled(self):
        from src.order.order_limit import OrderLimit
        order = OrderLimit(ticker='AAPL', price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order.cancel()
        self.assertFalse(order.is_active())

    def test_order_is_filled_true(self):
        from src.order.order_limit import OrderLimit
        order = OrderLimit(ticker='AAPL', price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order.execute(10)
        self.assertTrue(order.is_filled())

    def test_order_is_filled_false_open(self):
        from src.order.order_limit import OrderLimit
        order = OrderLimit(ticker='AAPL', price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        self.assertFalse(order.is_filled())

    def test_order_is_filled_false_canceled(self):
        from src.order.order_limit import OrderLimit
        order = OrderLimit(ticker='AAPL', price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order.cancel()
        self.assertFalse(order.is_filled())

    def test_eq(self):
        from src.order.order_limit import OrderLimit 
        order1 = OrderLimit(ticker='AAPL', price=10.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(ticker='AAPL', price=10.0, quantity=10, side=OrderSide.BUY, time=1000)
        self.assertFalse(order1 == order2)
        self.assertTrue(order1 == order1)
