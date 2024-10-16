import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_order_added import EventOrderAdded

class TestOrderAddedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.order_id = 101
        self.agent_id = 1
        self.event_id = 999

        self.order_added = EventOrderAdded(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            agent_id=self.agent_id,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.order_added.timestamp, self.timestamp)
        self.assertEqual(self.order_added.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.order_added.ticker, self.ticker)
        self.assertEqual(self.order_added.order_id, self.order_id)
        self.assertEqual(self.order_added.agent_id, self.agent_id)
        self.assertEqual(self.order_added.id, self.event_id)
        self.assertEqual(self.order_added.type, EventType.ORDER_ADDED)
        self.assertFalse(self.order_added.executable)

    def test_create_message(self):
        expected_message = (
            f"Order {self.order_id} added for {self.ticker} by agent {self.agent_id}."
        )
        self.assertEqual(self.order_added.create_message(), expected_message)
        self.assertEqual(self.order_added.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker",
            "order_id", "agent_id"
        ]
        self.assertEqual(EventOrderAdded.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.order_added)
        
        decoded_event = EventCsvManager.decode_from_csv(csv_row)
        self.assertIsInstance(decoded_event, EventOrderAdded)
        self.assertEqual(decoded_event.timestamp, self.timestamp)
        self.assertEqual(decoded_event.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_event.ticker, self.ticker)
        self.assertEqual(decoded_event.order_id, self.order_id)
        self.assertEqual(decoded_event.agent_id, self.agent_id)
        self.assertEqual(decoded_event.id, self.event_id)
        self.assertEqual(decoded_event.type, EventType.ORDER_ADDED)
        self.assertFalse(decoded_event.executable)
        self.assertEqual(decoded_event.message, self.order_added.message)
