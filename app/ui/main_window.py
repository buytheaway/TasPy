from PySide6.QtWidgets import QMainWindow, QSplitter
from PySide6.QtCore import Qt
from app.core.events import EventBus
from app.data.repositories import TaskRepository
from .views.task_tree import TaskTree
from .views.task_editor import TaskEditor
from .views.toolbar import MainToolbar
from .views.statusbar import MainStatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskTree")

        self.bus = EventBus()
        self.repo = TaskRepository()

        self.toolbar = MainToolbar(self, repo=self.repo, bus=self.bus)
        self.addToolBar(self.toolbar)

        self.tree = TaskTree(repo=self.repo, bus=self.bus)
        self.editor = TaskEditor(repo=self.repo, bus=self.bus)
        self.tree.selection_changed.connect(self.editor.load_task)

        split = QSplitter(Qt.Horizontal)
        split.addWidget(self.tree)
        split.addWidget(self.editor)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 2)
        self.setCentralWidget(split)

        self.status = MainStatusBar(repo=self.repo, bus=self.bus)
        self.setStatusBar(self.status)

        self._seed_if_empty()

    def _seed_if_empty(self):
        if not self.repo.all_roots():
            from app.usecases.add_task import AddTask, AddTaskInput
            add = AddTask(self.repo, self.bus)
            root = add.execute(AddTaskInput(None, "Учёба"))
            add.execute(AddTaskInput(root.id, "Физика"))
            add.execute(AddTaskInput(root.id, "Математика"))
            work = add.execute(AddTaskInput(None, "Работа"))
            add.execute(AddTaskInput(work.id, "Спринт-1"))