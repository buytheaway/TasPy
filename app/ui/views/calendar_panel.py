from PySide6.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QDate
from datetime import date
from app.data.repositories import TaskRepository
from app.core.events import EventBus


class CalendarPanel(QWidget):
    dateChanged = Signal(object)
    taskActivated = Signal(int)

    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo; self.bus = bus
        v = QVBoxLayout(self); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        self.cal = QCalendarWidget()
        self.list = QListWidget()
        v.addWidget(self.cal); v.addWidget(self.list, 1)
        self._filters = {}

        self.cal.selectionChanged.connect(self.reload_for_selected_day)
        # emit higher-level signals expected by MainWindow
        self.cal.selectionChanged.connect(lambda: self.dateChanged.emit(self.current_date()))
        self.list.itemDoubleClicked.connect(lambda it: self.taskActivated.emit(it.data(Qt.UserRole)))

        self.reload_for_selected_day()

    def apply_filters(self, f: dict):
        self._filters = f or {}
        self.reload_for_selected_day()

    def reload_for_selected_day(self):
        self.list.clear()
        sel = self.cal.selectedDate()
        q = self._filters.get("q") or ""
        rows = self.repo.search(q)
        for t in rows:
            if not getattr(t, "due_at", None): continue
            d = QDate(t.due_at.year, t.due_at.month, t.due_at.day)
            if d != sel: continue
            it = QListWidgetItem(f"{t.title} • {t.status} • prio {t.priority or 3}")
            it.setData(Qt.UserRole, t.id)
            self.list.addItem(it)

    def current_date(self) -> date:
        qd = self.cal.selectedDate()
        return date(qd.year(), qd.month(), qd.day())

    def set_tasks_for_day(self, tasks: list):
        """Populate the list from an explicit tasks list (used by MainWindow)."""
        self.list.clear()
        for t in tasks:
            item = QListWidgetItem(f"{t.title} • {t.status} • prio {t.priority or 3}")
            item.setData(Qt.UserRole, t.id)
            self.list.addItem(item)
