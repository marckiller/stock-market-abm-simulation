import unittest
from src.lob.lob_limit_order_book import LimitOrderBook
from src.order.order_limit import OrderLimit
from src.order.order_market import OrderMarket
from src.order.order import OrderSide
from src.lob.lob_matching_engine import MatchingEngine
from src.event.events.event_order_added import EventOrderAdded
from src.event.events.event_order_removed import EventOrderRemoved
from src.event.events.event_transaction import EventTransaction
from src.event.events.event_order_executed import EventOrderExecuted
from src.event.events.event_order_modified import EventOrderModified

class TestMatchingEngine(unittest.TestCase):

    def setUp(self):
        self.lob = LimitOrderBook()
        self.matching_engine = MatchingEngine()
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"

    def test_process_market_buy_order_full_match(self):
        sell_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=50, side=OrderSide.SELL, time=self.timestamp, order_id=1)
        self.lob.add_ask(sell_order, self.timestamp, self.trigger_event_id)
        market_buy_order = OrderMarket(agent_id = 0, ticker=self.ticker, quantity=50, side=OrderSide.BUY, time=self.timestamp, order_id=2)
        events = self.matching_engine.process_market_buy_order(market_buy_order, self.lob, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 4)
        self.assertIsInstance(events[0], EventOrderRemoved)
        self.assertIsInstance(events[1], EventTransaction)
        self.assertIsInstance(events[2], EventOrderExecuted)
        self.assertIsInstance(events[3], EventOrderExecuted)
        self.assertIsNone(self.lob.best_ask())

    def test_process_market_buy_order_partial_match(self):
        sell_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=30, side=OrderSide.SELL, time=self.timestamp, order_id=1)
        self.lob.add_ask(sell_order, self.timestamp, self.trigger_event_id)
        market_buy_order = OrderMarket(agent_id = 0, ticker=self.ticker, quantity=50, side=OrderSide.BUY, time=self.timestamp, order_id=2)
        events = self.matching_engine.process_market_buy_order(market_buy_order, self.lob, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 4)
        self.assertIsInstance(events[0], EventOrderRemoved)
        self.assertIsInstance(events[1], EventTransaction)
        self.assertIsInstance(events[2], EventOrderExecuted)
        self.assertIsInstance(events[3], EventOrderModified)
        self.assertEqual(market_buy_order.quantity, 20)
        self.assertIsNone(self.lob.best_ask())

    def test_process_market_sell_order_full_match(self):
        buy_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=50, side=OrderSide.BUY, time=self.timestamp, order_id=1)
        self.lob.add_bid(buy_order, self.timestamp, self.trigger_event_id)
        market_sell_order = OrderMarket(agent_id = 0, ticker=self.ticker, quantity=50, side=OrderSide.SELL, time=self.timestamp, order_id=2)
        events = self.matching_engine.process_market_sell_order(market_sell_order, self.lob, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 4)
        self.assertIsInstance(events[0], EventOrderRemoved)
        self.assertIsInstance(events[1], EventTransaction)
        self.assertIsInstance(events[2], EventOrderExecuted)
        self.assertIsInstance(events[3], EventOrderExecuted)
        self.assertIsNone(self.lob.best_bid())

    def test_process_limit_buy_order_no_match(self):
        limit_buy_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=95.0, quantity=50, side=OrderSide.BUY, time=self.timestamp, order_id=1)
        events = self.matching_engine.process_limit_buy_order(limit_buy_order, self.lob, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], EventOrderAdded)
        self.assertEqual(self.lob.best_bid(), 95.0)

    def test_process_limit_sell_order_no_match(self):
        limit_sell_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=105.0, quantity=50, side=OrderSide.SELL, time=self.timestamp, order_id=1)
        events = self.matching_engine.process_limit_sell_order(limit_sell_order, self.lob, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], EventOrderAdded)
        self.assertEqual(self.lob.best_ask(), 105.0)

    def test_process_limit_buy_order_full_match(self):
        sell_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=50, side=OrderSide.SELL, time=self.timestamp, order_id=1)
        self.lob.add_ask(sell_order, self.timestamp, self.trigger_event_id)
        limit_buy_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=50, side=OrderSide.BUY, time=self.timestamp, order_id=2)
        events = self.matching_engine.process_limit_buy_order(limit_buy_order, self.lob, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 4)
        self.assertIsInstance(events[0], EventOrderRemoved)
        self.assertIsInstance(events[1], EventTransaction)
        self.assertIsInstance(events[2], EventOrderExecuted)
        self.assertIsInstance(events[3], EventOrderExecuted)
        self.assertIsNone(self.lob.best_ask())
        self.assertIsNone(self.lob.best_bid())

    def test_process_limit_sell_order_partial_match(self):
        buy_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=30, side=OrderSide.BUY, time=self.timestamp, order_id=1)
        self.lob.add_bid(buy_order, self.timestamp, self.trigger_event_id)
        limit_sell_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=99.0, quantity=50, side=OrderSide.SELL, time=self.timestamp, order_id=2)
        events = self.matching_engine.process_limit_sell_order(limit_sell_order, self.lob, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 5)
        self.assertIsInstance(events[0], EventOrderRemoved)
        self.assertIsInstance(events[1], EventTransaction)
        self.assertIsInstance(events[2], EventOrderExecuted)
        self.assertIsInstance(events[3], EventOrderModified)
        self.assertIsInstance(events[4], EventOrderAdded)
        self.assertEqual(limit_sell_order.quantity, 20)
        self.assertEqual(self.lob.best_ask(), 99.0)

    def test_process_limit_buy_order_with_multiple_asks(self):
        sell_order1 = OrderLimit(agent_id = 0, ticker=self.ticker, price=100.0, quantity=20, side=OrderSide.SELL, time=self.timestamp, order_id=1)
        sell_order2 = OrderLimit(agent_id = 0, ticker=self.ticker, price=101.0, quantity=30, side=OrderSide.SELL, time=self.timestamp, order_id=2)
        self.lob.add_ask(sell_order1, self.timestamp, self.trigger_event_id)
        self.lob.add_ask(sell_order2, self.timestamp, self.trigger_event_id)
        limit_buy_order = OrderLimit(agent_id = 0, ticker=self.ticker, price=101.0, quantity=60, side=OrderSide.BUY, time=self.timestamp, order_id=3)
        events = self.matching_engine.process_limit_buy_order(limit_buy_order, self.lob, self.timestamp, self.trigger_event_id)
        self.assertEqual(len(events), 9)

        #TODO: Add correct event assertions

        #self.assertIsInstance(events[0], EventOrderRemoved)
        #self.assertIsInstance(events[1], EventTransaction)
        #self.assertIsInstance(events[2], EventOrderExecuted)
        #self.assertIsInstance(events[3], EventOrderModified)
        #self.assertIsInstance(events[4], EventOrderRemoved)
        #self.assertIsInstance(events[5], EventTransaction)
        #self.assertIsInstance(events[6], EventOrderExecuted)
        #self.assertIsInstance(events[7], EventOrderModified)
        #self.assertIsInstance(events[8], EventOrderExecuted)
        #self.assertEqual(limit_buy_order.quantity, 10)
        self.assertIsNone(self.lob.best_ask())