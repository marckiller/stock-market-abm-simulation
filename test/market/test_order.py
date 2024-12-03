import unittest
from src.market.order import Order

class TestOrder(unittest.TestCase):

    def test_initialization_market_order(self):
        order = Order(order_id=1, agent_id=100, timestamp=1633057000.0, 
                      side='buy', order_type='market', quantity=50)
        self.assertEqual(order.order_id, 1)
        self.assertEqual(order.agent_id, 100)
        self.assertEqual(order.timestamp, 1633057000.0)
        self.assertEqual(order.side, 'buy')
        self.assertEqual(order.order_type, 'market')
        self.assertEqual(order.quantity, 50)
        self.assertIsNone(order.price)

    def test_initialization_limit_order(self):
        order = Order(order_id=2, agent_id=101, timestamp=1633058000.0, 
                      side='sell', order_type='limit', quantity=100, price=10.5)
        self.assertEqual(order.order_id, 2)
        self.assertEqual(order.agent_id, 101)
        self.assertEqual(order.timestamp, 1633058000.0)
        self.assertEqual(order.side, 'sell')
        self.assertEqual(order.order_type, 'limit')
        self.assertEqual(order.quantity, 100)
        self.assertEqual(order.price, 10.5)

    def test_initialization_limit_order_no_price(self):
        with self.assertRaises(ValueError):
            Order(order_id=3, agent_id=102, timestamp=1633059000.0, 
                  side='buy', order_type='limit', quantity=10)

    def test_modify_order_quantity(self):
        order = Order(order_id=4, agent_id=103, timestamp=1633060000.0, 
                      side='buy', order_type='market', quantity=20)
        order.modify_quantity(new_quantity=30)
        self.assertEqual(order.quantity, 30)

    def test_modify_order_no_quantity(self):
        order = Order(order_id=5, agent_id=104, timestamp=1633061000.0, 
                      side='sell', order_type='limit', quantity=40, price=15.0)
        with self.assertRaises(ValueError):
            order.modify_quantity()

    def test_str_representation(self):
        order = Order(order_id=6, agent_id=105, timestamp=1633062000.0, 
                      side='buy', order_type='market', quantity=10)
        self.assertEqual(str(order), 'Order 6 (buy 10 units) from agent 105')
