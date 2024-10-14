# test/matching/test_matching_engine.py

import unittest
from src.lob.lob_limit_order_book import LimitOrderBook
from src.order.order_limit import OrderLimit
from src.order.order_market import OrderMarket
from src.order.order import OrderSide, Order
from src.lob.lob_matching_engine import MatchingEngine

class TestMatchingEngine(unittest.TestCase):

    def setUp(self):
        self.lob = LimitOrderBook()
        self.engine = MatchingEngine()
        OrderLimit.next_id = 0
        OrderMarket.next_id = 0
        Order.next_id = 0

    def test_process_limit_order_full_fill(self):
        ask_order = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        self.lob.add(ask_order)
        buy_order = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=2)
        self.engine.process_order(buy_order, self.lob)
        self.assertIsNone(self.lob.best_bid())
        self.assertIsNone(self.lob.best_ask())
        self.assertEqual(len(self.engine.transactions), 1)
        self.assertEqual(self.engine.transactions[0]['quantity'], 50)

    def test_process_limit_order_partial_fill(self):
        ask_order = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        self.lob.add(ask_order)
        buy_order = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2)
        self.engine.process_order(buy_order, self.lob)
        remaining_ask = self.lob.get_order(ask_order.order_id)
        self.assertIsNotNone(remaining_ask)
        self.assertEqual(remaining_ask.quantity, 20)
        self.assertIsNone(self.lob.get_order(buy_order.order_id))
        self.assertEqual(len(self.engine.transactions), 1)
        self.assertEqual(self.engine.transactions[0]['quantity'], 30)

    def test_process_market_order_full_fill(self):
        ask_order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        ask_order2 = OrderLimit(price=101.0, quantity=30, side=OrderSide.SELL, time=2)
        self.lob.add(ask_order1)
        self.lob.add(ask_order2)

        market_order = OrderMarket(quantity=80, side=OrderSide.BUY, time=3)
        self.engine.process_order(market_order, self.lob)
        self.assertIsNone(self.lob.best_bid())
        self.assertIsNone(self.lob.best_ask())
        self.assertEqual(len(self.engine.transactions), 2)
        self.assertEqual(self.engine.transactions[0]['quantity'], 50)
        self.assertEqual(self.engine.transactions[1]['quantity'], 30)

    def test_process_market_order_partial_fill(self):
        ask_order1 = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        self.lob.add(ask_order1)
        market_order = OrderMarket(quantity=70, side=OrderSide.BUY, time=2)
        self.engine.process_order(market_order, self.lob)
        self.assertIsNone(self.lob.best_bid())
        self.assertIsNone(self.lob.best_ask())
        self.assertEqual(len(self.engine.transactions), 1)
        self.assertEqual(self.engine.transactions[0]['quantity'], 50)

    def test_process_limit_order_no_fill(self):
        ask_order = OrderLimit(price=101.0, quantity=50, side=OrderSide.SELL, time=1)
        self.lob.add(ask_order)
        buy_order = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2)
        self.engine.process_order(buy_order, self.lob)
        self.assertEqual(self.lob.get_price_level_volume(100.0, OrderSide.BUY), 30)
        self.assertEqual(len(self.engine.transactions), 0)

    def test_process_market_order_no_fill(self):

        market_order = OrderMarket(quantity=40, side=OrderSide.BUY, time=1)
        self.engine.process_order(market_order, self.lob)
        self.assertIsNone(self.lob.best_bid())
        self.assertIsNone(self.lob.best_ask())
        self.assertEqual(len(self.engine.transactions), 0)

    def test_process_limit_order_partial_fill_and_readd(self):
        ask_order = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        self.lob.add(ask_order)
        buy_order = OrderLimit(price=100.0, quantity=30, side=OrderSide.BUY, time=2)
        self.engine.process_order(buy_order, self.lob)

        remaining_ask = self.lob.get_order(ask_order.order_id)
        self.assertIsNotNone(remaining_ask)
        self.assertEqual(remaining_ask.quantity, 20)
        self.assertIsNone(self.lob.get_order(buy_order.order_id))

        remaining_buy_order = OrderLimit(price=100.0, quantity=20, side=OrderSide.BUY, time=3, order_id=buy_order.order_id)
        self.engine.process_order(remaining_buy_order, self.lob)
        self.assertEqual(len(self.lob.sorted_bids), 0)
        self.assertIsNone(self.lob.best_bid())
        self.assertEqual(len(self.engine.transactions), 2)
        self.assertEqual(self.engine.transactions[0]['quantity'], 30)
        self.assertEqual(self.engine.transactions[1]['quantity'], 20)

    def test_transactions_recorded_correctly(self):
        ask_order = OrderLimit(price=100.0, quantity=50, side=OrderSide.SELL, time=1)
        self.lob.add(ask_order)
        buy_order = OrderLimit(price=100.0, quantity=50, side=OrderSide.BUY, time=2)
        self.engine.process_order(buy_order, self.lob)
        self.assertEqual(len(self.engine.transactions), 1)
        transaction = self.engine.transactions[0]
        self.assertEqual(transaction['buy_order_id'], buy_order.order_id)
        self.assertEqual(transaction['sell_order_id'], ask_order.order_id)
        self.assertEqual(transaction['price'], 100.0)
        self.assertEqual(transaction['quantity'], 50)
        self.assertEqual(transaction['time'], buy_order.timestamp)
