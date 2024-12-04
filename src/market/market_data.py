import pandas as pd
import numpy as np
from typing import Optional, List

class MarketData:
    def __init__(self, ohlcv_periods: List[int], store_tick_data: bool = False, max_ticks: int = 10000000):
        """
        Initializes the MarketData object.

        Parameters:
        - ohlcv_periods (List[int]): Periods for OHLCV aggregation in units of dt.
        - store_tick_data (bool): Whether to store tick-by-tick data.
        - max_ticks (int): Maximum number of ticks to store if store_tick_data is True.
        """
        self.ohlcv_periods = set(ohlcv_periods) if ohlcv_periods else set()
        self.ohlcv_data = {
            period: pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
            for period in self.ohlcv_periods
        }
        self.current_bars = {period: None for period in self.ohlcv_periods}

        self.best_bid = None
        self.best_ask = None
        self.mid_price = None
        self.last_transaction_price = None
        self.bid_volume = 0
        self.ask_volume = 0

        #tick-by-tick data
        self.store_tick_data = store_tick_data
        if self.store_tick_data:
            self.max_ticks = max_ticks
            self.tick_dtype = np.dtype([
                ('time', 'int64'),
                ('transaction_price', 'float64'),
                ('best_bid', 'float64'),
                ('best_ask', 'float64'),
                ('transaction_volume', 'int32'),
                ('bid_volume', 'int32'),
                ('ask_volume', 'int32')
            ])
            self.tick_data = np.zeros(self.max_ticks, dtype=self.tick_dtype)
            self.tick_count = 0

    def update_market_parameters(self, best_bid: Optional[float], best_ask: Optional[float],
                                 last_transaction_price: Optional[float], bid_volume: int, ask_volume: int):
        self.best_bid = best_bid
        self.best_ask = best_ask

        if last_transaction_price:
            self.last_transaction_price = last_transaction_price

        self.mid_price = self.calculate_mid_price(best_bid, best_ask)
        self.bid_volume = bid_volume
        self.ask_volume = ask_volume

    def add_tick(self, time: int, transaction_price: Optional[float], best_bid: Optional[float], best_ask: Optional[float],
                 transaction_volume: Optional[int], bid_volume: Optional[int], ask_volume: Optional[int]):
        self.update_market_parameters(best_bid, best_ask, transaction_price, bid_volume, ask_volume)

        if self.store_tick_data:
            if self.tick_count >= self.max_ticks:
                self.tick_data[:-1] = self.tick_data[1:]
                self.tick_count -= 1
            self.tick_data[self.tick_count] = (
                time, transaction_price or 0.0, best_bid or 0.0, best_ask or 0.0,
                transaction_volume or 0, bid_volume or 0, ask_volume or 0
            )
            self.tick_count += 1

        for period in self.ohlcv_periods:
            self.update_ohlcv(time, transaction_price or 0.0, transaction_volume or 0, period)

    def update_ohlcv(self, time: int, transaction_price: float, transaction_volume: int, period: int):
        current_interval = time // period

        current_bar = self.current_bars[period]
        if current_bar is None or current_bar['time'] < current_interval * period:
            if current_bar:
                current_bar_df = pd.DataFrame([current_bar])
                self.ohlcv_data[period] = pd.concat([self.ohlcv_data[period], current_bar_df], ignore_index=True)

            self.current_bars[period] = {
                'time': current_interval * period,
                'open': transaction_price,
                'high': transaction_price,
                'low': transaction_price,
                'close': transaction_price,
                'volume': transaction_volume
            }
        else:
            current_bar['high'] = max(current_bar['high'], transaction_price)
            current_bar['low'] = min(current_bar['low'], transaction_price)
            current_bar['close'] = transaction_price
            current_bar['volume'] += transaction_volume


    def get_ohlcv(self, period: int) -> pd.DataFrame:
        if period not in self.ohlcv_periods:
            raise ValueError(f"Period {period} not found. Please add it during initialization.")

        ohlcv_df = self.ohlcv_data[period].copy()

        current_bar = self.current_bars[period]
        if current_bar:
            current_bar_df = pd.DataFrame([current_bar])
            ohlcv_df = pd.concat([ohlcv_df, current_bar_df], ignore_index=True)

        return ohlcv_df

    def calculate_mid_price(self, best_bid: Optional[float], best_ask: Optional[float]) -> Optional[float]:
        if best_bid is not None and best_ask is not None:
            return (best_bid + best_ask) / 2
        return None

    def get_recent_ticks(self, n: int) -> np.ndarray:

        if not self.store_tick_data:
            raise ValueError("Tick data storage is disabled.")
        return self.tick_data[max(0, self.tick_count - n):self.tick_count]
