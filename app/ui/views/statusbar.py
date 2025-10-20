from PySide6.QtWidgets import QStatusBar
from app.core.events import EventBus, TaskAdded, TaskDeleted, TaskUpdated, TaskMoved
from app.data.repositories import TaskRepository

class MainStatusBar(QStatusBar):
    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo
        self.bus = bus
        for evt in (TaskAdded, TaskDeleted, TaskUpdated, TaskMoved):
            bus.subscribe(evt, lambda e: self.refresh())
        self.refresh()

    def refresh(self):
        cnt = 0
        def count_tree(pid=None):
            nonlocal cnt
            for t in self.repo.children(pid):
                cnt += 1
                count_tree(t.id)
        count_tree(None)
        self.showMessage(f"Всего задач: {cnt}")