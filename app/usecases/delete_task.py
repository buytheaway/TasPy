from dataclasses import dataclass
from app.data.repositories import TaskRepository
from app.core.events import EventBus, TaskDeleted

@dataclass
class DeleteTaskInput:
    task_id: int
    cascade: bool = True

class DeleteTask:
    def __init__(self, repo: TaskRepository, bus: EventBus):
        self.repo = repo
        self.bus = bus

    def execute(self, inp: DeleteTaskInput):
        self.repo.delete(inp.task_id, inp.cascade)
        self.bus.emit(TaskDeleted(inp.task_id))