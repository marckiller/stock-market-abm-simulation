import unittest
import os
import numpy as np
import pandas as pd
import h5py
from typing import Optional
from src.market.market_data import MarketData

class TestMarketData(unittest.TestCase):

    def setUp(self):
        self.tickers = ['AAPL', 'GOOG']
        self.ohlcv_periods = [60, 300]  # 1 minute and 5 minutes
        self.market_data = MarketData(tickers=self.tickers, ohlcv_periods=self.ohlcv_periods)

    def test_initialization(self):
        """Test that the MarketData class initializes correctly."""
        self.assertEqual(set(self.market_data.tickers), set(self.tickers))
        self.assertEqual(self.market_data.ohlcv_periods, self.ohlcv_periods)
        self.assertFalse(self.market_data.use_hdf5)
        self.assertTrue(all(ticker in self.market_data.mid_price for ticker in self.tickers))
        self.assertTrue(all(ticker in self.market_data.best_bid for ticker in self.tickers))
        self.assertTrue(all(ticker in self.market_data.best_ask for ticker in self.tickers))

    def test_add_new_ticker(self):
        """Test adding a new ticker to the MarketData."""
        new_ticker = 'MSFT'
        self.market_data.add_new_ticker(new_ticker)
        self.assertIn(new_ticker, self.market_data.tickers)
        self.assertIn(new_ticker, self.market_data.mid_price)
        self.assertIn(new_ticker, self.market_data.best_bid)
        self.assertIn(new_ticker, self.market_data.best_ask)
        self.assertIn(new_ticker, self.market_data.ohlcv_data)

    def test_add_tick_with_existing_ticker(self):
        """Test adding a tick for an existing ticker."""
        ticker = 'AAPL'
        time = 1609459200  # Jan 1, 2021 00:00:00 GMT
        transaction_price = 130.0
        mid_price = 130.0
        best_bid = 129.5
        best_ask = 130.5
        transaction_volume = 100
        ask_volume = 200
        bid_volume = 150

        self.market_data.add_tick(
            ticker, time, transaction_price, mid_price, best_bid, best_ask,
            transaction_volume, ask_volume, bid_volume
        )

        # Check if the tick data has been updated
        self.assertEqual(self.market_data.tick_data['ticker'][-1], ticker)
        self.assertEqual(self.market_data.tick_data['time'][-1], time)
        self.assertEqual(self.market_data.tick_data['transaction_price'][-1], transaction_price)
        self.assertEqual(self.market_data.tick_data['mid_price'][-1], mid_price)
        self.assertEqual(self.market_data.tick_data['best_bid'][-1], best_bid)
        self.assertEqual(self.market_data.tick_data['best_ask'][-1], best_ask)
        self.assertEqual(self.market_data.tick_data['transaction_volume'][-1], transaction_volume)
        self.assertEqual(self.market_data.tick_data['ask_volume'][-1], ask_volume)
        self.assertEqual(self.market_data.tick_data['bid_volume'][-1], bid_volume)

    def test_add_tick_with_new_ticker(self):
        """Test adding a tick for a new ticker not previously tracked."""
        ticker = 'MSFT'
        time = 1609459200
        transaction_price = 220.0
        mid_price = 220.0
        best_bid = 219.5
        best_ask = 220.5
        transaction_volume = 50
        ask_volume = 80
        bid_volume = 70

        self.market_data.add_tick(
            ticker, time, transaction_price, mid_price, best_bid, best_ask,
            transaction_volume, ask_volume, bid_volume
        )

        self.assertIn(ticker, self.market_data.tickers)
        self.assertEqual(self.market_data.tick_data['ticker'][-1], ticker)
        self.assertEqual(self.market_data.mid_price[ticker], mid_price)
        self.assertEqual(self.market_data.best_bid[ticker], best_bid)
        self.assertEqual(self.market_data.best_ask[ticker], best_ask)

    def test_ohlcv_update(self):
        """Test the OHLCV update mechanism."""
        ticker = 'AAPL'
        period = 60  # 1 minute
        time = 1609459260  # Jan 1, 2021 00:01:00 GMT
        transaction_price = 131.0
        transaction_volume = 200

        # Add first tick
        self.market_data.add_tick(
            ticker, time, transaction_price, None, None, None,
            transaction_volume, 0, 0
        )

        ohlcv_df = self.market_data.ohlcv_data[ticker][period]
        self.assertEqual(len(ohlcv_df), 1)
        self.assertEqual(ohlcv_df.iloc[-1]['open'], transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['high'], transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['low'], transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['close'], transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['volume'], transaction_volume)

        # Add a second tick within the same interval
        new_transaction_price = 132.0
        new_transaction_volume = 150
        self.market_data.add_tick(
            ticker, time + 30, new_transaction_price, None, None, None,
            new_transaction_volume, 0, 0
        )

        ohlcv_df = self.market_data.ohlcv_data[ticker][period]
        self.assertEqual(len(ohlcv_df), 1)
        self.assertEqual(ohlcv_df.iloc[-1]['high'], new_transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['close'], new_transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['volume'], transaction_volume + new_transaction_volume)

        # Add a third tick in a new interval
        next_interval_time = time + period
        next_transaction_price = 133.0
        next_transaction_volume = 100
        self.market_data.add_tick(
            ticker, next_interval_time, next_transaction_price, None, None, None,
            next_transaction_volume, 0, 0
        )

        ohlcv_df = self.market_data.ohlcv_data[ticker][period]
        self.assertEqual(len(ohlcv_df), 2)
        self.assertEqual(ohlcv_df.iloc[-1]['open'], next_transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['high'], next_transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['low'], next_transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['close'], next_transaction_price)
        self.assertEqual(ohlcv_df.iloc[-1]['volume'], next_transaction_volume)

    def test_get_current_values(self):
        """Test retrieval of current market values."""
        ticker = 'AAPL'
        transaction_price = 130.5
        mid_price = 130.5
        best_bid = 130.0
        best_ask = 131.0
        transaction_volume = 100
        ask_volume = 200
        bid_volume = 150

        # Add tick to update current values
        self.market_data.add_tick(
            ticker, 1609459200, transaction_price, mid_price, best_bid, best_ask,
            transaction_volume, ask_volume, bid_volume
        )

        self.assertEqual(self.market_data.get_current_mid_price(ticker), mid_price)
        self.assertEqual(self.market_data.get_current_best_bid(ticker), best_bid)
        self.assertEqual(self.market_data.get_current_best_ask(ticker), best_ask)
        self.assertEqual(self.market_data.get_current_transaction_volume(ticker), transaction_volume)
        self.assertEqual(self.market_data.get_current_ask_volume(ticker), ask_volume)
        self.assertEqual(self.market_data.get_current_bid_volume(ticker), bid_volume)


    def test_save_to_hdf5(self):
        """Test saving tick data to HDF5."""
        # Initialize MarketData with HDF5 enabled
        market_data_hdf5 = MarketData(
            tickers=self.tickers, ohlcv_periods=self.ohlcv_periods, use_hdf5=True
        )

        ticker = 'AAPL'
        time = 1609459200
        transaction_price = 130.0
        mid_price = 130.0
        best_bid = 129.5
        best_ask = 130.5
        transaction_volume = 100
        ask_volume = 200
        bid_volume = 150

        market_data_hdf5.add_tick(
            ticker, time, transaction_price, mid_price, best_bid, best_ask,
            transaction_volume, ask_volume, bid_volume
        )

        # Ensure the HDF5 file has been updated
        with h5py.File("market_data.h5", "r") as hdf5_file:
            self.assertIn('tick_data', hdf5_file)
            ticker_data = hdf5_file['tick_data']['ticker'][:]
            self.assertEqual(ticker_data[-1].decode('utf-8'), ticker)

        # Clean up the HDF5 file
        market_data_hdf5.close()
        os.remove("market_data.h5")

    def test_close(self):
        """Test closing the HDF5 file."""
        market_data_hdf5 = MarketData(
            tickers=self.tickers, ohlcv_periods=self.ohlcv_periods, use_hdf5=True
        )
        market_data_hdf5.close()
        self.assertFalse(market_data_hdf5.hdf5_file.id.valid)

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists("market_data.h5"):
            os.remove("market_data.h5")
