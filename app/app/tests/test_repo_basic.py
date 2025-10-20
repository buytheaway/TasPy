from app.data.db import ensure_db
from app.data.repositories import TaskRepository
from app.domain.models import Task

def test_crud_cycle(tmp_path, monkeypatch):
    from app.core import config as cfg
    monkeypatch.setattr(cfg.settings, "db_path", tmp_path/"test.db", raising=False)
    ensure_db()

    repo = TaskRepository()
    root = repo.add(Task(parent_id=None, title="Root"))
    a = repo.add(Task(parent_id=root.id, title="A"))
    b = repo.add(Task(parent_id=root.id, title="B"))

    assert repo.get(a.id).title == "A"

    repo.update(b.id, title="B2")
    assert repo.get(b.id).title == "B2"

    repo.move(a.id, new_parent_id=None, new_order_index=0)
    assert repo.get(a.id).parent_id is None

    repo.delete(root.id, cascade=True)
    assert repo.get(root.id) is None