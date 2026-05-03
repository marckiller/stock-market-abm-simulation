import unittest

from src.market.event_bus import EventBus
from src.market.event_logger import EventLogger
from src.market.events import LimitOrderStoredEvent, OrderExecutedEvent, TransactionEvent
from src.market.order import Order
from src.market.transaction import Transaction


class TestEventLogger(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.event_logger = EventLogger(self.event_bus)

    def test_logs_limit_order_as_record(self):
        order = Order(1, 2, 10, 'buy', 'limit', 5, price=100.0)

        self.event_bus.publish(LimitOrderStoredEvent(timestamp=10, order=order))

        records = self.event_logger.to_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['sequence'], 0)
        self.assertEqual(records[0]['event_type'], 'limit_order_stored')
        self.assertEqual(records[0]['order_id'], 1)
        self.assertEqual(records[0]['agent_id'], 2)
        self.assertEqual(records[0]['quantity'], 5)
        self.assertEqual(records[0]['price'], 100.0)

    def test_logs_order_execution_snapshot(self):
        order = Order(1, 2, 10, 'sell', 'limit', 0, price=101.0)

        self.event_bus.publish(OrderExecutedEvent(timestamp=12, order=order, executed_quantity=5))
        order.modify_quantity(10)

        records = self.event_logger.to_records()
        self.assertEqual(records[0]['event_type'], 'order_executed')
        self.assertEqual(records[0]['quantity'], 0)
        self.assertEqual(records[0]['executed_quantity'], 5)

    def test_logs_transaction(self):
        transaction = Transaction(
            order_buy_id=1,
            order_sell_id=2,
            buyer_id=10,
            seller_id=20,
            price=99.5,
            quantity=3,
            timestamp=15
        )

        self.event_bus.publish(TransactionEvent(timestamp=15, transaction=transaction))

        records = self.event_logger.to_records()
        self.assertEqual(records[0]['event_type'], 'transaction')
        self.assertEqual(records[0]['buyer_id'], 10)
        self.assertEqual(records[0]['seller_id'], 20)
        self.assertEqual(records[0]['transaction_timestamp'], 15)
        self.assertEqual(records[0]['price'], 99.5)
        self.assertEqual(records[0]['quantity'], 3)


if __name__ == '__main__':
    unittest.main()
