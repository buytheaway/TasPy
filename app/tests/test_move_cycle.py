from app.data.db import ensure_db
from app.data.repositories import TaskRepository
from app.domain.models import Task
from app.usecases.move_task import MoveTask, MoveTaskInput
from app.core.events import EventBus


def test_move_task_prevents_cycle(tmp_path, monkeypatch):
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "db_path", tmp_path / "cycle.db", raising=False)
    ensure_db()
    repo = TaskRepository()
    bus = EventBus()

    root = repo.add(Task(parent_id=None, title="Root"))
    child = repo.add(Task(parent_id=root.id, title="Child"))
    grand = repo.add(Task(parent_id=child.id, title="Grand"))

    MoveTask(repo, bus).execute(MoveTaskInput(task_id=child.id, new_parent_id=grand.id, new_order_index=0))

    # parent should remain unchanged because move is invalid
    assert repo.get(child.id).parent_id == root.id
