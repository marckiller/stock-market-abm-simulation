import unittest

from src.market.events import Event, LimitOrderStoredEvent, OrderExecutedEvent, TransactionEvent, OrderCancelledEvent

from src.market.order import Order
from src.market.transaction import Transaction

class TestTransaction(unittest.TestCase):
    def test_transaction_initialization(self):
        transaction = Transaction(
            order_buy_id=1,
            order_sell_id=2,
            buyer_id=3,
            seller_id=4,
            price=100.5,
            quantity=10,
            timestamp=1234567890
        )
        self.assertEqual(transaction.order_buy_id, 1)
        self.assertEqual(transaction.order_sell_id, 2)
        self.assertEqual(transaction.buyer_id, 3)
        self.assertEqual(transaction.seller_id, 4)
        self.assertEqual(transaction.price, 100.5)
        self.assertEqual(transaction.quantity, 10)
        self.assertEqual(transaction.timestamp, 1234567890)

    def test_transaction_str(self):
        transaction = Transaction(
            order_buy_id=1,
            order_sell_id=2,
            buyer_id=3,
            seller_id=4,
            price=100.5,
            quantity=10,
            timestamp=1234567890
        )
        expected_str = "Transaction: 10 units at 100.5. Buyer: 3, Seller: 4"
        self.assertEqual(str(transaction), expected_str)

class TestEvents(unittest.TestCase):
    def test_event_initialization(self):
        event = Event(event_type='test_event', timestamp=1234567890)
        self.assertEqual(event.event_type, 'test_event')
        self.assertEqual(event.timestamp, 1234567890)

    def test_limit_order_stored_event(self):
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        event = LimitOrderStoredEvent(timestamp=1234567890, order=order)
        self.assertEqual(event.event_type, 'limit_order_stored')
        self.assertEqual(event.order, order)

    def test_order_executed_event(self):
        order = Order(1, 2, 1234567890, 'buy', 'limit', 10, 100.5)
        event = OrderExecutedEvent(
            timestamp=1234567890,
            order=order,
            executed_quantity=5
        )
        self.assertEqual(event.event_type, 'order_executed')
        self.assertEqual(event.order, order)
        self.assertEqual(event.executed_quantity, 5)

    def test_transaction_event(self):
        transaction = Transaction(1, 2, 3, 4, 100.5, 10, 1234567890)
        event = TransactionEvent(timestamp=1234567890, transaction=transaction)
        self.assertEqual(event.event_type, 'transaction')
        self.assertEqual(event.transaction, transaction)
