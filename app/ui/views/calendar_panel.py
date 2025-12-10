from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional

from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCalendarWidget,
    QListWidget,
    QListWidgetItem,
    QLabel,
)

from ...domain.models import Task  # type: ignore[import]


class CalendarPanel(QWidget):
    \"\"\"Панель с календарем и списком задач на выбранный день.

    Это чистый виджет, не лезет сам в базу. Внешний код:
      - подписывается на dateChanged(date)
      - когда дата изменилась, выбирает задачи из репозитория и подает их в set_tasks_for_day(...)
      - по double-click на задаче можно открыть редактор задачи (через сигнал taskActivated)
    \"\"\"

    dateChanged = Signal(date)
    taskActivated = Signal(int)  # task_id

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName("CalendarPanel")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        top_layout = QHBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self._on_date_changed)

        right_layout = QVBoxLayout()
        self.day_label = QLabel()
        self.day_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.tasks_list = QListWidget()
        self.tasks_list.itemDoubleClicked.connect(self._on_item_double_clicked)

        right_layout.addWidget(self.day_label)
        right_layout.addWidget(self.tasks_list, 1)

        top_layout.addWidget(self.calendar, 1)
        top_layout.addLayout(right_layout, 1)

        main_layout.addLayout(top_layout, 1)

        # начальная дата
        self._on_date_changed()

    # --- публичный API ---

    def current_date(self) -> date:
        qd: QDate = self.calendar.selectedDate()
        return date(qd.year(), qd.month(), qd.day())

    def set_tasks_for_day(self, tasks: List[Task]) -> None:
        \"\"\"Обновить список задач на текущий выбранный день.

        Внешний код сам фильтрует по due_at.date() и вызывает эту функцию.
        \"\"\"
        self.tasks_list.clear()
        for t in tasks:
            if t.id is None:
                continue
            item = QListWidgetItem(t.title)
            item.setData(Qt.UserRole, t.id)
            self.tasks_list.addItem(item)

    # --- внутреннее ---

    def _on_date_changed(self) -> None:
        d = self.current_date()
        self.day_label.setText(f"Задачи на {d.strftime('%d.%m.%Y')}")
        self.dateChanged.emit(d)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        task_id = item.data(Qt.UserRole)
        if task_id is not None:
            self.taskActivated.emit(int(task_id))
