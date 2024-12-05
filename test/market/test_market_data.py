import unittest
from src.managers.market_data_manager import MarketDataManager

class TestMarketData(unittest.TestCase):

    def setUp(self):
        self.ohlcv_periods = [10, 60]
        self.market_data = MarketDataManager(ohlcv_periods=self.ohlcv_periods, store_tick_data=True, max_ticks=100)

    def test_initialization(self):
        self.assertEqual(len(self.market_data.ohlcv_periods), 2)
        self.assertTrue(10 in self.market_data.ohlcv_periods)
        self.assertTrue(60 in self.market_data.ohlcv_periods)
        self.assertEqual(len(self.market_data.ohlcv_data[10]), 0)
        self.assertEqual(len(self.market_data.ohlcv_data[60]), 0)
        self.assertEqual(self.market_data.tick_count, 0)

    def test_add_tick_updates_live_parameters(self):
        self.market_data.add_tick(
            time=1, transaction_price=100.5, best_bid=100.0, best_ask=101.0,
            transaction_volume=10, bid_volume=20, ask_volume=15
        )
        self.assertEqual(self.market_data.last_transaction_price, 100.5)
        self.assertEqual(self.market_data.best_bid, 100.0)
        self.assertEqual(self.market_data.best_ask, 101.0)
        self.assertEqual(self.market_data.bid_volume, 20)
        self.assertEqual(self.market_data.ask_volume, 15)
        self.assertAlmostEqual(self.market_data.mid_price, 100.5)

    def test_add_tick_stores_tick_data(self):
        self.market_data.add_tick(
            time=1, transaction_price=100.5, best_bid=100.0, best_ask=101.0,
            transaction_volume=10, bid_volume=20, ask_volume=15
        )
        self.assertEqual(self.market_data.tick_count, 1)
        tick = self.market_data.tick_data[0]
        self.assertEqual(tick['time'], 1)
        self.assertEqual(tick['transaction_price'], 100.5)
        self.assertEqual(tick['best_bid'], 100.0)
        self.assertEqual(tick['best_ask'], 101.0)

    def test_tick_data_overflow(self):
        for i in range(105):
            self.market_data.add_tick(
                time=i, transaction_price=100.0 + i, best_bid=99.0 + i, best_ask=101.0 + i,
                transaction_volume=10, bid_volume=20, ask_volume=15
            )
        self.assertEqual(self.market_data.tick_count, 100)
        tick = self.market_data.tick_data[0]
        self.assertEqual(tick['time'], 5)

    def test_update_ohlcv(self):
        self.market_data.add_tick(
            time=1, transaction_price=100.5, best_bid=100.0, best_ask=101.0,
            transaction_volume=10, bid_volume=20, ask_volume=15
        )
        self.market_data.add_tick(
            time=12, transaction_price=101.0, best_bid=100.8, best_ask=101.5,
            transaction_volume=5, bid_volume=18, ask_volume=12
        )
        ohlcv = self.market_data.get_ohlcv(10)
        self.assertEqual(len(ohlcv), 2)
        self.assertEqual(ohlcv.iloc[0]['open'], 100.5)
        self.assertEqual(ohlcv.iloc[0]['high'], 100.5)
        self.assertEqual(ohlcv.iloc[0]['low'], 100.5)
        self.assertEqual(ohlcv.iloc[0]['close'], 100.5)
        self.assertEqual(ohlcv.iloc[0]['volume'], 10)
        self.assertEqual(ohlcv.iloc[0]['time'], 0)

        self.assertEqual(ohlcv.iloc[1]['open'], 101.0)
        self.assertEqual(ohlcv.iloc[1]['high'], 101.0)
        self.assertEqual(ohlcv.iloc[1]['low'], 101.0)
        self.assertEqual(ohlcv.iloc[1]['close'], 101.0)
        self.assertEqual(ohlcv.iloc[1]['volume'], 5)
        self.assertEqual(ohlcv.iloc[1]['time'], 10)


    def test_get_recent_ticks(self):
        for i in range(5):
            self.market_data.add_tick(
                time=i, transaction_price=100.0 + i, best_bid=99.0 + i, best_ask=101.0 + i,
                transaction_volume=10, bid_volume=20, ask_volume=15
            )
        recent_ticks = self.market_data.get_recent_ticks(3)
        self.assertEqual(len(recent_ticks), 3)
        self.assertEqual(recent_ticks[0]['time'], 2)
        self.assertEqual(recent_ticks[1]['time'], 3)
        self.assertEqual(recent_ticks[2]['time'], 4)

    def test_no_tick_storage(self):
        market_data_no_ticks = MarketDataManager(ohlcv_periods=self.ohlcv_periods, store_tick_data=False)
        market_data_no_ticks.add_tick(
            time=1, transaction_price=100.5, best_bid=100.0, best_ask=101.0,
            transaction_volume=10, bid_volume=20, ask_volume=15
        )
        with self.assertRaises(ValueError):
            market_data_no_ticks.get_recent_ticks(1)
