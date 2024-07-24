from abc import ABCMeta
from src.events.event_registry import EventRegistry
from src.events.event_types import EventType

class EventMeta(ABCMeta):

    def __new__(cls, name, bases, class_dict):

        if 'type' not in class_dict:
            raise TypeError(f"Class {name} has no 'type' attribute")
        if 'executable' not in class_dict:
            raise TypeError(f"Class {name} has no 'executable' attribute")
        
        new_cls = super().__new__(cls, name, bases, class_dict)
        
        if 'type' in class_dict:
            if 'type' != EventType.ABSTRACT_EVENT:
                EventRegistry.register_event(new_cls.type.value, new_cls)
            else:
                raise TypeError(f"Class {name} has no 'type' attribute")
            
        if 'executable' in class_dict:
            if 'executable':
                EventRegistry.register_event(new_cls.type, new_cls)
            else:
                raise TypeError(f"Class {name} has no 'executable' attribute")
            
        return new_cls