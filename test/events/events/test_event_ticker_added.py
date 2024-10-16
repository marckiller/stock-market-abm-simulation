import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_ticker_added import EventTickerAdded

class TestTickerAddedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.event_id = 999

        self.ticker_added = EventTickerAdded(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.ticker_added.timestamp, self.timestamp)
        self.assertEqual(self.ticker_added.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.ticker_added.ticker, self.ticker)
        self.assertEqual(self.ticker_added.id, self.event_id)
        self.assertEqual(self.ticker_added.type, EventType.TICKER_ADDED)
        self.assertFalse(self.ticker_added.executable)

    def test_create_message(self):
        expected_message = (
            f"Ticker {self.ticker} added to the market."
        )
        self.assertEqual(self.ticker_added.create_message(), expected_message)
        self.assertEqual(self.ticker_added.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker"
        ]
        self.assertEqual(self.ticker_added.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.ticker_added)
        decoded_ticker_added = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_ticker_added.timestamp, self.timestamp)
        self.assertEqual(decoded_ticker_added.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_ticker_added.ticker, self.ticker)
        self.assertEqual(decoded_ticker_added.id, self.event_id)
        self.assertEqual(decoded_ticker_added.type, EventType.TICKER_ADDED)

    def test_ordering(self):
        earlier_ticker_added = EventTickerAdded(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_ticker_added < self.ticker_added)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.ticker_added.type.name}, ID: {self.ticker_added.id}, "
            f"Time: {self.ticker_added.timestamp}, Trigger ID: {self.ticker_added.trigger_event_id}, "
            f"Message: {self.ticker_added.message}"
        )
        self.assertEqual(str(self.ticker_added), expected_str)