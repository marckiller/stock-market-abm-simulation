import unittest
from src.events.event_types import EventType
from src.events.event import Event

class ConcreteEvent(Event):

    type = EventType.SIMULATION_START
    executable = True

    def __init__(self, timestamp, id=None, trigger_event_id=None, atr1=None, atr2=None):
        super().__init__(timestamp, id, trigger_event_id, atr1=atr1, atr2=atr2)
    
    def process(self):
        print("Processing ConcreteEvent")

    @classmethod
    def csv_attributes(cls):
        return super().csv_attributes() + ["atr1", "atr2"]
    
    def create_message(self):
        return f"SampleEvent occurred at {self.timestamp}"

class TestEvent(unittest.TestCase):
    def setUp(self):
        Event.next_id = 0
        self.event = ConcreteEvent(timestamp=1, trigger_event_id=0, atr1="val1", atr2="val2")

    def test_initialization(self):
        self.assertEqual(self.event.type, EventType.SIMULATION_START)
        self.assertEqual(self.event.timestamp, 1)
        self.assertTrue(self.event.executable)
        self.assertEqual(self.event.trigger_event_id, 0)
        self.assertEqual(self.event.id, 0)
        self.assertEqual(self.event.atr1, "val1")
        self.assertEqual(self.event.atr2, "val2")
        self.assertEqual(self.event.message, "SampleEvent occurred at 1")

    def test_id_increment(self):
        event2 = ConcreteEvent(timestamp=2, trigger_event_id=0)
        self.assertEqual(event2.id, 1)

    def test_comparison(self):
        event2 = ConcreteEvent(timestamp=2, id=2, trigger_event_id=1, atr1="val12", atr2="val22")
        self.assertTrue(self.event < event2)
        self.assertFalse(event2 < self.event)

    def test_csv_attributes(self):
        self.assertEqual(ConcreteEvent.csv_attributes(), ["type", "timestamp", "id", "trigger_event_id", "atr1", "atr2"])

    def test_str(self):
        expected_str = "Event: SIMULATION_START, ID: 0, Time: 1, Trigger ID: 0, Message: SampleEvent occurred at 1"
        self.assertEqual(str(self.event), expected_str)