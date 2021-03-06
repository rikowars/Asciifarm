


class Event:
    
    def __init__(self):
        self.listeners = {}
    
    def addListener(self, listener, key=None):
        if key is None:
            key = listener
        self.listeners[key] = listener
    
    def removeListener(self, key):
        return self.listeners.pop(key, None)
        
    
    def trigger(self, *args, **kwargs):
        for listener in frozenset(self.listeners.values()):
            listener(*args, **kwargs)
