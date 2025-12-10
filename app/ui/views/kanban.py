from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFrame,
)

from ...domain.models import Task  # type: ignore[import]


@dataclass
class KanbanTaskItem:
    id: int
    title: str
    status: str


class _KanbanColumn(QFrame):
    \"\"\"Одна колонка Kanban (todo / in_progress / done).\"\"\"

    taskDropped = Signal(int, str)  # task_id, target_status

    def __init__(self, title: str, status: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._status = status

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName(f"KanbanColumn-{status}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        header = QLabel(title)
        header.setAlignment(Qt.AlignCenter)
        header.setProperty("kanbanHeader", True)

        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.setDragEnabled(True)
        self.list.setAcceptDrops(True)
        self.list.setDragDropMode(QListWidget.InternalMove)
        self.list.setDefaultDropAction(Qt.MoveAction)
        self.list.viewport().setAcceptDrops(True)
        self.list.setProperty("kanbanList", True)

        layout.addWidget(header)
        layout.addWidget(self.list, 1)

        # перехватываем drop
        self.list.model().rowsInserted.connect(self._on_rows_inserted)

    @property
    def status(self) -> str:
        return self._status

    def clear(self) -> None:
        self.list.clear()

    def add_task(self, item: KanbanTaskItem) -> None:
        lw_item = QListWidgetItem(item.title)
        lw_item.setData(Qt.UserRole, item.id)
        self.list.addItem(lw_item)

    # --- DnD hook ---

    def _on_rows_inserted(self, parent_index, start, end) -> None:
        # Когда элемент перетащили в список, считаем, что его статус нужно
        # сменить на статус текущей колонки.
        for row in range(start, end + 1):
            item = self.list.item(row)
            if not item:
                continue
            task_id = item.data(Qt.UserRole)
            if task_id is not None:
                self.taskDropped.emit(int(task_id), self._status)


class KanbanBoard(QWidget):
    \"\"\"Kanban-доска: три колонки по статусам.

    Используется как чистый виджет уровня UI.
    Внешний код должен:
      - передавать туда список задач через set_tasks(...)
      - подписаться на сигнал statusChangeRequested(task_id, new_status)
      - на этот сигнал дергать use-case UpdateTask/ToggleStatus и перезагружать данные
    \"\"\"

    statusChangeRequested = Signal(int, str)  # task_id, new_status

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName("KanbanBoard")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(8)

        self.todo_column = _KanbanColumn("Todo", "todo", self)
        self.in_progress_column = _KanbanColumn("In progress", "in_progress", self)
        self.done_column = _KanbanColumn("Done", "done", self)

        for col in (self.todo_column, self.in_progress_column, self.done_column):
            col.taskDropped.connect(self._on_task_dropped)
            columns_layout.addWidget(col)

        main_layout.addLayout(columns_layout, 1)

    # --- Публичный API ---

    def set_tasks(self, tasks: List[Task]) -> None:
        \"\"\"Полностью обновить содержимое доски.

        Ожидает список Task (можно уже отфильтрованный по проекту/категории и т.д.).
        \"\"\"
        self.todo_column.clear()
        self.in_progress_column.clear()
        self.done_column.clear()

        for t in tasks:
            if t.id is None:
                continue
            item = KanbanTaskItem(id=t.id, title=t.title, status=t.status)
            if item.status == "todo":
                self.todo_column.add_task(item)
            elif item.status == "in_progress":
                self.in_progress_column.add_task(item)
            elif item.status == "done":
                self.done_column.add_task(item)
            else:
                # неизвестный статус — пусть живёт в todo
                self.todo_column.add_task(item)

    # --- внутреннее ---

    def _on_task_dropped(self, task_id: int, new_status: str) -> None:
        self.statusChangeRequested.emit(task_id, new_status)
