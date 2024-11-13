from typing import List, Dict, Optional
import numpy as np
import pandas as pd
import h5py

class MarketData:
    def __init__(self, tickers: List[str], ohlcv_periods: List[int], use_hdf5: bool = False):
        self.tickers = set(tickers)
        self.ohlcv_periods = ohlcv_periods
        self.use_hdf5 = use_hdf5

        # Define the data types for the structured array
        string_dt = h5py.string_dtype(encoding='utf-8')
        tick_dtype = np.dtype([
            ('ticker', string_dt),
            ('time', 'int64'),
            ('transaction_price', 'float64'),
            ('mid_price', 'float64'),
            ('best_bid', 'float64'),
            ('best_ask', 'float64'),
            ('transaction_volume', 'int32'),
            ('ask_volume', 'int32'),
            ('bid_volume', 'int32'),
        ])

        # Initialize tick-by-tick data as a structured NumPy array
        self.tick_data = np.empty(0, dtype=tick_dtype)

        # Initialize OHLCV data
        self.ohlcv_data = {
            ticker: {period: pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume', 'timestamp_interval'])
                     for period in ohlcv_periods}
            for ticker in self.tickers
        }

        # Current market values for each instrument
        self.mid_price: Dict[str, Optional[float]] = {ticker: None for ticker in self.tickers}
        self.best_bid: Dict[str, Optional[float]] = {ticker: None for ticker in self.tickers}
        self.best_ask: Dict[str, Optional[float]] = {ticker: None for ticker in self.tickers}
        self.transaction_volume: Dict[str, int] = {ticker: 0 for ticker in self.tickers}
        self.ask_volume: Dict[str, int] = {ticker: 0 for ticker in self.tickers}
        self.bid_volume: Dict[str, int] = {ticker: 0 for ticker in self.tickers}

        if use_hdf5:
            self.hdf5_file = h5py.File("market_data.h5", "w")


    def add_new_ticker(self, ticker: str):
        """Adds a new ticker to all data structures if it does not already exist."""
        if ticker not in self.tickers:
            self.tickers.add(ticker)
            self.ohlcv_data[ticker] = {period: pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume', 'timestamp_interval'])
                                       for period in self.ohlcv_periods}
            self.mid_price[ticker] = None
            self.best_bid[ticker] = None
            self.best_ask[ticker] = None
            self.transaction_volume[ticker] = 0
            self.ask_volume[ticker] = 0
            self.bid_volume[ticker] = 0

    def add_tick(self, ticker: str, time: int, transaction_price: Optional[float], mid_price: Optional[float],
                 best_bid: Optional[float], best_ask: Optional[float], transaction_volume: int,
                 ask_volume: int, bid_volume: int):
        """Adds a new tick to market data and automatically adds a new ticker if it is not already tracked."""
        if ticker not in self.tickers:
            self.add_new_ticker(ticker)

        # Create a new tick record
        new_tick = np.array([(ticker, time, transaction_price or 0.0,
                              mid_price if mid_price is not None else np.nan,
                              best_bid if best_bid is not None else np.nan,
                              best_ask if best_ask is not None else np.nan,
                              transaction_volume,
                              ask_volume,
                              bid_volume)],
                            dtype=self.tick_data.dtype)
        self.tick_data = np.concatenate((self.tick_data, new_tick))

        # Update current market values
        if mid_price is not None:
            self.mid_price[ticker] = mid_price
        if best_bid is not None:
            self.best_bid[ticker] = best_bid
        if best_ask is not None:
            self.best_ask[ticker] = best_ask
        self.transaction_volume[ticker] = transaction_volume
        self.ask_volume[ticker] = ask_volume
        self.bid_volume[ticker] = bid_volume

        # Update OHLCV for all periods of this instrument
        for period in self.ohlcv_periods:
            self.update_ohlcv(ticker, time, transaction_price, transaction_volume, period)

        if self.use_hdf5:
            self.save_to_hdf5()

    def update_ohlcv(self, ticker: str, time: int, transaction_price: Optional[float], transaction_volume: int, period: int):
        """Updates or creates a new OHLCV candle for the specified instrument and interval."""
        if transaction_price is None:
            return

        ohlcv_df = self.ohlcv_data[ticker][period]
        current_interval = time // period

        if ohlcv_df.empty or (ohlcv_df.iloc[-1]['timestamp_interval'] < current_interval):
            new_ohlcv = {
                'open': transaction_price,
                'high': transaction_price,
                'low': transaction_price,
                'close': transaction_price,
                'volume': transaction_volume,
                'timestamp_interval': current_interval
            }
            self.ohlcv_data[ticker][period] = pd.concat([ohlcv_df, pd.DataFrame([new_ohlcv])], ignore_index=True)
        else:
            last_ohlcv = ohlcv_df.iloc[-1]
            last_ohlcv['high'] = max(last_ohlcv['high'], transaction_price)
            last_ohlcv['low'] = min(last_ohlcv['low'], transaction_price)
            last_ohlcv['close'] = transaction_price
            last_ohlcv['volume'] += transaction_volume
            self.ohlcv_data[ticker][period].iloc[-1] = last_ohlcv

    def save_to_hdf5(self):
        """Saves current tick-by-tick data to HDF5 file."""
        if 'tick_data' in self.hdf5_file:
            del self.hdf5_file['tick_data']
        self.hdf5_file.create_dataset('tick_data', data=self.tick_data)

    def close(self):
        if self.use_hdf5:
            self.hdf5_file.close()

    # Methods to retrieve current values for each instrument
    def get_current_mid_price(self, ticker: str) -> Optional[float]:
        return self.mid_price.get(ticker)

    def get_current_best_bid(self, ticker: str) -> Optional[float]:
        return self.best_bid.get(ticker)

    def get_current_best_ask(self, ticker: str) -> Optional[float]:
        return self.best_ask.get(ticker)

    def get_current_transaction_volume(self, ticker: str) -> int:
        return self.transaction_volume.get(ticker, 0)

    def get_current_ask_volume(self, ticker: str) -> int:
        return self.ask_volume.get(ticker, 0)

    def get_current_bid_volume(self, ticker: str) -> int:
        return self.bid_volume.get(ticker, 0)
