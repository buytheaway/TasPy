from PySide6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.ui.views.task_tree import TaskTree
from app.ui.views.task_editor import TaskEditor
from app.ui.views.toolbar import MainToolbar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskTree")
        self.repo = TaskRepository()
        self.bus = EventBus()

        # центральный сплиттер
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.tree = TaskTree(repo=self.repo, bus=self.bus)
        self.editor = TaskEditor(repo=self.repo, bus=self.bus)
        self.tree.selection_changed.connect(self.editor.load_task)

        splitter.addWidget(self.tree)
        splitter.addWidget(self.editor)
        splitter.setStretchFactor(0, 0)   # дерево фиксированнее
        splitter.setStretchFactor(1, 1)   # редактор растягивается
        splitter.setHandleWidth(5)

        # верхний тулбар
        tb = MainToolbar(self, repo=self.repo, bus=self.bus)

        #  контейнер с layout
        root = QWidget()
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(tb)
        lay.addWidget(splitter)

        self.setCentralWidget(root)
        self.resize(1100, 700)

        # сидер на пустую БД — если нужно
        self._seed_if_empty()

    def _seed_if_empty(self):
        if len(self.repo.children_plain(None)) == 0:
            from app.usecases.add_task import AddTask, AddTaskInput
            add = AddTask(self.repo, self.bus)
            root = add.execute(AddTaskInput(None, "Учёба"))
            add.execute(AddTaskInput(root.id, "ДевОпс"))
            add.execute(AddTaskInput(root.id, "Клауд Компьютинг"))
