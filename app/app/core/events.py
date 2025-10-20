from dataclasses import dataclass

class EventBus:
    def __init__(self):
        self._subs = {}

    def subscribe(self, event_type, handler):
        self._subs.setdefault(event_type, []).append(handler)

    def emit(self, event):
        for h in self._subs.get(type(event), []):
            h(event)

@dataclass
class TaskAdded:
    task_id: int

@dataclass
class TaskUpdated:
    task_id: int

@dataclass
class TaskDeleted:
    task_id: int

@dataclass
class TaskMoved:
    task_id: int