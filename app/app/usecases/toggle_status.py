from dataclasses import dataclass
from app.data.repositories import TaskRepository
from app.core.events import EventBus, TaskUpdated
from app.domain.models import Status

@dataclass
class ToggleStatusInput:
    task_id: int

class ToggleStatus:
    def __init__(self, repo: TaskRepository, bus: EventBus):
        self.repo = repo
        self.bus = bus

    def execute(self, inp: ToggleStatusInput):
        obj = self.repo.get(inp.task_id)
        if not obj:
            return
        new_status = Status.DONE if obj.status != Status.DONE else Status.TODO
        self.repo.update(inp.task_id, status=new_status)
        self.bus.emit(TaskUpdated(inp.task_id))