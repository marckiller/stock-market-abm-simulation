import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_order_removed import EventOrderRemoved

class TestOrderRemovedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.order_id = 101
        self.agent_id = 1
        self.event_id = 999

        self.order_removed = EventOrderRemoved(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.order_removed.timestamp, self.timestamp)
        self.assertEqual(self.order_removed.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.order_removed.ticker, self.ticker)
        self.assertEqual(self.order_removed.order_id, self.order_id)
        self.assertEqual(self.order_removed.agent_id, self.agent_id)
        self.assertEqual(self.order_removed.id, self.event_id)
        self.assertEqual(self.order_removed.type, EventType.ORDER_REMOVED)
        self.assertFalse(self.order_removed.executable)

    def test_create_message(self):
        expected_message = (
            f"Order {self.order_id} removed for {self.agent_id} from {self.ticker}."
        )
        self.assertEqual(self.order_removed.create_message(), expected_message)
        self.assertEqual(self.order_removed.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker",
            "order_id", "agent_id"
        ]
        self.assertEqual(self.order_removed.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.order_removed)
        decoded_order_removed = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_order_removed.timestamp, self.timestamp)
        self.assertEqual(decoded_order_removed.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_order_removed.ticker, self.ticker)
        self.assertEqual(decoded_order_removed.order_id, self.order_id)
        self.assertEqual(decoded_order_removed.agent_id, self.agent_id)
        self.assertEqual(decoded_order_removed.id, self.event_id)
        self.assertEqual(decoded_order_removed.type, EventType.ORDER_REMOVED)

    def test_ordering(self):
        earlier_order_removed = EventOrderRemoved(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_order_removed < self.order_removed)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.order_removed.type.name}, ID: {self.order_removed.id}, "
            f"Time: {self.order_removed.timestamp}, Trigger ID: {self.order_removed.trigger_event_id}, "
            f"Message: {self.order_removed.message}"
        )
        self.assertEqual(str(self.order_removed), expected_str)