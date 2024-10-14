from src.lob.lob_limit_order_book import LimitOrderBook
from src.order.order_market import OrderMarket
from src.order.order import OrderSide, Order
from src.lob.lob_matching_engine import MatchingEngine

from src.market.market_trading_account import TradingAccount

class Market:

    def __init__(self):

        self.limit_order_books: dict[str, LimitOrderBook] = {}
        self.trading_accounts: dict[int, TradingAccount] = {}
        self.marching_engine = MatchingEngine()

    def add_limit_order_book(self, ticker: str) -> None:
        if ticker in self.limit_order_books:
            raise ValueError(f"Limit order book for {ticker} already exists.")
        
        self.limit_order_books[ticker] = LimitOrderBook()
        print(f"Added limit order book for {ticker}.")

    def execute_order(self, order: Order, ticker: str) -> None:
        if ticker not in self.limit_order_books:
            raise ValueError(f"Limit order book for {ticker} does not exist.")
    
        self.marching_engine.process_order(order, self.limit_order_books[ticker])
        #TODO: after the order is executed handle output events and save transactions

    def cancel_order(self, order_id: int, ticker: str) -> None:
        if ticker not in self.limit_order_books:
            raise ValueError(f"Limit order book for {ticker} does not exist.")
        
        self.limit_order_books[ticker].remove_order_by_id(order_id)
        #TODO: after the order is cancelled handle output events
        print(f"Cancelled Order {order_id} from {ticker}.")

    def register_account(self, agent_id: int) -> None:
        if agent_id in self.trading_accounts:
            raise ValueError(f"Trading account for agent {agent_id} already exists.")
        
        self.trading_accounts[agent_id] = TradingAccount(agent_id)
        print(f"Registered trading account for agent {agent_id}.")

    #account operations

    def add_funds(self, agent_id: int, amount: float) -> None:
        if agent_id not in self.trading_accounts:
            raise ValueError(f"Trading account for agent {agent_id} does not exist.")
        
        self.trading_accounts[agent_id].add_funds(amount)
    
    def remove_funds(self, agent_id: int, amount: float) -> None:
        if agent_id not in self.trading_accounts:
            raise ValueError(f"Trading account for agent {agent_id} does not exist.")
        
        self.trading_accounts[agent_id].remove_funds(amount)

    def add_pending_limit_order(self, agent_id: int, order_id: int, ticker: str, side: str, price: float, expiration_time: int) -> None:
        if agent_id not in self.trading_accounts:
            raise ValueError(f"Trading account for agent {agent_id} does not exist.")
        
        self.trading_accounts[agent_id].add_pending_limit_order(order_id, ticker, side, price, expiration_time)

    def remove_pending_order(self, agent_id: int, order_id: int) -> None:
        if agent_id not in self.trading_accounts:
            raise ValueError(f"Trading account for agent {agent_id} does not exist.")
        
        self.trading_accounts[agent_id].remove_pending_order(order_id)
