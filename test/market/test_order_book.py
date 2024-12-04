import unittest
from src.market.order import Order
from src.market.order_book import PriceLevel, LimitOrderBook

class TestPriceLevel(unittest.TestCase):
    def test_add_order(self):
        price_level = PriceLevel(100.5)
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        price_level.add_order(order)
        
        self.assertIn(order.order_id, price_level.orders)
        self.assertEqual(price_level.volume, 10)

    def test_remove_order(self):
        price_level = PriceLevel(100.5)
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        price_level.add_order(order)
        
        removed_order = price_level.remove_order(order.order_id)
        self.assertEqual(removed_order, order)
        self.assertNotIn(order.order_id, price_level.orders)
        self.assertEqual(price_level.volume, 0)

    def test_modify_order(self):
        price_level = PriceLevel(100.5)
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        price_level.add_order(order)
        
        modified_order = price_level.modify_order(order.order_id, 15)
        self.assertEqual(modified_order.quantity, 15)
        self.assertEqual(price_level.volume, 15)

    def test_top_order(self):
        price_level = PriceLevel(100.5)
        order1 = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        order2 = Order(2, 3, 1234567891, 'buy', 'limit', 5, 100.5)
        price_level.add_order(order1)
        price_level.add_order(order2)
        
        self.assertEqual(price_level.top_order(), order1)

    def test_is_empty(self):
        price_level = PriceLevel(100.5)
        self.assertTrue(price_level.is_empty())
        
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        price_level.add_order(order)
        self.assertFalse(price_level.is_empty())

class TestLimitOrderBook(unittest.TestCase):
    def setUp(self):
        self.order_book = LimitOrderBook()

    def test_add_order(self):
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        self.order_book.add_order(order)

        self.assertIn(order.order_id, self.order_book.orders_by_id)
        self.assertEqual(self.order_book.get_total_bid_volume(), 10)

    def test_remove_order(self):
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        self.order_book.add_order(order)
        removed_order = self.order_book.remove_order(order.order_id)

        self.assertEqual(removed_order, order)
        self.assertNotIn(order.order_id, self.order_book.orders_by_id)
        self.assertEqual(self.order_book.get_total_bid_volume(), 0)

    def test_modify_order(self):
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        self.order_book.add_order(order)
        self.order_book.modify_order(order.order_id, 5)

        self.assertEqual(self.order_book.orders_by_id[order.order_id].quantity, 5)
        self.assertEqual(self.order_book.get_total_bid_volume(), 5)

    def test_get_best_bid_ask(self):
        order1 = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        order2 = Order(2, 3, 1234567891, 'sell', 'limit', 5, 101.5)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)

        self.assertEqual(self.order_book.get_best_bid(), 100.5)
        self.assertEqual(self.order_book.get_best_ask(), 101.5)

    def test_top_bid_ask(self):
        order1 = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        order2 = Order(2, 3, 1234567891, 'sell', 'limit', 5, 101.5)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)

        self.assertEqual(self.order_book.top_bid(), order1)
        self.assertEqual(self.order_book.top_ask(), order2)

    def test_get_volume_at_price(self):
        order1 = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        order2 = Order(2, 3, 1234567891, 'buy', 'limit', 5, 100.5)
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)

        self.assertEqual(self.order_book.get_volume_at_price(100.5, 'buy'), 15)

    def test_remove_nonexistent_order(self):
        removed_order = self.order_book.remove_order(999)
        self.assertIsNone(removed_order)

    def test_modify_nonexistent_order(self):
        result = self.order_book.modify_order(999, 5)
        self.assertIsNone(result)
