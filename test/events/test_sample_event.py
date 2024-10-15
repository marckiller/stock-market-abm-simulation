import unittest
from src.event.event import Event
from src.event.event_types import EventType
from src.event.event_csv_manager import EventCsvManager

class SampleObject:

    def __init__(self, value: int = 0):
        self.value = value

    def add_value(self, value: int):
        self.value += value

    def __str__(self):
        return f"SampleObject: {self.value}"

class SampleEvent(Event):

    type = EventType.SIMULATION_START
    executable = True

    def __init__(self, timestamp, id=None, trigger_event_id=None, atr1=None, atr2=None):
        super().__init__(timestamp, id, trigger_event_id, atr1=atr1, atr2=atr2)
    
    def process(self, object: SampleObject):
        object.add_value(1)

    @classmethod
    def csv_attributes(cls):
        return super().csv_attributes() + ["atr1", "atr2"]
    
    def create_message(self):
        return f"SampleEvent occurred at {self.timestamp}"

class TestSampleEvent(unittest.TestCase):

    def test_sample_object_initialization(self):
        obj = SampleObject(100)
        self.assertEqual(obj.value, 100)

    def test_sample_event_process(self):
        obj = SampleObject(100)
        event = SampleEvent(123, 1, 0, atr1="val1", atr2="val2")
        event.process(obj)
        self.assertEqual(obj.value, 101)

    def test_event_csv_encoding_decoding(self):
        event = SampleEvent(123, 1, 0, atr1="val1", atr2="val2")
        csv_row = EventCsvManager.encode_to_csv(event)
        self.assertEqual(csv_row, [1, 123, 1, 0, 'val1', 'val2'])

        decoded_event = EventCsvManager.decode_from_csv(csv_row)
        self.assertIsInstance(decoded_event, SampleEvent)
        self.assertEqual(decoded_event.timestamp, 123)
        self.assertEqual(decoded_event.id, 1)
        self.assertEqual(decoded_event.trigger_event_id, 0)
        self.assertEqual(decoded_event.atr1, 'val1')
        self.assertEqual(decoded_event.atr2, 'val2')