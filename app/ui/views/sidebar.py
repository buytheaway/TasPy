from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QGridLayout,
)


class SideBar(QWidget):
    """Левая панель фильтров.

    Сигналы:
      - searchChanged(str)         — текст поиска
      - statusChanged(str)         — "" | "todo" | "in_progress" | "done"
      - categoryChanged(str)       — имя категории либо ""
      - quickFilterSelected(str)   — один из: "today", "week", "overdue", "high_priority"
    """

    searchChanged = Signal(str)
    statusChanged = Signal(str)
    categoryChanged = Signal(str)
    quickFilterSelected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName("SideBar")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # --- Поиск ---
        search_box = QGroupBox("Поиск")
        search_layout = QVBoxLayout(search_box)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по задачам…")
        self.search_edit.textChanged.connect(self.searchChanged)

        search_layout.addWidget(self.search_edit)
        main_layout.addWidget(search_box)

        # --- Фильтры статуса/категории ---
        filters_box = QGroupBox("Фильтры")
        filters_layout = QGridLayout(filters_box)

        status_label = QLabel("Статус:")
        self.status_combo = QComboBox()
        self.status_combo.addItem("Все", "")
        self.status_combo.addItem("Todo", "todo")
        self.status_combo.addItem("In progress", "in_progress")
        self.status_combo.addItem("Done", "done")
        self.status_combo.currentIndexChanged.connect(self._on_status_changed)

        category_label = QLabel("Категория:")
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItem("Все")
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        self.category_combo.lineEdit().editingFinished.connect(self._on_category_changed)

        filters_layout.addWidget(status_label, 0, 0)
        filters_layout.addWidget(self.status_combo, 0, 1)
        filters_layout.addWidget(category_label, 1, 0)
        filters_layout.addWidget(self.category_combo, 1, 1)

        main_layout.addWidget(filters_box)

        # --- Быстрые пресеты ---
        quick_box = QGroupBox("Быстрые представления")
        quick_layout = QVBoxLayout(quick_box)

        row1 = QHBoxLayout()
        btn_today = QPushButton("Сегодня")
        btn_week = QPushButton("Неделя")
        row1.addWidget(btn_today)
        row1.addWidget(btn_week)

        row2 = QHBoxLayout()
        btn_overdue = QPushButton("Просроченные")
        btn_high = QPushButton("Высокий приоритет")
        row2.addWidget(btn_overdue)
        row2.addWidget(btn_high)

        btn_today.clicked.connect(lambda: self.quickFilterSelected.emit("today"))
        btn_week.clicked.connect(lambda: self.quickFilterSelected.emit("week"))
        btn_overdue.clicked.connect(lambda: self.quickFilterSelected.emit("overdue"))
        btn_high.clicked.connect(lambda: self.quickFilterSelected.emit("high_priority"))

        quick_layout.addLayout(row1)
        quick_layout.addLayout(row2)

        main_layout.addWidget(quick_box)

        main_layout.addStretch(1)

    # --- API для обновления категорий снаружи ---

    def set_categories(self, categories: list[str]) -> None:
        """Обновить список категорий (без дубликатов, пустые отфильтровываются)."""
        current_text = self.category_combo.currentText()
        self.category_combo.blockSignals(True)

        self.category_combo.clear()
        self.category_combo.addItem("Все")
        for cat in sorted({c for c in categories if c}):
            self.category_combo.addItem(cat)

        # Попробовать восстановить текущий текст
        index = self.category_combo.findText(current_text)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

        self.category_combo.blockSignals(False)

    # --- internal slots ---

    def _on_status_changed(self) -> None:
        value = self.status_combo.currentData()
        self.statusChanged.emit(value or "")

    def _on_category_changed(self) -> None:
        text = self.category_combo.currentText().strip()
        if text == "" or text.lower() == "все":
            self.categoryChanged.emit("")
        else:
            self.categoryChanged.emit(text)
