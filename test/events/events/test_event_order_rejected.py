import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_order_rejected import EventOrderRejected

class TestOrderRejectedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.order_id = 101
        self.agent_id = 1
        self.event_id = 999

        self.order_rejected = EventOrderRejected(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.order_rejected.timestamp, self.timestamp)
        self.assertEqual(self.order_rejected.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.order_rejected.ticker, self.ticker)
        self.assertEqual(self.order_rejected.order_id, self.order_id)
        self.assertEqual(self.order_rejected.agent_id, self.agent_id)
        self.assertEqual(self.order_rejected.id, self.event_id)
        self.assertEqual(self.order_rejected.type, EventType.ORDER_REJECTED)
        self.assertFalse(self.order_rejected.executable)

    def test_create_message(self):
        expected_message = (
            f"Order {self.order_id} {self.ticker} (issuer: {self.agent_id} ) rejected."
        )
        self.assertEqual(self.order_rejected.create_message(), expected_message)
        self.assertEqual(self.order_rejected.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker",
            "order_id", "agent_id"
        ]
        self.assertEqual(self.order_rejected.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.order_rejected)
        decoded_order_rejected = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_order_rejected.timestamp, self.timestamp)
        self.assertEqual(decoded_order_rejected.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_order_rejected.ticker, self.ticker)
        self.assertEqual(decoded_order_rejected.order_id, self.order_id)
        self.assertEqual(decoded_order_rejected.agent_id, self.agent_id)
        self.assertEqual(decoded_order_rejected.id, self.event_id)
        self.assertEqual(decoded_order_rejected.type, EventType.ORDER_REJECTED)

    def test_ordering(self):
        earlier_order_rejected = EventOrderRejected(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_order_rejected < self.order_rejected)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.order_rejected.type.name}, ID: {self.order_rejected.id}, "
            f"Time: {self.order_rejected.timestamp}, Trigger ID: {self.order_rejected.trigger_event_id}, "
            f"Message: {self.order_rejected.message}"
        )
        self.assertEqual(str(self.order_rejected), expected_str)
