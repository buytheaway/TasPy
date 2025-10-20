from typing import List, Optional, Iterable
from sqlmodel import select
from shutil import copy2
from datetime import datetime
from pathlib import Path
from app.domain.models import Task
from .db import session_scope

class TaskRepository:
    def add(self, task: Task) -> Task:
        with session_scope() as s:
            oi = self._next_order_index(s, task.parent_id)
            task.order_index = oi
            s.add(task)
            s.flush()
            return task

    def get(self, task_id: int) -> Optional[Task]:
        with session_scope() as s:
            return s.get(Task, task_id)

    def update(self, task_id: int, **fields) -> Optional[Task]:
        with session_scope() as s:
            obj = s.get(Task, task_id)
            if not obj:
                return None
            for k, v in fields.items():
                setattr(obj, k, v)
            obj.updated_at = datetime.utcnow()
            s.add(obj)
            return obj

    def delete(self, task_id: int, cascade: bool = True) -> None:
        with session_scope() as s:
            target = s.get(Task, task_id)
            if not target:
                return
            ids_to_delete = [target.id]
            if cascade:
                ids_to_delete += [t.id for t in self._subtree(s, task_id) if t.id != task_id]
            for tid in ids_to_delete:
                obj = s.get(Task, tid)
                if obj:
                    s.delete(obj)
            self._reindex_siblings(s, target.parent_id)

    def move(self, task_id: int, new_parent_id: Optional[int], new_order_index: int) -> None:
        with session_scope() as s:
            obj = s.get(Task, task_id)
            if not obj:
                return
            obj.parent_id = new_parent_id
            s.add(obj)
            s.flush()
            self._insert_at_index(s, obj, new_order_index)

    def siblings(self, parent_id: Optional[int]) -> List[Task]:
        with session_scope() as s:
            return s.exec(select(Task).where(Task.parent_id == parent_id).order_by(Task.order_index)).all()

    def children(self, parent_id: Optional[int]) -> List[Task]:
        return self.siblings(parent_id)

    def all_roots(self) -> List[Task]:
        return self.siblings(None)

    def search(self, query: str) -> List[Task]:
        like = f"%{query}%"
        with session_scope() as s:
            return s.exec(select(Task).where((Task.title.like(like)) | (Task.description.like(like)))).all()

    def subtree(self, root_id: int) -> List[Task]:
        with session_scope() as s:
            return list(self._subtree(s, root_id))

    def backup(self, dest_dir: Path) -> Path:
        dest_dir.mkdir(parents=True, exist_ok=True)
        src = Path("tasks.db")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = dest_dir / f"tasks_{ts}.db"
        copy2(src, dst)
        return dst

    # internals
    def _next_order_index(self, s, parent_id: Optional[int]) -> int:
        rows = s.exec(select(Task.order_index).where(Task.parent_id == parent_id).order_by(Task.order_index.desc())).all()
        return (rows[0] if rows else 0) + 1 if rows else 0

    def _reindex_siblings(self, s, parent_id: Optional[int]):
        sibs = s.exec(select(Task).where(Task.parent_id == parent_id).order_by(Task.order_index)).all()
        for i, t in enumerate(sibs):
            if t.order_index != i:
                t.order_index = i
                s.add(t)

    def _insert_at_index(self, s, obj: Task, idx: int):
        sibs = s.exec(select(Task).where(Task.parent_id == obj.parent_id).order_by(Task.order_index)).all()
        idx = max(0, min(idx, len(sibs)))
        for i in range(idx, len(sibs)):
            sibs[i].order_index = i + 1
            s.add(sibs[i])
        obj.order_index = idx
        s.add(obj)

    def _subtree(self, s, root_id: int) -> Iterable[Task]:
        root = s.get(Task, root_id)
        if not root:
            return []
        yield root
        children = s.exec(select(Task).where(Task.parent_id == root_id).order_by(Task.order_index)).all()
        for ch in children:
            yield from self._subtree(s, ch.id)