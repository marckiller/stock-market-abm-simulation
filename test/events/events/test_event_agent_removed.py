import unittest
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager
from src.event.events.event_agent_removed import EventAgentRemoved

class TestAgentRemovedEvent(unittest.TestCase):

    def setUp(self):
        self.timestamp = 123456789
        self.trigger_event_id = 42
        self.agent_id = 1
        self.event_id = 999

        self.agent_removed = EventAgentRemoved(
            timestamp=self.timestamp,
            trigger_event_id=self.trigger_event_id,
            agent_id=self.agent_id,
            id=self.event_id
        )

    def test_initialization(self):
        self.assertEqual(self.agent_removed.timestamp, self.timestamp)
        self.assertEqual(self.agent_removed.trigger_event_id, self.trigger_event_id)
        self.assertEqual(self.agent_removed.agent_id, self.agent_id)
        self.assertEqual(self.agent_removed.id, self.event_id)
        self.assertEqual(self.agent_removed.type, EventType.AGENT_REMOVED)
        self.assertFalse(self.agent_removed.executable)

    def test_create_message(self):
        expected_message = (
            f"Agent {self.agent_id} removed from the market."
        )
        self.assertEqual(self.agent_removed.create_message(), expected_message)
        self.assertEqual(self.agent_removed.message, expected_message)

    def test_csv_attributes(self):
        expected_attributes = [
            "type", "timestamp", "id", "trigger_event_id", "agent_id"
        ]
        self.assertEqual(self.agent_removed.csv_attributes(), expected_attributes)

    def test_csv_encoding_decoding(self):
        csv_row = EventCsvManager.encode_to_csv(self.agent_removed)
        decoded_agent_removed = EventCsvManager.decode_from_csv(csv_row)

        self.assertEqual(decoded_agent_removed.timestamp, self.timestamp)
        self.assertEqual(decoded_agent_removed.trigger_event_id, self.trigger_event_id)
        self.assertEqual(decoded_agent_removed.agent_id, self.agent_id)
        self.assertEqual(decoded_agent_removed.id, self.event_id)
        self.assertEqual(decoded_agent_removed.type, EventType.AGENT_REMOVED)

    def test_ordering(self):
        earlier_agent_removed = EventAgentRemoved(
            timestamp=self.timestamp - 1,
            trigger_event_id=self.trigger_event_id,
            agent_id=self.agent_id,
            id=self.event_id - 1
        )
        self.assertTrue(earlier_agent_removed < self.agent_removed)

    def test_string_representation(self):
        expected_str = (
            f"Event: {self.agent_removed.type.name}, ID: {self.agent_removed.id}, "
            f"Time: {self.agent_removed.timestamp}, Trigger ID: {self.agent_removed.trigger_event_id}, "
            f"Message: {self.agent_removed.message}"
        )
        self.assertEqual(str(self.agent_removed), expected_str)