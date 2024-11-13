import unittest
from src.order.order_limit import OrderLimit
from src.order.order import OrderType, OrderSide
from src.lob.lob_price_level import PriceLevel

class TestPriceLevel(unittest.TestCase):

    def setUp(self):
        self.price_level = PriceLevel(price=100)
        self.order1 = OrderLimit(agent_id = 0, ticker='AAPL', price=100, quantity=10, side=OrderSide.BUY, time= 1, order_id=1)
        self.order2 = OrderLimit(agent_id = 0, ticker='AAPL', price=100, quantity=20, side=OrderSide.BUY, time= 2, order_id=2)

    def test_add_order(self):
        self.price_level.add(self.order1)
        self.assertEqual(len(self.price_level), 1)
        self.assertEqual(self.price_level.get_volume(), 10)
        
        self.price_level.add(self.order2)
        self.assertEqual(len(self.price_level), 2)
        self.assertEqual(self.price_level.get_volume(), 30)

    def test_add_to_front(self):
        self.price_level.add(self.order1)
        self.price_level.add_to_front(self.order2)
        
        first_order = self.price_level.get_first()
        self.assertEqual(first_order.order_id, 2)
        self.assertEqual(len(self.price_level), 2)
        self.assertEqual(self.price_level.get_volume(), 30)

    def test_remove_order(self):
        self.price_level.add(self.order1)
        self.price_level.add(self.order2)
        
        removed_order = self.price_level.remove(self.order1)
        self.assertEqual(removed_order.order_id, 1)
        self.assertEqual(len(self.price_level), 1)
        self.assertEqual(self.price_level.get_volume(), 20)

        with self.assertRaises(ValueError):
            self.price_level.remove(self.order1)

    def test_pop_first_order(self):
        self.price_level.add(self.order1)
        self.price_level.add(self.order2)
        
        popped_order = self.price_level.pop_first_order()
        self.assertEqual(popped_order.order_id, 1)
        self.assertEqual(len(self.price_level), 1)
        self.assertEqual(self.price_level.get_volume(), 20)

    def test_get_first(self):
        self.assertIsNone(self.price_level.get_first())
        
        self.price_level.add(self.order1)
        first_order = self.price_level.get_first()
        self.assertEqual(first_order.order_id, 1)

    def test_is_empty(self):
        self.assertTrue(self.price_level.is_empty())
        
        self.price_level.add(self.order1)
        self.assertFalse(self.price_level.is_empty())

    def test_repr(self):
        self.price_level.add(self.order1)
        repr_str = repr(self.price_level)
        self.assertEqual(repr_str, "PriceLevel(price=100, orders=1, volume=10)")

    def test_get_volume(self):
        self.price_level.add(self.order1)
        self.assertEqual(self.price_level.get_volume(), 10)
        
        self.price_level.add(self.order2)
        self.assertEqual(self.price_level.get_volume(), 30)
