from src.market.market_market import Market

class MarketData:

    def __init__(self):

        self.tickers = []
        self.best_bids = {}
        self.best_asks = {}
        self.mid_prices = {}

    def add_ticker(self, ticker: str) -> None:
        if ticker in self.tickers:
            raise ValueError(f"Ticker {ticker} already exists.")
        
        self.tickers.append(ticker)
        self.best_bids[ticker] = None
        self.best_asks[ticker] = None
        self.mid_prices[ticker] = None
    
    def update_market_data(self, market: Market) -> None:
        for ticker, lob in market.limit_order_books.items():

            self.best_bids[ticker] = lob.best_bid()
            self.best_asks[ticker] = lob.best_ask()

            if self.best_bids[ticker] is None or self.best_asks[ticker] is None:
                self.mid_prices[ticker] = None

            else:
                self.mid_prices[ticker] = (self.best_bids[ticker] + self.best_asks[ticker]) / 2

    def best_bid(self, ticker: str) -> float:
        if ticker not in self.best_bids:
            raise ValueError(f"Ticker {ticker} does not exist.")
        
        return self.best_bids[ticker]
    
    def best_ask(self, ticker: str) -> float:
        if ticker not in self.best_asks:
            raise ValueError(f"Ticker {ticker} does not exist.")
        
        return self.best_asks[ticker]
    
    def mid_price(self, ticker: str) -> float:
        if ticker not in self.mid_prices:
            raise ValueError(f"Ticker {ticker} does not exist.")
        
        return self.mid_prices[ticker]
    
    def tickers(self) -> list[str]:
        return self.tickers
        