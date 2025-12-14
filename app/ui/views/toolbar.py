from PySide6.QtWidgets import QToolBar, QToolButton
from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.usecases.add_task import AddTask, AddTaskInput

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
        b_add.clicked.connect(lambda: AddTask(repo, bus).execute(AddTaskInput(None, "Новая задача")))

        # store helpers for callbacks
        self._parent = parent
        self._repo = repo
        self._bus = bus
