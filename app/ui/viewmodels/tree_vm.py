from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from typing import Optional, List
from app.data.repositories import TaskRepository

class TreeItem:
    def __init__(self, row: dict, parent: Optional["TreeItem"] = None):
        self.row = row   # dict: id, parent_id, title, status, priority, due_at, order_index
        self.parent = parent
        self.children: List["TreeItem"] = []

    def row_idx(self) -> int:
        if not self.parent:
            return 0
        return self.parent.children.index(self)

class TaskTreeModel(QAbstractItemModel):
    def __init__(self, repo: TaskRepository):
        super().__init__()
        self.repo = repo
        self.root_items: List[TreeItem] = []
        self.reload()

    def reload(self):
        self.beginResetModel()
        self.root_items.clear()

        def build(parent_item: Optional[TreeItem], parent_id: Optional[int]):
            for r in self.repo.children_plain(parent_id):  # ← ПЛОСКИЕ ЗАПИСИ ИЗ РЕПО
                node = TreeItem(r, parent_item)
                if parent_item:
                    parent_item.children.append(node)
                else:
                    self.root_items.append(node)
                build(node, r["id"])

        build(None, None)
        self.endResetModel()

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_item = self._item_from_index(parent)
        child = parent_item.children[row] if parent.isValid() else self.root_items[row]
        return self.createIndex(row, column, child)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item: TreeItem = index.internalPointer()
        if item.parent is None:
            return QModelIndex()
        return self.createIndex(item.parent.row_idx(), 0, item.parent)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            item: TreeItem = parent.internalPointer()
            return len(item.children)
        return len(self.root_items)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item: TreeItem = index.internalPointer()
        if role in (Qt.DisplayRole, Qt.EditRole):
            return item.row["title"]
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        base = super().flags(index)
        return base | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False
        item: TreeItem = index.internalPointer()
        from app.usecases.update_task import UpdateTask, UpdateTaskInput
        UpdateTask(self.repo, None).execute(UpdateTaskInput(item.row["id"], {"title": str(value)}))
        item.row["title"] = str(value)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return True

    def supportedDropActions(self):
        return Qt.MoveAction

    def _item_from_index(self, index: QModelIndex) -> Optional[TreeItem]:
        return index.internalPointer() if index.isValid() else None
