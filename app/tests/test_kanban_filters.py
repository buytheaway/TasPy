from types import SimpleNamespace

from app.ui.views.kanban import task_matches_filters


def make_task(**kwargs):
    defaults = dict(title="Test", description="desc", status="todo", priority=3, due_at=None, category="")
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_task_matches_filters_text_and_status():
    task = make_task(title="Hello", description="world", status="in_progress", priority=2)
    assert task_matches_filters(task, {"q": "hello"})
    assert not task_matches_filters(task, {"q": "absent"})
    assert task_matches_filters(task, {"status": "in_progress"})
    assert not task_matches_filters(task, {"status": "done"})


def test_task_matches_filters_presets_and_category():
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    overdue_task = make_task(due_at=now - timedelta(days=1))
    week_task = make_task(due_at=now + timedelta(days=3))
    today_task = make_task(due_at=now)

    assert task_matches_filters(overdue_task, {"preset": "overdue"})
    assert task_matches_filters(week_task, {"preset": "week"})
    assert task_matches_filters(today_task, {"preset": "today"})
    assert not task_matches_filters(today_task, {"preset": "overdue"})

    cat_task = make_task(category="X")
    assert task_matches_filters(cat_task, {"category": "X"})
    assert not task_matches_filters(cat_task, {"category": "Y"})
