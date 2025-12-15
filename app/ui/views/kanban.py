from datetime import datetime

from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, Signal

from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.usecases.update_task import UpdateTask, UpdateTaskInput
from app.usecases.add_task import AddTask, AddTaskInput
from app.usecases.delete_task import DeleteTask, DeleteTaskInput


class Column(QListWidget):
    def __init__(self, status: str, board: "KanbanBoard"):
        super().__init__()
        self.status = status
        self.board = board
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)

    def dropEvent(self, e):
        super().dropEvent(e)
        # после дропа синхронизируем статусы задач в этой колонке
        self.board._sync_column(self.status)

    def contextMenuEvent(self, event):
        idx = self.indexAt(event.pos())
        menu = QMenu(self)
        if idx.isValid():
            item = self.itemFromIndex(idx)
            tid = item.data(Qt.UserRole)
            act_sub = menu.addAction("↳ Подзадача")
            act_del = menu.addAction("✖ Удалить")
            chosen = menu.exec(event.globalPos())
            if chosen == act_sub:
                self.board.context_action.emit("add_sub", tid)
            elif chosen == act_del:
                self.board.context_action.emit("delete", tid)
        else:
            act_new = menu.addAction("+ Новая задача")
            if menu.exec(event.globalPos()) == act_new:
                self.board.context_action.emit("new", -1)


class KanbanBoard(QWidget):
    open_task = Signal(int)
    context_action = Signal(str, int)  # ("new" | "add_sub" | "delete", task_id_or_-1)

    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo; self.bus = bus
        h = QHBoxLayout(self); h.setContentsMargins(8,8,8,8); h.setSpacing(8)
        self.cols = {}
        for name, title in [("todo","To Do"), ("in_progress","In Progress"), ("done","Done")]:
            v = QVBoxLayout(); v.setSpacing(6)
            v.addWidget(QLabel(title))
            lw = Column(name, self)
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
        for name in self.cols:
            self._sync_column(name)

    def _sync_column(self, name: str):
        lw = self.cols.get(name)
        if not lw:
            return
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
        rows = self.repo.search(self._filters.get("q") or "")
        self._render(rows)

    def _render(self, tasks: list):
        for lw in self.cols.values():
            lw.clear()
        for t in tasks:
            if not self._should_include(t):
                continue
            st = (t.status or "todo").strip()
            if st not in self.cols:
                st = "todo"
            it = QListWidgetItem(f"{t.title} | {t.status} | prio {t.priority or 3}")
            it.setData(Qt.UserRole, t.id)
            self.cols[st].addItem(it)

    def _should_include(self, task) -> bool:
        """Apply current filters to a task."""
        q = (self._filters.get("q") or "").strip()
        if q and q.lower() not in (task.title or "").lower():
            return False

        st_filter = (self._filters.get("status") or "").strip()
        if st_filter and (task.status or "").strip() != st_filter:
            return False

        cat_filter = (self._filters.get("category") or "").strip()
        if cat_filter and (getattr(task, "category", "") or "").strip() != cat_filter:
            return False

        preset = (self._filters.get("preset") or "").strip()
        now = datetime.utcnow()
        if preset == "today":
            return task.due_at and task.due_at.date() == now.date()
        if preset == "week":
            return task.due_at and 0 <= (task.due_at - now).days <= 7
        if preset == "overdue":
            return task.due_at and task.due_at < now
        if preset == "high_priority":
            return (task.priority or 0) <= 2
        return True

    def set_tasks(self, tasks: list):
        """Populate kanban from an explicit tasks list (used by MainWindow)."""
        self._render(tasks)
