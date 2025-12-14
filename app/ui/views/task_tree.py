from PySide6.QtWidgets import QTreeView, QMenu
from PySide6.QtCore import Signal, QModelIndex, QPoint, Qt
from app.ui.viewmodels.tree_vm import TaskTreeModel
from app.data.repositories import TaskRepository
from app.core.events import EventBus, TaskAdded, TaskDeleted, TaskMoved, TaskUpdated

class TaskTree(QTreeView):
    selection_changed = Signal(int)
    context_action = Signal(str, int)  # ("new" | "add_sub" | "delete", task_id_or_-1)

    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo
        self.bus = bus
        self.model_ = TaskTreeModel(repo)
        self.setModel(self.model_)
        self.setHeaderHidden(True)
        self.setEditTriggers(QTreeView.EditTrigger.EditKeyPressed | QTreeView.EditTrigger.DoubleClicked)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.setExpandsOnDoubleClick(False)
        self.setAnimated(True)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

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

    def current_task_id(self) -> int | None:
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        item = idx.internalPointer()
        return item.row.get("id")

    def select_task(self, task_id: int) -> None:
        """Programmatically focus a task node by id."""
        def find_path(items, target_id):
            for i, itm in enumerate(items):
                if itm.row["id"] == target_id:
                    return [i]
                nested = find_path(itm.children, target_id)
                if nested:
                    return [i] + nested
            return []

        path = find_path(self.model_.root_items, task_id)
        if not path:
            return

        index: QModelIndex = QModelIndex()
        for row in path:
            index = self.model_.index(row, 0, index)
        if index.isValid():
            self.setCurrentIndex(index)
            self.scrollTo(index, QTreeView.PositionAtCenter)

    def reload(self) -> None:
        """Refresh tree contents from repository."""
        self.model_.reload()

    def contextMenuEvent(self, event):
        pos: QPoint = event.pos()
        idx = self.indexAt(pos)
        menu = QMenu(self)
        if idx.isValid():
            item = idx.internalPointer()
            tid = item.row["id"]
            act_sub = menu.addAction("↳ Подзадача")
            act_del = menu.addAction("✖ Удалить")
            chosen = menu.exec(event.globalPos())
            if chosen == act_sub:
                self.context_action.emit("add_sub", tid)
            elif chosen == act_del:
                self.context_action.emit("delete", tid)
        else:
            act_new = menu.addAction("+ Новая задача")
            if menu.exec(event.globalPos()) == act_new:
                self.context_action.emit("new", -1)
