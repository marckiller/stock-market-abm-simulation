import unittest
from src.order.order_limit import OrderLimit
from src.order.order import OrderStatus, OrderSide, Order
from src.lob.lob_price_level import PriceLevel

class TestPriceLevel(unittest.TestCase):

    def setUp(self):
        self.price_level = PriceLevel(price=100.0)
        Order.next_id = 0

    def test_add(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        self.price_level.add(order1)
        self.assertEqual(self.price_level.number_of_orders, 1)
        self.assertEqual(len(self.price_level), 1)
        self.assertEqual(self.price_level.volume, 10)
        self.assertIn(order1, self.price_level)

    def test_add_wrong_type_order(self):
        from src.order.order_market import OrderMarket
        order1 = OrderMarket(quantity=10, side=OrderSide.BUY, time=1000)
        with self.assertRaises(ValueError):
            self.price_level.add(order1)

    def test_add_wrong_price_order(self):
        order1 = OrderLimit(price=101.0, quantity=10, side=OrderSide.BUY, time=1000)
        with self.assertRaises(ValueError):
            self.price_level.add(order1)

    def test_volume_after_add(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1000)
        self.price_level.add(order1)
        self.price_level.add(order2)
        self.assertEqual(self.price_level.volume, 30)

    def test_length_after_add(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1000)
        self.price_level.add(order1)
        self.price_level.add(order2)
        self.assertEqual(len(self.price_level), 2)

    def test_remove_order(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        self.price_level.add(order1)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1000)
        self.price_level.add(order2)

        self.price_level.remove(order1)
        self.assertEqual(self.price_level.number_of_orders, 1)
        self.assertEqual(len(self.price_level), 1)
        self.assertEqual(self.price_level.volume, 20)
        self.assertNotIn(order1, self.price_level)
    
    def test_remove_not_existing_order(self):
        order = OrderLimit(order_id=1, quantity=10, side=OrderSide.BUY, price=100.5, time=1000)
        with self.assertRaises(ValueError):
            self.price_level.remove(order)

    def test_get_first(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1000)
        self.price_level.add(order1)
        self.price_level.add(order2)
        first_order = self.price_level.get_first()
        self.assertEqual(first_order, order1)

    def test_get_first_order_empty(self):
        self.assertTrue(self.price_level.is_empty())
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        self.price_level.add(order1)
        self.assertFalse(self.price_level.is_empty())

    def test_pop_orders_to_meet_demand(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1001)
        order3 = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=1002)
        self.price_level.add(order1)
        self.price_level.add(order2)
        self.price_level.add(order3)

        #demand = 40
        orders_to_match = self.price_level.pop_orders_to_meet_demand(40)
        self.assertEqual(len(orders_to_match), 3)
        self.assertEqual(orders_to_match[0], (order1, 10))
        self.assertEqual(orders_to_match[1], (order2, 20))
        self.assertEqual(orders_to_match[2], (order3, 10))
        self.assertEqual(order1.quantity, 10)
        self.assertEqual(order2.quantity, 20)
        self.assertEqual(order3.quantity, 20) #las orders quantity should be reduced to 20
        
        self.assertEqual(self.price_level.number_of_orders, 1)
        self.assertEqual(self.price_level.volume, 20)

    def test_pop_orders_to_meet_demand_not_enough_orders(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1001)
        order3 = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=1002)

        self.price_level.add(order1)
        self.price_level.add(order2)
        self.price_level.add(order3)

        #demand = 70
        orders_to_match = self.price_level.pop_orders_to_meet_demand(70)
        self.assertEqual(len(orders_to_match), 3)
        self.assertEqual(orders_to_match[0], (order1, 10))
        self.assertEqual(orders_to_match[1], (order2, 20))
        self.assertEqual(orders_to_match[2], (order3, 30))

        self.assertEqual(order1.quantity, 10)
        self.assertEqual(order2.quantity, 20)
        self.assertEqual(order3.quantity, 30)

        self.assertEqual(self.price_level.number_of_orders, 0)
        self.assertEqual(self.price_level.volume, 0)
        self.assertTrue(self.price_level.is_empty())
        self.assertEqual(len(self.price_level), 0)

    def test_len_method(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1001)
        self.price_level.add(order1)
        self.price_level.add(order2)
        self.assertEqual(len(self.price_level), 2)

    def test_repr_method(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1001)
        self.price_level.add(order1)
        self.price_level.add(order2)
        self.assertEqual(repr(self.price_level), "PriceLevel(price=100.0, orders=2, volume=30)")

    def test_get_volume(self):
        order1 = OrderLimit(price=100.0, quantity=10, side=OrderSide.BUY, time=1000)
        order2 = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1001)
        self.price_level.add(order1)
        self.assertEqual(self.price_level.get_volume(), 10)
        self.price_level.add(order2)
        self.assertEqual(self.price_level.get_volume(), 30)

        


