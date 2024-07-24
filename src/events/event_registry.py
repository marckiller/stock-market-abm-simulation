class EventRegistry:
    
    registry = {}

    @classmethod
    def register_event(cls, event_type, event_class):
        cls.registry[event_type] = event_class

    @classmethod
    def get_event_class(cls, event_type):
        return cls.registry.get(event_type, None)