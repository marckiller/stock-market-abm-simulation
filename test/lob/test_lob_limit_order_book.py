import unittest
from src.order.order import OrderSide
from src.order.order_limit import OrderLimit
from src.lob.lob_limit_order_book import LimitOrderBook
from src.event.events.event_order_added import EventOrderAdded
from src.event.events.event_order_removed import EventOrderRemoved
from src.event.events.event_order_canceled import EventOrderCanceled

class TestLimitOrderBook(unittest.TestCase):

    def setUp(self):
        self.lob = LimitOrderBook()
        OrderLimit.next_id = 0
        EventOrderAdded.next_id = 0
        EventOrderRemoved.next_id = 0
        self.ticker = 'AAPL'
        self.time = 1
        self.timestamp = 100
        self.trigger_event_id = 1

    def test_add_bid(self):
        order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.BUY, time=self.time, order_id=1)
        events = self.lob.add_bid(order, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], EventOrderAdded)
        self.assertEqual(self.lob.best_bid(), 100.0)
        self.assertEqual(self.lob.get_price_level_volume(100.0, OrderSide.BUY), 10)

    def test_add_ask(self):
        order = OrderLimit(agent_id = 0, ticker=self.ticker, price=101.0, quantity=5, side=OrderSide.SELL, time=self.time, order_id=2)
        events = self.lob.add_ask(order, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], EventOrderAdded)
        self.assertEqual(self.lob.best_ask(), 101.0)
        self.assertEqual(self.lob.get_price_level_volume(101.0, OrderSide.SELL), 5)

    def test_best_bid_and_ask(self):
        self.assertIsNone(self.lob.best_bid())
        self.assertIsNone(self.lob.best_ask())

        bid_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.BUY, time=self.time, order_id=1)
        ask_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=101.0, quantity=5, side=OrderSide.SELL, time=self.time, order_id=2)
        self.lob.add_bid(bid_order, self.timestamp, self.trigger_event_id)
        self.lob.add_ask(ask_order, self.timestamp, self.trigger_event_id)

        self.assertEqual(self.lob.best_bid(), 100.0)
        self.assertEqual(self.lob.best_ask(), 101.0)

    def test_pop_top_ask_at_price(self):
        ask_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=101.0, quantity=5, side=OrderSide.SELL, time=self.time, order_id=2)
        self.lob.add_ask(ask_order, self.timestamp, self.trigger_event_id)
        order, events = self.lob.pop_top_ask_at_price(101.0, self.timestamp, self.trigger_event_id)
        self.assertEqual(order.order_id, 2)
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], EventOrderRemoved)
        self.assertIsNone(self.lob.best_ask())

    def test_cancel_order_by_id(self):
        bid_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.BUY, time=self.time, order_id=1)
        self.lob.add_bid(bid_order, self.timestamp, self.trigger_event_id)
        events = self.lob.cancel_order_by_id(1, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 2)
        self.assertIsInstance(events[0], EventOrderCanceled)
        self.assertIsInstance(events[1], EventOrderRemoved)
        self.assertIsNone(self.lob.best_bid())

    def test_get_price_level_volume(self):
        bid_order1 = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.BUY, time=self.time, order_id=1)
        bid_order2 = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=5, side=OrderSide.BUY, time=self.time, order_id=2)
        self.lob.add_bid(bid_order1, self.timestamp, self.trigger_event_id)
        self.lob.add_bid(bid_order2, self.timestamp, self.trigger_event_id)
        volume = self.lob.get_price_level_volume(100.0, OrderSide.BUY)
        self.assertEqual(volume, 15)

    def test_best_bid_updates_after_cancel(self):
        bid_order1 = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.BUY, time=self.time, order_id=1)
        bid_order2 = OrderLimit(agent_id = 0, ticker=self.ticker, price=99.0, quantity=5, side=OrderSide.BUY, time=self.time, order_id=2)
        self.lob.add_bid(bid_order1, self.timestamp, self.trigger_event_id)
        self.lob.add_bid(bid_order2, self.timestamp, self.trigger_event_id)
        self.assertEqual(self.lob.best_bid(), 100.0)
        self.lob.cancel_order_by_id(1, self.timestamp, self.trigger_event_id)
        self.assertEqual(self.lob.best_bid(), 99.0)

    def test_add_bid_with_existing_price_level(self):
        bid_order1 = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.BUY, time=self.time, order_id=1)
        bid_order2 = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=15, side=OrderSide.BUY, time=self.time, order_id=2)
        self.lob.add_bid(bid_order1, self.timestamp, self.trigger_event_id)
        self.lob.add_bid(bid_order2, self.timestamp, self.trigger_event_id)
        self.assertEqual(self.lob.get_price_level_volume(100.0, OrderSide.BUY), 25)

    def test_add_ask_with_existing_price_level(self):
        ask_order1 = OrderLimit(agent_id = 0, ticker=self.ticker, price=101.0, quantity=10, side=OrderSide.SELL, time=self.time, order_id=1)
        ask_order2 = OrderLimit(agent_id = 0, ticker=self.ticker, price=101.0, quantity=15, side=OrderSide.SELL, time=self.time, order_id=2)
        self.lob.add_ask(ask_order1, self.timestamp, self.trigger_event_id)
        self.lob.add_ask(ask_order2, self.timestamp, self.trigger_event_id)
        self.assertEqual(self.lob.get_price_level_volume(101.0, OrderSide.SELL), 25)

    def test_order_map_updates_on_add_and_cancel(self):
        bid_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.BUY, time=self.time, order_id=1)
        self.lob.add_bid(bid_order, self.timestamp, self.trigger_event_id)
        self.assertIn(1, self.lob.order_map)
        self.lob.cancel_order_by_id(1, self.timestamp, self.trigger_event_id)
        self.assertNotIn(1, self.lob.order_map)

    def test_exception_on_invalid_order_side(self):
        bid_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.SELL, time=self.time, order_id=1)
        with self.assertRaises(ValueError):
            self.lob.add_bid(bid_order, self.timestamp, self.trigger_event_id)
        ask_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=101.0, quantity=5, side=OrderSide.BUY, time=self.time, order_id=2)
        with self.assertRaises(ValueError):
            self.lob.add_ask(ask_order, self.timestamp, self.trigger_event_id)

    def test_exception_on_canceling_nonexistent_order(self):
        with self.assertRaises(ValueError):
            self.lob.cancel_order_by_id(999, self.timestamp, self.trigger_event_id)

    def test_last_popped_order_id_reset(self):
        bid_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=10, side=OrderSide.BUY, time=self.time, order_id=1)
        self.lob.last_popped_order_id = 1
        self.lob.add_bid(bid_order, self.timestamp, self.trigger_event_id)
        self.assertIsNone(self.lob.last_popped_order_id)
