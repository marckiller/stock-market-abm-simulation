import unittest
from src.market.order import Order
from src.market.responses import LimitOrderStoredResponse, OrderCancelledResponse
from src.market.order_book import PriceLevel
from src.market.order_book import LimitOrderBook

class TestPriceLevel(unittest.TestCase):
    def setUp(self):
        self.price_level = PriceLevel(price=100.0)

    def test_add_order(self):
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        self.price_level.add_order(order)
        self.assertIn(order.order_id, self.price_level.orders)
        self.assertEqual(self.price_level.volume, 50)

    def test_remove_order(self):
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        self.price_level.add_order(order)
        removed_order = self.price_level.remove_order(order.order_id)
        self.assertEqual(removed_order, order)
        self.assertNotIn(order.order_id, self.price_level.orders)
        self.assertEqual(self.price_level.volume, 0)

    def test_modify_order(self):
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        self.price_level.add_order(order)
        modified_order = self.price_level.modify_order(order_id=1, new_quantity=30)
        self.assertEqual(modified_order.quantity, 30)
        self.assertEqual(self.price_level.volume, 30)

    def test_modify_order_to_zero_quantity(self):
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        self.price_level.add_order(order)
        self.price_level.modify_order(order_id=1, new_quantity=0)
        self.assertNotIn(order.order_id, self.price_level.orders)
        self.assertEqual(self.price_level.volume, 0)
        self.assertEqual(self.price_level.is_empty(), True)

    def test_top_order(self):
        order1 = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        order2 = Order(order_id=2, agent_id=11, timestamp=2.0, side='buy', order_type='limit', quantity=30, price=100.0)
        self.price_level.add_order(order1)
        self.price_level.add_order(order2)
        top_order = self.price_level.top_order()
        self.assertEqual(top_order, order1)

    def test_is_empty(self):
        self.assertTrue(self.price_level.is_empty())
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        self.price_level.add_order(order)
        self.assertFalse(self.price_level.is_empty())
        self.price_level.remove_order(order.order_id)
        self.assertTrue(self.price_level.is_empty())

