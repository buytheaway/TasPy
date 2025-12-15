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

from app.ui.i18n import tr


class SideBar(QWidget):
    """Side bar with search and filters.

    Signals:
      - searchChanged(str)
      - statusChanged(str)
      - categoryChanged(str)
      - quickFilterSelected(str)
    """

    searchChanged = Signal(str)
    statusChanged = Signal(str)
    categoryChanged = Signal(str)
    quickFilterSelected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName("SideBar")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(10)

        self._build_search()
        self._build_filters()
        self._build_quick_filters()

        self.main_layout.addStretch(1)

    def _build_search(self):
        self.search_box = QGroupBox(tr("sidebar.search"))
        search_layout = QVBoxLayout(self.search_box)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("sidebar.search.placeholder"))
        self.search_edit.textChanged.connect(self.searchChanged)

        search_layout.addWidget(self.search_edit)
        self.main_layout.addWidget(self.search_box)

    def _build_filters(self):
        self.filters_box = QGroupBox(tr("sidebar.filters"))
        filters_layout = QGridLayout(self.filters_box)

        self.status_label = QLabel(tr("sidebar.status"))
        self.status_combo = QComboBox()
        self.status_combo.addItem(tr("sidebar.any"), "")
        self.status_combo.addItem(tr("kanban.todo"), "todo")
        self.status_combo.addItem(tr("kanban.in_progress"), "in_progress")
        self.status_combo.addItem(tr("kanban.done"), "done")
        self.status_combo.currentIndexChanged.connect(self._on_status_changed)

        self.category_label = QLabel(tr("sidebar.category"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItem(tr("sidebar.any"))
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        self.category_combo.lineEdit().editingFinished.connect(self._on_category_changed)

        filters_layout.addWidget(self.status_label, 0, 0)
        filters_layout.addWidget(self.status_combo, 0, 1)
        filters_layout.addWidget(self.category_label, 1, 0)
        filters_layout.addWidget(self.category_combo, 1, 1)

        self.main_layout.addWidget(self.filters_box)

    def _build_quick_filters(self):
        quick_box = QGroupBox(tr("sidebar.quick"))
        quick_layout = QVBoxLayout(quick_box)

        row1 = QHBoxLayout()
        btn_today = QPushButton(tr("sidebar.today"))
        btn_week = QPushButton(tr("sidebar.week"))
        row1.addWidget(btn_today)
        row1.addWidget(btn_week)

        row2 = QHBoxLayout()
        btn_overdue = QPushButton(tr("sidebar.overdue"))
        btn_high = QPushButton(tr("sidebar.high"))
        row2.addWidget(btn_overdue)
        row2.addWidget(btn_high)

        btn_today.clicked.connect(lambda: self.quickFilterSelected.emit("today"))
        btn_week.clicked.connect(lambda: self.quickFilterSelected.emit("week"))
        btn_overdue.clicked.connect(lambda: self.quickFilterSelected.emit("overdue"))
        btn_high.clicked.connect(lambda: self.quickFilterSelected.emit("high_priority"))

        quick_layout.addLayout(row1)
        quick_layout.addLayout(row2)

        self.main_layout.addWidget(quick_box)

    # --- API ---

    def set_categories(self, categories: list[str]) -> None:
        current_text = self.category_combo.currentText()
        self.category_combo.blockSignals(True)

        self.category_combo.clear()
        self.category_combo.addItem(tr("sidebar.any"))
        for cat in sorted({c for c in categories if c}):
            self.category_combo.addItem(cat)

        index = self.category_combo.findText(current_text)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

        self.category_combo.blockSignals(False)

    def refresh_labels(self) -> None:
        """Update labels after language switch."""
        self.search_box.setTitle(tr("sidebar.search"))
        self.search_edit.setPlaceholderText(tr("sidebar.search.placeholder"))
        self.filters_box.setTitle(tr("sidebar.filters"))
        self.status_label.setText(tr("sidebar.status"))
        self.category_label.setText(tr("sidebar.category"))
        # repopulate combos with translated labels while preserving data
        status_data = [self.status_combo.itemData(i) for i in range(self.status_combo.count())]
        status_selected = self.status_combo.currentData()
        self.status_combo.blockSignals(True)
        self.status_combo.clear()
        labels = [tr("sidebar.any"), tr("kanban.todo"), tr("kanban.in_progress"), tr("kanban.done")]
        data = ["", "todo", "in_progress", "done"]
        for lbl, d in zip(labels, data):
            self.status_combo.addItem(lbl, d)
        idx = self.status_combo.findData(status_selected)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)
        self.status_combo.blockSignals(False)

    # --- internal slots ---

    def _on_status_changed(self) -> None:
        value = self.status_combo.currentData()
        self.statusChanged.emit(value or "")

    def _on_category_changed(self) -> None:
        text = self.category_combo.currentText().strip()
        if text == "" or text.lower() == tr("sidebar.any").lower():
            self.categoryChanged.emit("")
        else:
            self.categoryChanged.emit(text)
