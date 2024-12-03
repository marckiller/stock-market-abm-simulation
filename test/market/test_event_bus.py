import unittest

from src.market.event_bus import EventBus
from src.market.events import Event

class TestEventBus(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.events_handled = []

    def test_subscribe_and_publish(self):
        def handler(event):
            self.events_handled.append(event)

        self.event_bus.subscribe('test_event', handler)
        event = Event(event_type='test_event', timestamp=123)
        self.event_bus.publish(event)

        self.assertEqual(len(self.events_handled), 1)
        self.assertIs(self.events_handled[0], event)

    def test_unsubscribe(self):
        def handler(event):
            self.events_handled.append(event)

        self.event_bus.subscribe('test_event', handler)
        self.event_bus.unsubscribe('test_event', handler)
        event = Event(event_type='test_event', timestamp=123)
        self.event_bus.publish(event)

        self.assertEqual(len(self.events_handled), 0)

    def test_multiple_handlers(self):
        def handler_one(event):
            self.events_handled.append(('handler_one', event))

        def handler_two(event):
            self.events_handled.append(('handler_two', event))

        self.event_bus.subscribe('test_event', handler_one)
        self.event_bus.subscribe('test_event', handler_two)
        event = Event(event_type='test_event', timestamp=123)
        self.event_bus.publish(event)

        self.assertEqual(len(self.events_handled), 2)
        self.assertEqual(self.events_handled[0], ('handler_one', event))
        self.assertEqual(self.events_handled[1], ('handler_two', event))

    def test_no_subscribers(self):
        event = Event(event_type='no_subscribers_event', timestamp=123)
        try:
            self.event_bus.publish(event)
        except Exception as e:
            self.fail(f"Publishing an event with no subscribers raised an exception: {e}")

    def test_subscribe_different_events(self):
        def handler_one(event):
            self.events_handled.append(('handler_one', event))

        def handler_two(event):
            self.events_handled.append(('handler_two', event))

        self.event_bus.subscribe('event_one', handler_one)
        self.event_bus.subscribe('event_two', handler_two)

        event_one = Event(event_type='event_one', timestamp=123)
        event_two = Event(event_type='event_two', timestamp=456)
        self.event_bus.publish(event_one)
        self.event_bus.publish(event_two)

        self.assertEqual(len(self.events_handled), 2)
        self.assertEqual(self.events_handled[0], ('handler_one', event_one))
        self.assertEqual(self.events_handled[1], ('handler_two', event_two))
