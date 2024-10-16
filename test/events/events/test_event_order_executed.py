import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_order_executed import EventOrderExecuted

class TestOrderExecutedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.order_id = 101
        self.agent_id = 1
        self.event_id = 999

        self.order_executed = EventOrderExecuted(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.order_executed.timestamp, self.timestamp)
        self.assertEqual(self.order_executed.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.order_executed.ticker, self.ticker)
        self.assertEqual(self.order_executed.order_id, self.order_id)
        self.assertEqual(self.order_executed.agent_id, self.agent_id)
        self.assertEqual(self.order_executed.id, self.event_id)
        self.assertEqual(self.order_executed.type, EventType.ORDER_EXECUTED)
        self.assertFalse(self.order_executed.executable)

    def test_create_message(self):
        expected_message = (
            f"Order {self.order_id} {self.ticker} (issuer: {self.agent_id} ) executed."
        )
        self.assertEqual(self.order_executed.create_message(), expected_message)
        self.assertEqual(self.order_executed.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker",
            "order_id", "agent_id"
        ]
        self.assertEqual(self.order_executed.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.order_executed)
        decoded_order_executed = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_order_executed.timestamp, self.timestamp)
        self.assertEqual(decoded_order_executed.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_order_executed.ticker, self.ticker)
        self.assertEqual(decoded_order_executed.order_id, self.order_id)
        self.assertEqual(decoded_order_executed.agent_id, self.agent_id)
        self.assertEqual(decoded_order_executed.id, self.event_id)
        self.assertEqual(decoded_order_executed.type, EventType.ORDER_EXECUTED)

    def test_ordering(self):
        earlier_order_executed = EventOrderExecuted(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_order_executed < self.order_executed)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.order_executed.type.name}, ID: {self.order_executed.id}, "
            f"Time: {self.order_executed.timestamp}, Trigger ID: {self.order_executed.trigger_event_id}, "
            f"Message: {self.order_executed.message}"
        )
        self.assertEqual(str(self.order_executed), expected_str)