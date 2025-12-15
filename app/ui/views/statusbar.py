from datetime import datetime

from PySide6.QtWidgets import QStatusBar

from app.core.events import EventBus, TaskAdded, TaskDeleted, TaskUpdated, TaskMoved
from app.data.repositories import TaskRepository
from app.domain.models import Status
from app.ui.i18n import tr


class MainStatusBar(QStatusBar):
    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo
        self.bus = bus
        for evt in (TaskAdded, TaskDeleted, TaskUpdated, TaskMoved):
            bus.subscribe(evt, lambda e: self.refresh())
        self.refresh()

    def refresh(self):
        total = 0
        by_status = {
            Status.TODO.value: 0,
            Status.IN_PROGRESS.value: 0,
            Status.DONE.value: 0,
        }
        overdue = 0
        now = datetime.utcnow()

        def walk(pid=None):
            nonlocal total, overdue
            for t in self.repo.children(pid):
                total += 1
                key = (t.status or Status.TODO.value)
                by_status[key] = by_status.get(key, 0) + 1
                if t.due_at and t.due_at < now and (t.status or "") != Status.DONE.value:
                    overdue += 1
                walk(t.id)

        walk(None)
        msg = " | ".join(
            [
                tr("statusbar.summary", total=total),
                tr("statusbar.todo", todo=by_status.get(Status.TODO.value, 0)),
                tr("statusbar.in_progress", in_progress=by_status.get(Status.IN_PROGRESS.value, 0)),
                tr("statusbar.done", done=by_status.get(Status.DONE.value, 0)),
                tr("statusbar.overdue", overdue=overdue),
            ]
        )
        self.showMessage(msg)
