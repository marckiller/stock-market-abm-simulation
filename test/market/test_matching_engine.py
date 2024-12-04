import unittest
from unittest.mock import MagicMock
from src.market.matching_engine import MatchingEngine
from src.market.order_book import LimitOrderBook
from src.market.order import Order
from src.market.transaction import Transaction
from src.market.events import TransactionEvent, OrderExecutedEvent, OrderCancelledEvent, LimitOrderStoredEvent


class TestMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.event_bus = MagicMock()
        self.matching_engine = MatchingEngine(self.event_bus)
        self.order_book = LimitOrderBook()

    def test_execute_market_order_no_match(self):
        """Test executing a market order with no matching orders."""
        market_order = Order(1, 2, 1234567890, 'buy', 'market', 10)
        self.matching_engine.execute_order(market_order, self.order_book, timestamp=1234567890)

        self.assertEqual(market_order.quantity, 10)
        self.event_bus.publish.assert_not_called()

    def test_execute_limit_order_no_match(self):
        limit_order = Order(1, 2, 1234567890, 'buy', 'limit', 10, price=100.5)
        self.matching_engine.execute_order(limit_order, self.order_book, timestamp=1234567890)

        self.assertEqual(limit_order.quantity, 10)
        calls = self.event_bus.publish.call_args_list
        self.assertEqual(len(calls), 1)
        self.assertIsInstance(calls[0][0][0], LimitOrderStoredEvent)
        event = calls[0][0][0]
        self.assertEqual(event.timestamp, 1234567890)
        self.assertEqual(event.order, limit_order)

    def test_execute_market_order_with_match(self):
        sell_order = Order(2, 3, 1234567889, 'sell', 'limit', 10, price=100.5)
        self.order_book.add_order(sell_order)

        buy_order = Order(1, 4, 1234567890, 'buy', 'market', 5)
        self.matching_engine.execute_order(buy_order, self.order_book, timestamp=1234567890)

        self.assertEqual(buy_order.quantity, 0)
        self.assertEqual(sell_order.quantity, 5)

        calls = self.event_bus.publish.call_args_list
        self.assertEqual(len(calls), 3)
        even1 = calls[0][0][0]
        self.assertIsInstance(even1, TransactionEvent)
        self.assertEqual(even1.timestamp, 1234567890)
        self.assertEqual(even1.transaction.order_buy_id, 1)
        self.assertEqual(even1.transaction.order_sell_id, 2)
        self.assertEqual(even1.transaction.buyer_id, 4)
        self.assertEqual(even1.transaction.seller_id, 3)
        self.assertEqual(even1.transaction.price, 100.5)
        self.assertEqual(even1.transaction.quantity, 5)
        self.assertEqual(even1.transaction.timestamp, 1234567890)

        even2 = calls[1][0][0]
        self.assertIsInstance(even2, OrderExecutedEvent)
        self.assertEqual(even2.timestamp, 1234567890)
        self.assertEqual(even2.order, sell_order)
        self.assertEqual(even2.executed_quantity, 5)

        even3 = calls[2][0][0]
        self.assertIsInstance(even3, OrderExecutedEvent)
        self.assertEqual(even3.timestamp, 1234567890)
        self.assertEqual(even3.order, buy_order)
        self.assertEqual(even3.executed_quantity, 5)

    def test_execute_limit_order_partial_match(self):
        sell_order = Order(2, 3, 1234567889, 'sell', 'limit', 5, price=100.5)
        self.order_book.add_order(sell_order)

        buy_order = Order(1, 4, 1234567890, 'buy', 'limit', 10, price=100.5)
        self.matching_engine.execute_order(buy_order, self.order_book, timestamp=1234567890)

        self.assertEqual(buy_order.quantity, 5)
        self.assertEqual(sell_order.quantity, 0)

        calls = self.event_bus.publish.call_args_list
        self.assertEqual(len(calls), 4)
        event1 = calls[0][0][0]
        self.assertIsInstance(event1, TransactionEvent)
        self.assertEqual(event1.timestamp, 1234567890)
        self.assertEqual(event1.transaction.order_buy_id, 1)
        self.assertEqual(event1.transaction.order_sell_id, 2)
        self.assertEqual(event1.transaction.buyer_id, 4)
        self.assertEqual(event1.transaction.seller_id, 3)
        self.assertEqual(event1.transaction.price, 100.5)
        self.assertEqual(event1.transaction.quantity, 5)
        self.assertEqual(event1.transaction.timestamp, 1234567890)
        
        event2 = calls[1][0][0]
        self.assertIsInstance(event2, OrderExecutedEvent)
        self.assertEqual(event2.timestamp, 1234567890)
        self.assertEqual(event2.order, sell_order)
        self.assertEqual(event2.executed_quantity, 5)

        event3 = calls[2][0][0]
        self.assertIsInstance(event3, OrderExecutedEvent)
        self.assertEqual(event3.timestamp, 1234567890)
        self.assertEqual(event3.order, buy_order)
        self.assertEqual(event3.executed_quantity, 5)

        event4 = calls[3][0][0]
        self.assertIsInstance(event4, LimitOrderStoredEvent)
        self.assertEqual(event4.timestamp, 1234567890)
        self.assertEqual(event4.order, buy_order)

    def test_cancel_order(self):
        limit_order = Order(1, 2, 1234567890, 'buy', 'limit', 10, price=100.5)
        self.order_book.add_order(limit_order)

        self.matching_engine.cancel_order(limit_order.order_id, self.order_book, timestamp=1234567891)

        calls = self.event_bus.publish.call_args_list
        self.assertEqual(len(calls), 1)
        event = calls[0][0][0]
        self.assertIsInstance(event, OrderCancelledEvent)
        self.assertEqual(event.timestamp, 1234567891)
        self.assertEqual(event.order, limit_order)
        self.assertNotIn(limit_order.order_id, self.order_book.orders_by_id)

    def test_execute_limit_order_exact_match(self):
        sell_order = Order(2, 3, 1234567889, 'sell', 'limit', 10, price=100.5)
        self.order_book.add_order(sell_order)

        buy_order = Order(1, 4, 1234567890, 'buy', 'limit', 10, price=100.5)
        self.matching_engine.execute_order(buy_order, self.order_book, timestamp=1234567890)

        self.assertEqual(buy_order.quantity, 0)
        self.assertEqual(sell_order.quantity, 0)

        calls = self.event_bus.publish.call_args_list
        self.assertEqual(len(calls), 3)
        
        event1 = calls[0][0][0]
        self.assertIsInstance(event1, TransactionEvent)
        self.assertEqual(event1.timestamp, 1234567890)
        self.assertEqual(event1.transaction.order_buy_id, 1)
        self.assertEqual(event1.transaction.order_sell_id, 2)
        self.assertEqual(event1.transaction.buyer_id, 4)
        self.assertEqual(event1.transaction.seller_id, 3)
        self.assertEqual(event1.transaction.price, 100.5)
        self.assertEqual(event1.transaction.quantity, 10)
        self.assertEqual(event1.transaction.timestamp, 1234567890)

        event2 = calls[1][0][0]
        self.assertIsInstance(event2, OrderExecutedEvent)
        self.assertEqual(event2.timestamp, 1234567890)
        self.assertEqual(event2.order, sell_order)
        self.assertEqual(event2.executed_quantity, 10)

        event3 = calls[2][0][0]
        self.assertIsInstance(event3, OrderExecutedEvent)
        self.assertEqual(event3.timestamp, 1234567890)
        self.assertEqual(event3.order, buy_order)
        self.assertEqual(event3.executed_quantity, 10)
