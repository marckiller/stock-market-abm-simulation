import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_order_modified import EventOrderModified

class TestOrderModifiedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.order_id = 101
        self.initial_quantity = 500
        self.left_quantity = 300
        self.event_id = 999

        self.order_modified = EventOrderModified(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            initial_quantity=self.initial_quantity,
            left_quantity=self.left_quantity,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.order_modified.timestamp, self.timestamp)
        self.assertEqual(self.order_modified.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.order_modified.ticker, self.ticker)
        self.assertEqual(self.order_modified.order_id, self.order_id)
        self.assertEqual(self.order_modified.initial_quantity, self.initial_quantity)
        self.assertEqual(self.order_modified.left_quantity, self.left_quantity)
        self.assertEqual(self.order_modified.id, self.event_id)
        self.assertEqual(self.order_modified.type, EventType.ORDER_MODIFIED)
        self.assertFalse(self.order_modified.executable)

    def test_create_message(self):
        expected_message = (
            f"Order {self.order_id} modified for {self.ticker} from {self.initial_quantity} to {self.left_quantity}."
        )
        self.assertEqual(self.order_modified.create_message(), expected_message)
        self.assertEqual(self.order_modified.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker",
            "order_id", "initial_quantity", "left_quantity"
        ]
        self.assertEqual(self.order_modified.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.order_modified)
        decoded_order_modified = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_order_modified.timestamp, self.timestamp)
        self.assertEqual(decoded_order_modified.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_order_modified.ticker, self.ticker)
        self.assertEqual(decoded_order_modified.order_id, self.order_id)
        self.assertEqual(decoded_order_modified.initial_quantity, self.initial_quantity)
        self.assertEqual(decoded_order_modified.left_quantity, self.left_quantity)
        self.assertEqual(decoded_order_modified.id, self.event_id)
        self.assertEqual(decoded_order_modified.type, EventType.ORDER_MODIFIED)

    def test_ordering(self):
        earlier_order_modified = EventOrderModified(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            order_id=self.order_id,
            initial_quantity=self.initial_quantity,
            left_quantity=self.left_quantity,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_order_modified < self.order_modified)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.order_modified.type.name}, ID: {self.order_modified.id}, "
            f"Time: {self.order_modified.timestamp}, Trigger ID: {self.order_modified.trigger_event_id}, "
            f"Message: {self.order_modified.message}"
        )
        self.assertEqual(str(self.order_modified), expected_str)