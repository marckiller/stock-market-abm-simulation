from src.events.event import Event
from src.events.event_registry import EventRegistry

class EventCsvManager:
    
    @staticmethod
    def encode_to_csv(event: Event):
        attributes = event.csv_attributes()
        return [getattr(event, attr, "") if attr != 'type' else getattr(event, attr).value for attr in attributes]
    
    @staticmethod
    def decode_from_csv(csv_row):
        event_type = csv_row[0]
        event_class = EventRegistry.get_event_class(event_type)

        if not event_class:
            raise ValueError(f"No registered event class for type {event_type}")
        
        attrs = event_class.csv_attributes()
        del attrs[0]
        kwargs = {attr: csv_row[i+1] for i, attr in enumerate(attrs) if attr != 'type'}

        return event_class(**kwargs)