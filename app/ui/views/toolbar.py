from PySide6.QtWidgets import QToolBar, QToolButton
from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.usecases.add_task import AddTask, AddTaskInput
from app.usecases.update_task import UpdateTask, UpdateTaskInput
from app.usecases.delete_task import DeleteTask, DeleteTaskInput

class MainToolbar(QToolBar):
    def __init__(self, parent, repo: TaskRepository, bus: EventBus):
        super().__init__(parent)
        self.repo = repo; self.bus = bus
        self.setMovable(False)

        def btn(text, accent=False):
            b = QToolButton(self); b.setText(text)
            # Use Qt enum for clarity (instance attribute is not present in PySide6)
            from PySide6.QtCore import Qt
            b.setToolButtonStyle(Qt.ToolButtonTextOnly)
            if accent: b.setProperty("accent", True)
            self.addWidget(b); return b

        b_add = btn("+ Новая", True)
        b_sub = btn("↳ Подзадача")
        b_done = btn("✓ Готово")
        b_del = btn("⌫ Удалить")

        b_add.clicked.connect(lambda: AddTask(repo, bus).execute(AddTaskInput(None, "Новая задача")))
        b_sub.clicked.connect(self._add_sub)
        b_done.clicked.connect(self._done)
        b_del.clicked.connect(self._delete)

        # store helpers for callbacks
        self._parent = parent
        self._repo = repo
        self._bus = bus

    def _done(self):
        tid = self.parent().get_current_id()
        if not tid: return
        print(f"[Toolbar] toggling done for tid={tid}")
        obj = self.repo.get(tid)
        new_status = "done" if obj.status != "done" else "todo"
        UpdateTask(self.repo, self.bus).execute(UpdateTaskInput(tid, {"status": new_status}))

    def _delete(self):
        tid = self.parent().get_current_id()
        if not tid: return
        print(f"[Toolbar] deleting tid={tid}")
        DeleteTask(self.repo, self.bus).execute(DeleteTaskInput(tid, cascade=True))

    def _add_sub(self):
        tid = None
        try:
            tid = self._parent.get_current_id()
        except Exception:
            tid = None
        print(f"[Toolbar] add subtask under parent={tid}")
        AddTask(self._repo, self._bus).execute(AddTaskInput(tid, "Подзадача"))
