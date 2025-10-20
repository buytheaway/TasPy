from PySide6.QtWidgets import QToolBar, QInputDialog, QMessageBox
from PySide6.QtGui import QAction
from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.usecases.add_task import AddTask, AddTaskInput
from app.usecases.delete_task import DeleteTask, DeleteTaskInput
from app.usecases.toggle_status import ToggleStatus, ToggleStatusInput

class MainToolbar(QToolBar):
    def __init__(self, parent=None, repo: TaskRepository=None, bus: EventBus=None):
        super().__init__("MainToolbar", parent)
        self.repo = repo; self.bus = bus

        act_new = QAction("+ Новая", self)
        act_sub = QAction("↳ Подзадача", self)
        act_edit_done = QAction("✓ Готово", self)
        act_del = QAction("⌫ Удалить", self)

        act_new.triggered.connect(self._add_root)
        act_sub.triggered.connect(self._add_child)
        act_edit_done.triggered.connect(self._toggle_done)
        act_del.triggered.connect(self._delete)

        for a in (act_new, act_sub, act_edit_done, act_del):
            self.addAction(a)

    def _current_task_id(self) -> int | None:
        tv = self.parent().centralWidget().widget(0)
        idx = tv.currentIndex()
        if not idx or not idx.isValid():
            return None
        return idx.internalPointer().task.id

    def _add_root(self):
        title, ok = QInputDialog.getText(self, "Новая задача", "Заголовок:")
        if ok and title:
            AddTask(self.repo, self.bus).execute(AddTaskInput(None, title))

    def _add_child(self):
        parent_id = self._current_task_id()
        if not parent_id:
            QMessageBox.information(self, "Подзадача", "Выберите родительскую задачу")
            return
        title, ok = QInputDialog.getText(self, "Подзадача", "Заголовок:")
        if ok and title:
            AddTask(self.repo, self.bus).execute(AddTaskInput(parent_id, title))

    def _toggle_done(self):
        tid = self._current_task_id()
        if tid:
            ToggleStatus(self.repo, self.bus).execute(ToggleStatusInput(tid))

    def _delete(self):
        tid = self._current_task_id()
        if not tid:
            return
        if QMessageBox.question(self, "Удалить", "Удалить ветвь целиком?"):
            DeleteTask(self.repo, self.bus).execute(DeleteTaskInput(tid, cascade=True))