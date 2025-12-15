from PySide6.QtWidgets import QToolBar, QToolButton, QComboBox
from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.usecases.add_task import AddTask, AddTaskInput
from app.ui.i18n import tr, LANG_OPTIONS, set_lang
from app.core.config import settings


class MainToolbar(QToolBar):
    def __init__(self, parent, repo: TaskRepository, bus: EventBus):
        super().__init__(parent)
        self.repo = repo
        self.bus = bus
        self.setMovable(False)

        def btn(text, accent=False):
            b = QToolButton(self)
            b.setText(text)
            from PySide6.QtCore import Qt
            b.setToolButtonStyle(Qt.ToolButtonTextOnly)
            if accent:
                b.setProperty("accent", True)
            self.addWidget(b)
            return b

        self.b_add = btn(tr("toolbar.new_task"), True)
        self.b_add.clicked.connect(lambda: AddTask(repo, bus).execute(AddTaskInput(None, tr("toolbar.new_task_title"))))

        self.lang = QComboBox(self)
        for code, label in LANG_OPTIONS:
            self.lang.addItem(label, code)
        current = getattr(settings, "lang", "ru") or "ru"
        idx = self.lang.findData(current)
        if idx >= 0:
            self.lang.setCurrentIndex(idx)
        self.lang.currentIndexChanged.connect(self._on_lang_changed)
        self.addWidget(self.lang)

        self._parent = parent
        self._repo = repo
        self._bus = bus

    def _on_lang_changed(self):
        code = self.lang.currentData()
        set_lang(code)
        self._refresh_texts()
        if hasattr(self._parent, "refresh_labels"):
            try:
                self._parent.refresh_labels()
            except Exception:
                pass

    def _refresh_texts(self):
        self.b_add.setText(tr("toolbar.new_task"))
