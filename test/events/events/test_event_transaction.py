import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_transaction import EventTransaction

class TestTransactionEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.ticker = "AAPL"
        self.quantity = 100
        self.price = 150.0
        self.id_buyer = 1
        self.id_seller = 2
        self.id_buy_order = 101
        self.id_sell_order = 202
        self.event_id = 999

        self.transaction = EventTransaction(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            quantity=self.quantity,
            price=self.price,
            id_buyer=self.id_buyer,
            id_seller=self.id_seller,
            id_buy_order=self.id_buy_order,
            id_sell_order=self.id_sell_order,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.transaction.timestamp, self.timestamp)
        self.assertEqual(self.transaction.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.transaction.ticker, self.ticker)
        self.assertEqual(self.transaction.quantity, self.quantity)
        self.assertEqual(self.transaction.price, self.price)
        self.assertEqual(self.transaction.id_buyer, self.id_buyer)
        self.assertEqual(self.transaction.id_seller, self.id_seller)
        self.assertEqual(self.transaction.id_buy_order, self.id_buy_order)
        self.assertEqual(self.transaction.id_sell_order, self.id_sell_order)
        self.assertEqual(self.transaction.id, self.event_id)
        self.assertEqual(self.transaction.type, EventType.TRANSACTION)
        self.assertFalse(self.transaction.executable)

    def test_create_message(self):
        expected_message = (
            f"Transaction {self.event_id} occurred at {self.timestamp} for "
            f"{self.quantity} shares of {self.ticker} at price {self.price} "
            f"between {self.id_buyer} and {self.id_seller}."
        )
        self.assertEqual(self.transaction.create_message(), expected_message)
        self.assertEqual(self.transaction.message, expected_message)

    def test_csv_attributes(self):

        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "ticker",
            "quantity", "price", "id_buyer", "id_seller",
            "id_buy_order", "id_sell_order"
        ]
        self.assertEqual(self.transaction.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.transaction)
        decoded_transaction = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_transaction.timestamp, self.timestamp)
        self.assertEqual(decoded_transaction.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_transaction.ticker, self.ticker)
        self.assertEqual(decoded_transaction.quantity, self.quantity)
        self.assertEqual(decoded_transaction.price, self.price)
        self.assertEqual(decoded_transaction.id_buyer, self.id_buyer)
        self.assertEqual(decoded_transaction.id_seller, self.id_seller)
        self.assertEqual(decoded_transaction.id_buy_order, self.id_buy_order)
        self.assertEqual(decoded_transaction.id_sell_order, self.id_sell_order)
        self.assertEqual(decoded_transaction.id, self.event_id)
        self.assertEqual(decoded_transaction.type, EventType.TRANSACTION)

    def test_ordering(self):
        earlier_transaction = EventTransaction(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            ticker=self.ticker,
            quantity=self.quantity,
            price=self.price,
            id_buyer=self.id_buyer,
            id_seller=self.id_seller,
            id_buy_order=self.id_buy_order,
            id_sell_order=self.id_sell_order,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_transaction < self.transaction)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.transaction.type.name}, ID: {self.transaction.id}, "
            f"Time: {self.transaction.timestamp}, Trigger ID: {self.transaction.trigger_event_id}, "
            f"Message: {self.transaction.message}"
        )
        self.assertEqual(str(self.transaction), expected_str)