import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_agent_added import EventAgentAdded

class TestAgentAddedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.agent_id = 1
        self.event_id = 999

        self.agent_added = EventAgentAdded(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            agent_id=self.agent_id,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.agent_added.timestamp, self.timestamp)
        self.assertEqual(self.agent_added.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.agent_added.agent_id, self.agent_id)
        self.assertEqual(self.agent_added.id, self.event_id)
        self.assertEqual(self.agent_added.type, EventType.AGENT_ADDED)
        self.assertFalse(self.agent_added.executable)

    def test_create_message(self):
        expected_message = (
            f"Agent {self.agent_id} added to the market."
        )
        self.assertEqual(self.agent_added.create_message(), expected_message)
        self.assertEqual(self.agent_added.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "agent_id"
        ]
        self.assertEqual(self.agent_added.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.agent_added)
        decoded_agent_added = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_agent_added.timestamp, self.timestamp)
        self.assertEqual(decoded_agent_added.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_agent_added.agent_id, self.agent_id)
        self.assertEqual(decoded_agent_added.id, self.event_id)
        self.assertEqual(decoded_agent_added.type, EventType.AGENT_ADDED)

    def test_ordering(self):
        earlier_agent_added = EventAgentAdded(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            agent_id=self.agent_id,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_agent_added < self.agent_added)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.agent_added.type.name}, ID: {self.agent_added.id}, "
            f"Time: {self.agent_added.timestamp}, Trigger ID: {self.agent_added.trigger_event_id}, "
            f"Message: {self.agent_added.message}"
        )
        self.assertEqual(str(self.agent_added), expected_str)
