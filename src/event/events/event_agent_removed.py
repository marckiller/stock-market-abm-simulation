from src.event.event import Event
from src.event.event_types import EventType

class EventAgentRemoved(Event):

    type = EventType.AGENT_REMOVED
    executable = False

    def __init__(self, timestamp: int, trigger_event_id: int, agent_id: int, id: int = None):

        super().__init__(timestamp = timestamp, id = id, trigger_event_id = trigger_event_id, agent_id = agent_id)
        self.create_message()

    def process(self):
        pass

    @classmethod
    def csv_attributes(cls):
        return super().csv_attributes() + ["agent_id"]
    
    def create_message(self):
        return super().create_message() + f"Agent {self.agent_id} removed from the market."