import pandas as pd

def calculate_ema(series, window):
    return series.ewm(span=window, adjust=False).mean()