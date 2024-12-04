class EventBus:
    
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            if not self.subscribers[event_type]:
                del self.subscribers[event_type]

    def publish(self, event):
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            handler(event)
