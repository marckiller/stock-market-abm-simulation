import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_ticker_removed import EventTickerRemoved

class TestTickerRemovedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.event_id = 999

        self.ticker_removed = EventTickerRemoved(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.ticker_removed.timestamp, self.timestamp)
        self.assertEqual(self.ticker_removed.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.ticker_removed.ticker, self.ticker)
        self.assertEqual(self.ticker_removed.id, self.event_id)
        self.assertEqual(self.ticker_removed.type, EventType.TICKER_REMOVED)
        self.assertFalse(self.ticker_removed.executable)

    def test_create_message(self):
        expected_message = (
            f"Ticker {self.ticker} removed from the market."
        )
        self.assertEqual(self.ticker_removed.create_message(), expected_message)
        self.assertEqual(self.ticker_removed.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker"
        ]
        self.assertEqual(self.ticker_removed.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.ticker_removed)
        decoded_ticker_removed = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_ticker_removed.timestamp, self.timestamp)
        self.assertEqual(decoded_ticker_removed.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_ticker_removed.ticker, self.ticker)
        self.assertEqual(decoded_ticker_removed.id, self.event_id)
        self.assertEqual(decoded_ticker_removed.type, EventType.TICKER_REMOVED)

    def test_ordering(self):
        earlier_ticker_removed = EventTickerRemoved(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_ticker_removed < self.ticker_removed)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.ticker_removed.type.name}, ID: {self.ticker_removed.id}, "
            f"Time: {self.ticker_removed.timestamp}, Trigger ID: {self.ticker_removed.trigger_event_id}, "
            f"Message: {self.ticker_removed.message}"
        )
        self.assertEqual(str(self.ticker_removed), expected_str)