import unittest
from src.event.event_types import EventType

class TestEventType(unittest.TestCase):
    
    def test_enum_values(self):
        event_types = list(EventType)
        event_type_values = [event.value for event in event_types]
        self.assertEqual(len(event_type_values), len(set(event_type_values)), "Enum values are not unique")
    
    def test_enum_members(self):
        expected_members = [
            "SIMULATION_START", "SIMULATION_END", "AGENT_ACTION",
            "AGENT_ACTION_REJECTED", "AGENT_ACTION_ACCEPTED",
            "LIMIT_BUY_ORDER", "LIMIT_SELL_ORDER", "MARKET_BUY_ORDER", "MARKET_SELL_ORDER",
            "CANCEL_ORDER", "EXPIRE_ORDER",
            "ORDER_ADDED", "ORDER_REMOVED", "ORDER_MODIFIED", "ORDER_CANCELED",
            "ORDER_EXECUTED", "ORDER_REJECTED", "ORDER_ACCEPTED", "ORDER_EXPIRED", "TRANSACTION",
            "ADD_AGENT", "REMOVE_AGENT", "ADD_TICKER", "REMOVE_TICKER",
            "AGENT_ADDED", "AGENT_REMOVED", "TICKER_ADDED", "TICKER_REMOVED",
            "AGENT_ORDER", "AGENT_TRADE",
            "ABSTRACT_EVENT"
        ]
        actual_members = [event.name for event in EventType]
        self.assertListEqual(actual_members, expected_members, "Enum members do not match expected members")

    def test_enum_member_access(self):
        self.assertIsInstance(EventType.LIMIT_BUY_ORDER, EventType)
        self.assertIsInstance(EventType.SIMULATION_END, EventType)

    def test_enum_auto_values(self):
        self.assertEqual(EventType.SIMULATION_START.value, 1)
        self.assertEqual(EventType.SIMULATION_END.value, 2)
        self.assertEqual(EventType.AGENT_ACTION.value, 3)
        self.assertEqual(EventType.AGENT_ACTION_REJECTED.value, 4)
        self.assertEqual(EventType.AGENT_ACTION_ACCEPTED.value, 5)
        self.assertEqual(EventType.LIMIT_BUY_ORDER.value, 6)
        self.assertEqual(EventType.LIMIT_SELL_ORDER.value, 7)
        self.assertEqual(EventType.MARKET_BUY_ORDER.value, 8)
        self.assertEqual(EventType.MARKET_SELL_ORDER.value, 9)
        self.assertEqual(EventType.CANCEL_ORDER.value, 10)
        self.assertEqual(EventType.ABSTRACT_EVENT.value, 0)
