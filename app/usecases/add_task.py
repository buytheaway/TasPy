from dataclasses import dataclass
from typing import Optional
from app.domain.models import Task
from app.data.repositories import TaskRepository
from app.core.events import EventBus, TaskAdded

@dataclass
class AddTaskInput:
    parent_id: Optional[int]
    title: str
    description: str = ""

class AddTask:
    def __init__(self, repo: TaskRepository, bus: EventBus):
        self.repo = repo
        self.bus = bus

    def execute(self, inp: AddTaskInput) -> Task:
        task = Task(parent_id=inp.parent_id, title=inp.title, description=inp.description)
        task = self.repo.add(task)
        if self.bus:
            self.bus.emit(TaskAdded(task.id))
        return task