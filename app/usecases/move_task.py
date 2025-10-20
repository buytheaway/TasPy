from dataclasses import dataclass
from typing import Optional
from app.data.repositories import TaskRepository
from app.core.events import EventBus, TaskMoved

@dataclass
class MoveTaskInput:
    task_id: int
    new_parent_id: Optional[int]
    new_order_index: int

class MoveTask:
    def __init__(self, repo: TaskRepository, bus: EventBus):
        self.repo = repo
        self.bus = bus

    def execute(self, inp: MoveTaskInput):
        # TODO: запретить перенос в своего потомка (валидация цикла)
        self.repo.move(inp.task_id, inp.new_parent_id, inp.new_order_index)
        self.bus.emit(TaskMoved(inp.task_id))