class TestLimitOrderBook(unittest.TestCase):
    def setUp(self):
        self.order_book = LimitOrderBook()

    def test_add_order_buy(self):
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        response = self.order_book.add_order(order)
        self.assertIn(order.order_id, self.order_book.orders_by_id)
        self.assertEqual(self.order_book.bids_total_volume, 50)
        self.assertEqual(len(self.order_book.bids), 1)
        self.assertEqual(response.order_id, order.order_id)

    def test_add_order_sell(self):
        order = Order(order_id=2, agent_id=11, timestamp=1.0, side='sell', order_type='limit', quantity=30, price=101.0)
        response = self.order_book.add_order(order)
        self.assertIn(order.order_id, self.order_book.orders_by_id)
        self.assertEqual(self.order_book.asks_total_volume, 30)
        self.assertEqual(len(self.order_book.asks), 1)
        self.assertEqual(response.order_id, order.order_id)

    def test_remove_order(self):
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        self.order_book.add_order(order)
        response = self.order_book.remove_order(order.order_id)
        self.assertNotIn(order.order_id, self.order_book.orders_by_id)
        self.assertEqual(self.order_book.bids_total_volume, 0)
        self.assertEqual(len(self.order_book.bids), 0)
        self.assertEqual(response.order_id, order.order_id)

    def test_modify_order(self):
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        self.order_book.add_order(order)
        modified_order = self.order_book.modify_order(order_id=1, new_quantity=30)
        self.assertEqual(modified_order.quantity, 30)
        self.assertEqual(self.order_book.bids_total_volume, 30)

    def test_modify_order_to_zero_quantity(self):
        order = Order(order_id=1, agent_id=10, timestamp=1.0, side='sell', order_type='limit', quantity=50, price=101.0)
        self.order_book.add_order(order)
        self.order_book.modify_order(order_id=1, new_quantity=0)
        self.assertNotIn(order.order_id, self.order_book.orders_by_id)
        self.assertEqual(self.order_book.asks_total_volume, 0)
        self.assertEqual(len(self.order_book.asks), 0)

    def test_get_best_bid(self):
        order1 = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=99.0)
        order2 = Order(order_id=2, agent_id=11, timestamp=1.1, side='buy', order_type='limit', quantity=50, price=100.0)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)
        best_bid = self.order_book.get_best_bid()
        self.assertEqual(best_bid, 100.0)

    def test_get_best_ask(self):
        order1 = Order(order_id=1, agent_id=10, timestamp=1.0, side='sell', order_type='limit', quantity=50, price=101.0)
        order2 = Order(order_id=2, agent_id=11, timestamp=1.1, side='sell', order_type='limit', quantity=50, price=100.0)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)
        best_ask = self.order_book.get_best_ask()
        self.assertEqual(best_ask, 100.0)

    def test_top_bid(self):
        order1 = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        order2 = Order(order_id=2, agent_id=11, timestamp=1.1, side='buy', order_type='limit', quantity=30, price=100.0)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)
        top_bid_order = self.order_book.top_bid()
        self.assertEqual(top_bid_order, order1)

    def test_top_ask(self):
        order1 = Order(order_id=1, agent_id=10, timestamp=1.0, side='sell', order_type='limit', quantity=50, price=100.0)
        order2 = Order(order_id=2, agent_id=11, timestamp=1.1, side='sell', order_type='limit', quantity=30, price=100.0)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)
        top_ask_order = self.order_book.top_ask()
        self.assertEqual(top_ask_order, order1)

    def test_get_orders_at_price(self):
        order1 = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=50, price=100.0)
        order2 = Order(order_id=2, agent_id=11, timestamp=1.1, side='buy', order_type='limit', quantity=30, price=100.0)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)
        orders_at_price = self.order_book.get_orders_at_price(price=100.0, side='buy')
        self.assertEqual(len(orders_at_price), 2)
        self.assertIn(order1.order_id, orders_at_price)
        self.assertIn(order2.order_id, orders_at_price)

    def test_get_depth(self):
        order1 = Order(order_id=1, agent_id=10, timestamp=1.0, side='sell', order_type='limit', quantity=50, price=101.0)
        order2 = Order(order_id=2, agent_id=11, timestamp=1.1, side='sell', order_type='limit', quantity=30, price=101.0)
        order3 = Order(order_id=3, agent_id=12, timestamp=1.2, side='sell', order_type='limit', quantity=20, price=102.0)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)
        self.order_book.add_order(order3)
        depth = self.order_book.get_depth(side='sell')
        expected_depth = {101.0: 80, 102.0: 20}
        self.assertEqual(depth, expected_depth)

    def test_total_volume(self):
        order1 = Order(order_id=1, agent_id=10, timestamp=1.0, side='buy', order_type='limit', quantity=40, price=99.0)
        order2 = Order(order_id=2, agent_id=11, timestamp=1.1, side='buy', order_type='limit', quantity=60, price=100.0)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)
        self.assertEqual(self.order_book.get_total_bid_volume(), 100)
        self.assertEqual(self.order_book.get_total_ask_volume(), 0)

    def test_remove_nonexistent_order(self):
        response = self.order_book.remove_order(order_id=999)
        self.assertIsNone(response)

    def test_modify_nonexistent_order(self):
        modified_order = self.order_book.modify_order(order_id=999, new_quantity=50)
        self.assertIsNone(modified_order)

    def test_get_orders_at_nonexistent_price(self):
        orders_at_price = self.order_book.get_orders_at_price(price=200.0, side='buy')
        self.assertEqual(len(orders_at_price), 0)

    def test_get_depth_empty_book(self):
        depth = self.order_book.get_depth(side='sell')
        self.assertEqual(depth, {})