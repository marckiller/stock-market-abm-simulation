import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_order_canceled import EventOrderCanceled

class TestOrderCanceledEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.order_id = 101
        self.agent_id = 1
        self.event_id = 999

        self.order_canceled = EventOrderCanceled(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.order_canceled.timestamp, self.timestamp)
        self.assertEqual(self.order_canceled.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.order_canceled.ticker, self.ticker)
        self.assertEqual(self.order_canceled.order_id, self.order_id)
        self.assertEqual(self.order_canceled.agent_id, self.agent_id)
        self.assertEqual(self.order_canceled.id, self.event_id)
        self.assertEqual(self.order_canceled.type, EventType.ORDER_CANCELED)
        self.assertFalse(self.order_canceled.executable)

    def test_create_message(self):
        expected_message = (
            f"Order {self.order_id} {self.ticker} canceled for agent {self.agent_id}."
        )
        self.assertEqual(self.order_canceled.create_message(), expected_message)
        self.assertEqual(self.order_canceled.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker",
            "order_id", "agent_id"
        ]
        self.assertEqual(self.order_canceled.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.order_canceled)
        decoded_order_canceled = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_order_canceled.timestamp, self.timestamp)
        self.assertEqual(decoded_order_canceled.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_order_canceled.ticker, self.ticker)
        self.assertEqual(decoded_order_canceled.order_id, self.order_id)
        self.assertEqual(decoded_order_canceled.agent_id, self.agent_id)
        self.assertEqual(decoded_order_canceled.id, self.event_id)
        self.assertEqual(decoded_order_canceled.type, EventType.ORDER_CANCELED)

    def test_ordering(self):
        earlier_order_canceled = EventOrderCanceled(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_order_canceled < self.order_canceled)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.order_canceled.type.name}, ID: {self.order_canceled.id}, "
            f"Time: {self.order_canceled.timestamp}, Trigger ID: {self.order_canceled.trigger_event_id}, "
            f"Message: {self.order_canceled.message}"
        )
        self.assertEqual(str(self.order_canceled), expected_str)
