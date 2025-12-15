from app.data.db import ensure_db
from app.data.repositories import TaskRepository
from app.domain.models import Task


def test_children_plain_returns_category_and_order(tmp_path, monkeypatch):
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "db_path", tmp_path / "test.db", raising=False)
    ensure_db()
    repo = TaskRepository()

    root = repo.add(Task(parent_id=None, title="Root"))
    child1 = repo.add(Task(parent_id=root.id, title="A", category="cat1"))
    child2 = repo.add(Task(parent_id=root.id, title="B", category="cat2"))

    rows = repo.children_plain(root.id)
    assert [r["title"] for r in rows] == [child1.title, child2.title]
    assert rows[0]["category"] == "cat1"
    assert rows[1]["category"] == "cat2"
