import numpy as np
from typing import Optional

class IndicatorManager:
    
    def __init__(self, market_data_manager: 'MarketDataManager'):
        self.market = market_data_manager
        self.indicators = {}

    def add_indicator(self, name: str, func, window: int, period: int):
        self.indicators[name] = {
            'func': func,
            'window': window,
            'period': period,
            'value': None
        }
        self.calculate_indicator(name)

    def calculate_indicator(self, name: str):
        indicator = self.indicators[name]
        window = indicator['window']
        period = indicator['period']
        series = self.market.get_price_history(period=period, window=window)
        if series.empty or len(series) < window:
            indicator['value'] = None
        else:
            indicator['value'] = indicator['func'](series, window)

    def update_indicators(self):
        for name in self.indicators:
            self.calculate_indicator(name)

    def get_indicator(self, name: str) -> Optional[float]:
        return self.indicators[name]['value']

    def calculate_all_indicators(self):
        for name in self.indicators:
            self.calculate_indicator(name)