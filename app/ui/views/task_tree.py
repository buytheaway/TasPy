from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import Signal
from app.ui.viewmodels.tree_vm import TaskTreeModel
from app.data.repositories import TaskRepository
from app.core.events import EventBus, TaskAdded, TaskDeleted, TaskMoved, TaskUpdated

class TaskTree(QTreeView):
    selection_changed = Signal(int)

    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo
        self.bus = bus
        self.model_ = TaskTreeModel(repo)
        self.setModel(self.model_)
        self.setHeaderHidden(True)
        self.setEditTriggers(QTreeView.EditTrigger.EditKeyPressed | QTreeView.EditTrigger.SelectedClicked)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)

        self.selectionModel().selectionChanged.connect(self._on_selection)

        for evt in (TaskAdded, TaskDeleted, TaskMoved, TaskUpdated):
            bus.subscribe(evt, lambda e: self.model_.reload())

    def _on_selection(self, *_):
        idx = self.currentIndex()
        if not idx.isValid():
            self.selection_changed.emit(-1)
            return
        item = idx.internalPointer()
        self.selection_changed.emit(item.row["id"])
