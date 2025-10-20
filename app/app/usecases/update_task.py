from dataclasses import dataclass
from typing import Dict, Any
from app.data.repositories import TaskRepository
from app.core.events import EventBus, TaskUpdated

@dataclass
class UpdateTaskInput:
    task_id: int
    fields: Dict[str, Any]

class UpdateTask:
    def __init__(self, repo: TaskRepository, bus: EventBus | None):
        self.repo = repo
        self.bus = bus

    def execute(self, inp: UpdateTaskInput):
        obj = self.repo.update(inp.task_id, **inp.fields)
        if obj and self.bus:
            self.bus.emit(TaskUpdated(inp.task_id))
        return obj