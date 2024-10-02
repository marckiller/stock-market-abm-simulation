import unittest
from src.lob.lob_limit_order_book import LimitOrderBook
from src.order.order_limit import OrderLimit
from src.order.order import Order
from src.order.order import OrderSide, OrderType
from src.lob.lob_price_level import PriceLevel

class TestLimitOrderBook(unittest.TestCase):

    def setUp(self):
        Order.next_id = 0

    def test_add_order(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        lob.add(order1)

        self.assertEqual(lob.best_bid(), 100.0)
        self.assertEqual(len(lob.sorted_bids), 1)
        self.assertEqual(lob.sorted_bids[0], -100.0)
        self.assertEqual(lob.get_price_level_volume(100.0, OrderSide.BUY), 50)

    def test_add_multiple_orders(self):
        lob = LimitOrderBook()
        orders = [
            OrderLimit(price=101.0, quantity=50, side=OrderSide.BUY, time=1),
            OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2),
            OrderLimit(price=102.0, quantity=20, side=OrderSide.BUY, time=3),
        ]
        for order in orders:
            lob.add(order)

        self.assertEqual(lob.best_bid(), 102.0)
        self.assertEqual(lob.sorted_bids, [-102.0, -101.0, -100.0])
        self.assertEqual(lob.get_price_level_volume(102.0, OrderSide.BUY), 20)

    def test_remove_order_by_id(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        order2 = OrderLimit(price=101.0, quantity=30, side=OrderSide.SELL, time=2)
        lob.add(order1)
        lob.add(order2)

        self.assertEqual(lob.best_ask(), 100.0)
        lob.remove_order_by_id(order1.order_id)
        self.assertEqual(lob.best_ask(), 101.0)
        self.assertEqual(len(lob.sorted_asks), 1)
        self.assertNotIn(100.0, lob.sorted_asks)

    def test_pop_orders_from_given_price_level_to_meet_demand(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        lob.add(order1)

        orders = lob.pop_orders_from_given_price_level_to_meet_demand(price=100.0, side=OrderSide.BUY, demand=30)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0], (order1, 30))
        self.assertEqual(lob.get_price_level_volume(100.0, OrderSide.BUY), 0)
        self.assertEqual(len(lob.sorted_bids), 1)
        #self.assertIsNone(lob.best_bid())

    def test_pop_orders_with_partial_fill(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        lob.add(order1)

        orders = lob.pop_orders_from_given_price_level_to_meet_demand(price=100.0, side=OrderSide.SELL, demand=70)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0], (order1, 50))
        self.assertEqual(lob.get_price_level_volume(100.0, OrderSide.SELL), 0)
        self.assertEqual(len(lob.sorted_asks), 0)
        self.assertIsNone(lob.best_ask())

    def test_order_map_consistency(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        lob.add(order1)

        self.assertIn(order1.order_id, lob.order_map)
        lob.remove_order_by_id(order1.order_id)
        self.assertNotIn(order1.order_id, lob.order_map)

    def test_best_bid_and_ask(self):
        lob = LimitOrderBook()
        self.assertIsNone(lob.best_bid())
        self.assertIsNone(lob.best_ask())

        order_buy = OrderLimit(price=99.0, quantity=50, side=OrderSide.BUY, time=1)
        order_sell = OrderLimit(price=101.0, quantity=50, side=OrderSide.SELL, time=1)
        lob.add(order_buy)
        lob.add(order_sell)

        self.assertEqual(lob.best_bid(), 99.0)
        self.assertEqual(lob.best_ask(), 101.0)

    def test_get_order(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        lob.add(order1)

        retrieved_order = lob.get_order(order1.order_id)
        self.assertEqual(retrieved_order, order1)

    def test_remove_nonexistent_order(self):
        lob = LimitOrderBook()
        with self.assertRaises(ValueError):
            lob.remove_order_by_id(999)

    def test_add_order_with_same_price(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        order2 = OrderLimit(price=100.0, quantity=30, side=OrderSide.SELL, time=2)
        lob.add(order1)
        lob.add(order2)

        self.assertEqual(len(lob.asks), 1)
        self.assertEqual(lob.get_price_level_volume(100.0, OrderSide.SELL), 80)
        self.assertEqual(lob.sorted_asks, [100.0])

    def test_pop_orders_with_multiple_price_levels(self):
        lob = LimitOrderBook()
        orders = [
            OrderLimit(price=101.0, quantity=50, side=OrderSide.BUY, time=1),
            OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2),
        ]
        for order in orders:
            lob.add(order)

        orders_popped = lob.pop_orders_from_given_price_level_to_meet_demand(price=101.0, side=OrderSide.BUY, demand=50)
        self.assertEqual(len(orders_popped), 1)
        self.assertEqual(orders_popped[0], (orders[0], 50))
        self.assertEqual(lob.best_bid(), 100.0)

    def test_partial_fill_and_readd(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        lob.add(order1)

        #Pop 30 units from the order
        orders = lob.pop_orders_from_given_price_level_to_meet_demand(price=100.0, side=OrderSide.SELL, demand=30)
        self.assertEqual(orders[0], (order1, 30))
        self.assertEqual(lob.get_price_level_volume(100.0, OrderSide.SELL), 0)
        self.assertEqual(len(lob.sorted_asks), 1) #price level is keeped because partial order is expected back

        #Simulate matching engine updating the order and re-adding it
        remaining_order = OrderLimit(price=100.0, quantity=20, side=OrderSide.SELL, time=1, order_id=order1.order_id)
        lob.add(remaining_order)
        self.assertEqual(lob.get_price_level_volume(100.0, OrderSide.SELL), 20)
        self.assertEqual(len(lob.sorted_asks), 1)

    def test_remove_price_level_after_order_removal(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        lob.add(order1)
        lob.remove_order_by_id(order1.order_id)

        self.assertEqual(len(lob.sorted_bids), 0)
        self.assertIsNone(lob.best_bid())

    def test_get_price_level_volume_nonexistent(self):
        lob = LimitOrderBook()
        volume = lob.get_price_level_volume(price=100.0, side=OrderSide.BUY)
        self.assertEqual(volume, 0)

    def test_order_map_after_partial_fill(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        lob.add(order1)

        orders = lob.pop_orders_from_given_price_level_to_meet_demand(price=100.0, side=OrderSide.BUY, demand=30)
        self.assertNotIn(order1.order_id, lob.order_map)

        remaining_order = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=1, order_id=order1.order_id)
        lob.add(remaining_order)
        self.assertIn(order1.order_id, lob.order_map)

    def test_repr(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        lob.add(order1)
        repr_str = repr(lob)
        self.assertIn("LimitOrderBook(bids=1, asks=0)", repr_str)

    def test_negative_prices_in_sorted_bids(self):
        lob = LimitOrderBook()
        orders = [
            OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1),
            OrderLimit(price=101.0, quantity=30, side=OrderSide.BUY, time=2),
            OrderLimit(price=99.0, quantity=20, side=OrderSide.BUY, time=3),
        ]
        for order in orders:
            lob.add(order)

        expected_sorted_bids = [-101.0, -100.0, -99.0]
        self.assertEqual(lob.sorted_bids, expected_sorted_bids)
        self.assertEqual(lob.best_bid(), 101.0)

    def test_add_order_with_negative_price(self):
        lob = LimitOrderBook()
        with self.assertRaises(ValueError):
            order = OrderLimit(price=-100.0, quantity=50, side=OrderSide.BUY, time=1)
            lob.add(order)

    def test_get_price_level_volume_with_negative_prices(self):
        lob = LimitOrderBook()
        order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=1)
        lob.add(order1)
        volume = lob.get_price_level_volume(100.0, OrderSide.BUY)
        self.assertEqual(volume, 50)

    def test_pop_orders_with_no_matching_price_level(self):
        lob = LimitOrderBook()
        orders = lob.pop_orders_from_given_price_level_to_meet_demand(price=100.0, side=OrderSide.BUY, demand=50)
        self.assertEqual(len(orders), 0)
