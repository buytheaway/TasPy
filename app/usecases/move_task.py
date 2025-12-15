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
        if inp.new_parent_id:
            subtree_ids = {t.id for t in self.repo.subtree(inp.task_id)}
            if inp.new_parent_id in subtree_ids:
                # ignore invalid move that would create a cycle
                return
        self.repo.move(inp.task_id, inp.new_parent_id, inp.new_order_index)
        self.bus.emit(TaskMoved(inp.task_id))
