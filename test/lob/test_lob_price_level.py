import unittest
from typing import List
from src.order.order import OrderType, OrderSide
from src.order.order_limit import OrderLimit
from src.lob.lob_price_level import PriceLevel


class TestPriceLevel(unittest.TestCase):
    def setUp(self):
        OrderLimit.next_id = 0

    def test_initialization(self):
        price_level = PriceLevel(price=100.0)
        self.assertEqual(price_level.price, 100.0)
        self.assertEqual(price_level.number_of_orders, 0)
        self.assertEqual(price_level.volume, 0)
        self.assertTrue(price_level.is_empty())
        self.assertIsNone(price_level.last_partial_order_id)

    def test_add_order(self):
        price_level = PriceLevel(price=100.0)
        order = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        price_level.add(order)

        self.assertEqual(price_level.number_of_orders, 1)
        self.assertEqual(price_level.volume, 50)
        self.assertFalse(price_level.is_empty())
        self.assertEqual(price_level.get_first(), order)
        self.assertIsNone(price_level.last_partial_order_id)

    def test_add_order_invalid_type(self):
        price_level = PriceLevel(price=100.0)
        order = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        order.type = OrderType.MARKET  # Force invalid type

        with self.assertRaises(ValueError) as context:
            price_level.add(order)
        self.assertIn("PriceLevel accepts only LIMIT orders", str(context.exception))

    def test_add_order_invalid_price(self):
        price_level = PriceLevel(price=100.0)
        order = OrderLimit(price=101.0, quantity=50, side=OrderSide.BUY, time=1)

        with self.assertRaises(ValueError) as context:
            price_level.add(order)
        self.assertIn("PriceLevel accepts only orders with the same price", str(context.exception))

    def test_remove_order(self):
        price_level = PriceLevel(price=100.0)
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        order2 = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2)
        price_level.add(order1)
        price_level.add(order2)

        price_level.remove(order1)
        self.assertEqual(price_level.number_of_orders, 1)
        self.assertEqual(price_level.volume, 30)
        self.assertEqual(price_level.get_first(), order2)

        price_level.remove(order2)
        self.assertTrue(price_level.is_empty())
        self.assertEqual(price_level.number_of_orders, 0)
        self.assertEqual(price_level.volume, 0)

    def test_remove_order_not_found(self):
        price_level = PriceLevel(price=100.0)
        order = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)

        with self.assertRaises(ValueError) as context:
            price_level.remove(order)
        self.assertIn("No Order with id", str(context.exception))

    def test_get_first(self):
        price_level = PriceLevel(price=100.0)
        self.assertIsNone(price_level.get_first())

        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        order2 = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2)
        price_level.add(order1)
        price_level.add(order2)

        self.assertEqual(price_level.get_first(), order1)

    def test_iteration(self):
        price_level = PriceLevel(price=100.0)
        orders = [
            OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1),
            OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2),
            OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=3),
        ]
        for order in orders:
            price_level.add(order)

        for idx, order in enumerate(price_level):
            self.assertEqual(order, orders[idx])

    def test_length(self):
        price_level = PriceLevel(price=100.0)
        self.assertEqual(len(price_level), 0)

        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        price_level.add(order1)
        self.assertEqual(len(price_level), 1)

        order2 = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2)
        price_level.add(order2)
        self.assertEqual(len(price_level), 2)

    def test_pop_orders_to_meet_demand_full_fill(self):
        price_level = PriceLevel(price=100.0)
        orders = [
            OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1),
            OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2),
        ]
        for order in orders:
            price_level.add(order)

        fulfilled_orders = price_level.pop_orders_to_meet_demand(80)
        self.assertEqual(len(fulfilled_orders), 2)
        self.assertEqual(fulfilled_orders[0], (orders[0], 50))
        self.assertEqual(fulfilled_orders[1], (orders[1], 30))
        self.assertEqual(price_level.number_of_orders, 0)
        self.assertEqual(price_level.volume, 0)
        self.assertIsNone(price_level.last_partial_order_id)
        self.assertTrue(price_level.is_empty())

    def test_pop_orders_to_meet_demand_partial_fill(self):
        price_level = PriceLevel(price=100.0)
        order1 = OrderLimit(price=100.0, quantity=100, side=OrderSide.BUY, time=1)
        price_level.add(order1)

        fulfilled_orders = price_level.pop_orders_to_meet_demand(60)
        self.assertEqual(len(fulfilled_orders), 1)
        self.assertEqual(fulfilled_orders[0], (order1, 60))
        self.assertEqual(price_level.number_of_orders, 0)
        self.assertEqual(price_level.volume, 0)
        self.assertEqual(price_level.last_partial_order_id, order1.order_id)
        self.assertTrue(price_level.is_empty())

        remaining_order = OrderLimit(
            price=100.0,
            quantity=40,
            side=OrderSide.BUY,
            time=1,
            order_id=order1.order_id,
        )

        price_level.add(remaining_order)
        self.assertEqual(price_level.number_of_orders, 1)
        self.assertEqual(price_level.volume, 40)
        self.assertIsNone(price_level.last_partial_order_id)
        self.assertFalse(price_level.is_empty())
        self.assertEqual(price_level.get_first(), remaining_order)

    def test_pop_orders_to_meet_demand_exact_fill(self):
        price_level = PriceLevel(price=100.0)
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        order2 = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2)
        price_level.add(order1)
        price_level.add(order2)

        fulfilled_orders = price_level.pop_orders_to_meet_demand(80)
        self.assertEqual(len(fulfilled_orders), 2)
        self.assertEqual(fulfilled_orders[0], (order1, 50))
        self.assertEqual(fulfilled_orders[1], (order2, 30))
        self.assertEqual(price_level.number_of_orders, 0)
        self.assertEqual(price_level.volume, 0)
        self.assertIsNone(price_level.last_partial_order_id)
        self.assertTrue(price_level.is_empty())

    def test_pop_orders_to_meet_demand_more_than_available(self):
        price_level = PriceLevel(price=100.0)
        orders = [
            OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1),
            OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2),
        ]
        for order in orders:
            price_level.add(order)

        fulfilled_orders = price_level.pop_orders_to_meet_demand(100)
        self.assertEqual(len(fulfilled_orders), 2)
        self.assertEqual(fulfilled_orders[0], (orders[0], 50))
        self.assertEqual(fulfilled_orders[1], (orders[1], 30))
        self.assertEqual(price_level.number_of_orders, 0)
        self.assertEqual(price_level.volume, 0)
        self.assertTrue(price_level.is_empty())
        self.assertIsNone(price_level.last_partial_order_id)

    def test_pop_orders_to_meet_demand_no_orders(self):
        price_level = PriceLevel(price=100.0)
        fulfilled_orders = price_level.pop_orders_to_meet_demand(50)
        self.assertEqual(len(fulfilled_orders), 0)
        self.assertEqual(price_level.number_of_orders, 0)
        self.assertEqual(price_level.volume, 0)
        self.assertTrue(price_level.is_empty())
        self.assertIsNone(price_level.last_partial_order_id)

    def test_pop_orders_to_meet_demand_zero_demand(self):
        price_level = PriceLevel(price=100.0)
        order = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        price_level.add(order)

        fulfilled_orders = price_level.pop_orders_to_meet_demand(0)
        self.assertEqual(len(fulfilled_orders), 0)
        self.assertEqual(price_level.number_of_orders, 1)
        self.assertEqual(price_level.volume, 50)
        self.assertFalse(price_level.is_empty())
        self.assertIsNone(price_level.last_partial_order_id)

    def test_get_volume(self):
        price_level = PriceLevel(price=100.0)
        self.assertEqual(price_level.get_volume(), 0)

        order1 = OrderLimit(price=100.0, quantity=40, side=OrderSide.BUY, time=1)
        price_level.add(order1)
        self.assertEqual(price_level.get_volume(), 40)

        order2 = OrderLimit(price=100.0, quantity=60, side=OrderSide.BUY, time=2)
        price_level.add(order2)
        self.assertEqual(price_level.get_volume(), 100)

    def test_last_partial_order_id_reset(self):
        price_level = PriceLevel(price=100.0)
        order = OrderLimit(price=100.0, quantity=100, side=OrderSide.BUY, time=1)
        price_level.add(order)

        fulfilled_orders = price_level.pop_orders_to_meet_demand(30)
        self.assertEqual(price_level.last_partial_order_id, order.order_id)

        remaining_order = OrderLimit(
            price=100.0,
            quantity=70,
            side=OrderSide.BUY,
            time=1,
            order_id=order.order_id,
        )

        price_level.add(remaining_order)
        self.assertIsNone(price_level.last_partial_order_id)

        fulfilled_orders = price_level.pop_orders_to_meet_demand(70)
        self.assertEqual(len(fulfilled_orders), 1)
        self.assertEqual(fulfilled_orders[0], (remaining_order, 70))
        self.assertEqual(price_level.number_of_orders, 0)
        self.assertEqual(price_level.volume, 0)
        self.assertIsNone(price_level.last_partial_order_id)

    def test_add_same_order_id_new_order(self):
        price_level = PriceLevel(price=100.0)
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1, order_id=1)
        order2 = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2, order_id=1)  # Same ID

        price_level.add(order1)
        price_level.add(order2)

        self.assertEqual(price_level.number_of_orders, 2)
        self.assertEqual(price_level.volume, 80)
        self.assertEqual(len(price_level.orders), 2)
        self.assertEqual(price_level.orders[0], order1)
        self.assertEqual(price_level.orders[1], order2)

    def test_add_partial_order_with_different_id(self):
        price_level = PriceLevel(price=100.0)
        order = OrderLimit(price=100.0, quantity=100, side=OrderSide.BUY, time=1, order_id=1)
        order2 = OrderLimit(price=100.0, quantity=40, side=OrderSide.BUY, time=1, order_id=10)
        price_level.add(order)
        price_level.add(order2)

        self.assertEqual(len(price_level), 2)
        self.assertEqual(price_level.volume, 140)

        fulfilled_orders = price_level.pop_orders_to_meet_demand(60)
        self.assertEqual(price_level.last_partial_order_id, 1)
        self.assertEqual(len(price_level), 1)
        self.assertEqual(price_level.volume, 40)

        #Simulate matching engine adjusting order quantity
        #but accidentally assigns a different order_id
        remaining_order = OrderLimit(
            price=100.0,
            quantity=40,
            side=OrderSide.BUY,
            time=1,
            order_id=2,
        )

        price_level.add(remaining_order)
        self.assertEqual(price_level.number_of_orders, 2)
        self.assertEqual(price_level.volume, 80)
        self.assertEqual(price_level.orders[-1], remaining_order)
        self.assertNotEqual(price_level.orders[0], remaining_order)
        self.assertIsNone(price_level.last_partial_order_id)

    def test_order_equality(self):
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        order2 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        self.assertNotEqual(order1, order2)

        order3 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1, order_id=order1.order_id)
        self.assertEqual(order1, order3)

    def test_repr(self):
        price_level = PriceLevel(price=100.0)
        order = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        price_level.add(order)
        repr_str = repr(price_level)
        self.assertIn("PriceLevel(price=100.0, orders=1, volume=50)", repr_str)
