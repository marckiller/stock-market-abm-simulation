from abc import ABC, abstractmethod
from src.events.event_types import EventType
from src.events.event_meta import EventMeta

class Event(ABC, metaclass=EventMeta):

    next_id = 0
    type = EventType.ABSTRACT_EVENT
    executable = None

    def __init__(self, timestamp: int, id: int = None, trigger_event_id: int = None, **kwargs):

        self.timestamp = timestamp
        self.trigger_event_id = trigger_event_id

        if id:
            self.id = id
        else:
            self.id = Event.next_id
            Event.next_id += 1

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.message = self.create_message()

    @abstractmethod
    def process(self):
        pass

    @classmethod 
    @abstractmethod
    def csv_attributes(self):
        return ["type", "timestamp", "id", "trigger_event_id"]
    
    @abstractmethod
    def create_message(self):
        return ""
    
    def __lt__(self, other):
        if self.timestamp == other.timestamp:
            return self.id < other.id
        return self.timestamp < other.timestamp
    
    def __str__(self):
        return f"Event: {self.type.name}, ID: {self.id}, Time: {self.timestamp}, Trigger ID: {self.trigger_event_id}, Message: {self.message}"