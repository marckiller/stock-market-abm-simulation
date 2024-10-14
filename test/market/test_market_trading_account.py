import unittest
from src.market.market_trading_account import TradingAccount

class TestTradingAccount(unittest.TestCase):
    
    def setUp(self):
        self.account = TradingAccount(1)
    
    def test_add_funds(self):
        self.account.add_funds(5000.0)
        self.assertEqual(self.account.balance, 5000.0)
        
        self.account.add_funds(2500.0)
        self.assertEqual(self.account.balance, 7500.0)
    
    def test_remove_funds(self):
        self.account.add_funds(8000.0)
        self.account.remove_funds(3000.0)
        self.assertEqual(self.account.balance, 5000.0)
        
        with self.assertRaises(ValueError):
            self.account.remove_funds(6000.0)
        
        with self.assertRaises(ValueError):
            self.account.remove_funds(-100.0)
    
    def test_add_pending_limit_order(self):
        self.account.add_pending_limit_order(id=1, ticker='TSLA', side='BUY', price=700.0, expiration_time=3600)
        self.assertIn(1, self.account.pending_orders)
        self.assertEqual(self.account.pending_orders[1]['ticker'], 'TSLA')
        self.assertEqual(self.account.pending_orders[1]['side'], 'BUY')
        self.assertEqual(self.account.pending_orders[1]['price'], 700.0)
        self.assertEqual(self.account.pending_orders[1]['expiration_time'], 3600)
        
        with self.assertRaises(ValueError):
            self.account.add_pending_limit_order(id=1, ticker='AAPL', side='SELL', price=150.0)
    
        with self.assertRaises(ValueError):
            self.account.add_pending_limit_order(id=2, ticker='AAPL', side='HOLD', price=150.0)
    
    def test_remove_pending_order(self):
        self.account.add_pending_limit_order(id=1, ticker='AMZN', side='SELL', price=3300.0)
        self.assertIn(1, self.account.pending_orders)
        
        self.account.remove_pending_order(id=1)
        self.assertNotIn(1, self.account.pending_orders)
    
        with self.assertRaises(KeyError):
            self.account.remove_pending_order(id=2)
    
    def test_str_representation(self):
        self.account.add_funds(10000.0)
        self.account.add_pending_limit_order(id=1, ticker='NFLX', side='BUY', price=500.0)
        expected_output = (
            "TradingAccount:\n"
            "Balance: 10000.0\n"
            "Pending Orders:\n"
            "ID: 1, Ticker: NFLX, Side: BUY, Price: 500.0, Expiration: None"
        )
        self.assertEqual(str(self.account), expected_output)
        
        self.account.remove_pending_order(id=1)
        expected_output_no_orders = (
            "TradingAccount:\n"
            "Balance: 10000.0\n"
            "Pending Orders:\nNone"
        )
        self.assertEqual(str(self.account), expected_output_no_orders)