from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.usecases.update_task import UpdateTask, UpdateTaskInput


class Column(QListWidget):
    def __init__(self, status: str):
        super().__init__()
        self.status = status
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)

    def dropEvent(self, e):
        super().dropEvent(e)
        # статус меняем в обработчике сверху


class KanbanBoard(QWidget):
    open_task = Signal(int)

    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo; self.bus = bus
        h = QHBoxLayout(self); h.setContentsMargins(8,8,8,8); h.setSpacing(8)
        self.cols = {}
        for name, title in [("todo","To Do"), ("in_progress","In Progress"), ("done","Done")]:
            v = QVBoxLayout(); v.setSpacing(6)
            v.addWidget(QLabel(title))
            lw = Column(name)
            lw.itemDoubleClicked.connect(lambda it, s=self: s.open_task.emit(it.data(Qt.UserRole)))
            v.addWidget(lw, 1)
            h.addLayout(v, 1)
            self.cols[name] = lw
        self._filters = dict()

        for lw in self.cols.values():
            lw.model().rowsMoved.connect(self._on_rows_moved)

        self.reload()

    def _on_rows_moved(self, *args):
        # после dnd просто проставим статус столбца
        for name, lw in self.cols.items():
            for i in range(lw.count()):
                tid = lw.item(i).data(Qt.UserRole)
                UpdateTask(self.repo, self.bus).execute(UpdateTaskInput(tid, {"status": name}))

    def current_task_id(self):
        cur = None
        for lw in self.cols.values():
            cur = lw.currentItem()
            if cur: break
        return cur.data(Qt.UserRole) if cur else None

    def apply_filters(self, f: dict):
        self._filters = f or {}
        self.reload()

    def reload(self):
        for lw in self.cols.values(): lw.clear()
        rows = self.repo.search(self._filters.get("q") or "")
        # простая фильтрация
        st = self._filters.get("status")
        cat = (self._filters.get("category") or "").strip()
        preset = self._filters.get("preset")

        from datetime import datetime, timedelta
        now = datetime.utcnow()

        def pass_presets(t):
            if preset == "Сегодня":
                return t.due_at and t.due_at.date() == now.date()
            if preset == "Неделя":
                return t.due_at and 0 <= (t.due_at - now).days <= 7
            if preset == "Просроченные":
                return t.due_at and t.due_at < now
            if preset == "Высокий приоритет":
                return (t.priority or 0) <= 2
            return True

    def set_tasks(self, tasks: list):
        """Populate kanban from an explicit tasks list (used by MainWindow)."""
        for lw in self.cols.values(): lw.clear()
        for t in tasks:
            # simple filters
            if self._filters.get("q") and self._filters.get("q") not in (t.title or ""):
                continue
            st = t.status or "todo"
            if st not in self.cols:
                st = "todo"
            it = QListWidgetItem(f"{t.title} • {t.status} • prio {t.priority or 3}")
            it.setData(Qt.UserRole, t.id)
            self.cols[st].addItem(it)

