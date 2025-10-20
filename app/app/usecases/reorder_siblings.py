from dataclasses import dataclass
from typing import List, Optional
from app.data.repositories import TaskRepository

@dataclass
class ReorderSiblingsInput:
    parent_id: Optional[int]
    ordered_ids: List[int]

class ReorderSiblings:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def execute(self, inp: ReorderSiblingsInput):
        from app.data.db import session_scope
        from app.domain.models import Task
        with session_scope() as s:
            id_to_idx = {tid: i for i, tid in enumerate(inp.ordered_ids)}
            for tid, idx in id_to_idx.items():
                obj = s.get(Task, tid)
                if obj and obj.parent_id == inp.parent_id:
                    obj.order_index = idx
                    s.add(obj)