from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QSpinBox, QDateTimeEdit, QSizePolicy, QLabel, QDialog,
    QVBoxLayout, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QTextOption
from app.data.repositories import TaskRepository
from app.core.events import EventBus
        # UpdateTask вызывает событие в UI
from app.usecases.update_task import UpdateTask, UpdateTaskInput
from app.domain.models import Status

def _status_values():
    items = []
    for name in ("TODO", "IN_PROGRESS", "DONE"):
        val = getattr(Status, name, None)
        if val is None:
            continue
        items.append(getattr(val, "value", val))
    if not items:
        items = ["todo", "in_progress", "done"]
    return items

class TaskEditor(QWidget):
    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo
        self.bus = bus
        self.current_id: int | None = None

        # поля
        self.title = QLineEdit(placeholderText="Название задачи")
        self.title.setMinimumHeight(36)
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.desc = QTextEdit()
        self.desc.setPlaceholderText("Описание (markdown-лайт)")
        self.desc.setAcceptRichText(False)
        self.desc.setWordWrapMode(QTextOption.WordWrap)
        self.desc.setMinimumHeight(100)
        self.desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.desc.viewport().installEventFilter(self)  # для даблклика

        self.status = QComboBox()
        for it in _status_values(): self.status.addItem(it)

        self.priority = QSpinBox()
        self.priority.setRange(1, 5)
        self.priority.setValue(3)
        self.priority.setMinimumWidth(80)

        self.category = QComboBox()
        self.category.setEditable(True)  # можно руками написать свой тип
        self.category.addItems(["", "Важное", "Работа", "Быт"])

        self.due = QDateTimeEdit()
        self.due.setCalendarPopup(True)
        self.due.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.due.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # таймеры/лейблы
        self.countdown = QLabel("-")
        self.overdue = QLabel("-")
        self.countdown.setToolTip("Времени осталось до дедлайна")
        self.overdue.setToolTip("Сколько прошло после дедлайна (если просрочено)")

        # layout
        form = QFormLayout(self)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        form.setContentsMargins(12, 12, 12, 12)

        form.addRow("Заголовок", self.title)
        form.addRow("Описание", self.desc)

        # мини-ряд с селекторами
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(QLabel("Статус:"))
        row.addWidget(self.status)
        row.addSpacing(12)
        row.addWidget(QLabel("Приоритет:"))
        row.addWidget(self.priority)
        row.addSpacing(12)
        row.addWidget(QLabel("Тип:"))
        row.addWidget(self.category)
        row.addStretch(1)
        form.addRow(row)

        form.addRow("Дедлайн", self.due)
        form.addRow("До дедлайна", self.countdown)
        form.addRow("После дедлайна", self.overdue)

        # --- debounce-автосейв
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(400)
        self._debounce.timeout.connect(self._save_now)

        # --- таймер обновления счётчиков
        self._ticker = QTimer(self)
        self._ticker.setInterval(1000)
        self._ticker.timeout.connect(self._update_timers)
        self._ticker.start()

        # сигналы
        self.title.editingFinished.connect(self._save_now)
        self.desc.textChanged.connect(self._save_debounced)
        self.status.currentIndexChanged.connect(self._save_now)
        self.priority.valueChanged.connect(self._save_now)
        self.category.editTextChanged.connect(self._save_now)
        self.due.dateTimeChanged.connect(self._on_due_changed)

        # авто-resize описания
        self.desc.textChanged.connect(self._auto_resize_desc)

    # ---------- публично ----------
    def load_task(self, task_id: int):
        if task_id == -1:
            self._clear()
            return

        obj = self.repo.get(task_id)
        self.current_id = task_id

        self.title.blockSignals(True)
        self.desc.blockSignals(True)
        self.status.blockSignals(True)
        self.priority.blockSignals(True)
        self.category.blockSignals(True)
        self.due.blockSignals(True)
        try:
            self.title.setText(getattr(obj, "title", "") or "")
            self.desc.setPlainText(getattr(obj, "description", "") or "")

            cur_status = getattr(obj, "status", "") or _status_values()[0]
            if self.status.findText(cur_status) < 0:
                self.status.addItem(cur_status)
            self.status.setCurrentText(cur_status)

            self.priority.setValue(getattr(obj, "priority", 3) or 3)

            cur_cat = getattr(obj, "category", "") or ""
            if cur_cat and self.category.findText(cur_cat) < 0:
                self.category.addItem(cur_cat)
            self.category.setCurrentText(cur_cat)

            if getattr(obj, "due_at", None):
                dt = QDateTime.fromSecsSinceEpoch(int(obj.due_at.timestamp()))
            else:
                dt = QDateTime.currentDateTime()
            self.due.setDateTime(dt)
        finally:
            self.title.blockSignals(False)
            self.desc.blockSignals(False)
            self.status.blockSignals(False)
            self.priority.blockSignals(False)
            self.category.blockSignals(False)
            self.due.blockSignals(False)

        self._update_timers()
        self._auto_resize_desc()

    # внутреннее 
    def _clear(self):
        self.current_id = None
        self.title.clear()
        self.desc.clear()
        self.status.setCurrentIndex(0)
        self.priority.setValue(3)
        self.category.setCurrentText("")
        self.due.setDateTime(QDateTime.currentDateTime())
        self.countdown.setText("-")
        self.overdue.setText("-")

    def _save_debounced(self):
        self._debounce.start()

    def _save_now(self):
        if not self.current_id:
            return
        fields = {
            "title": self.title.text().strip(),
            "description": self.desc.toPlainText(),
            "status": self.status.currentText(),
            "priority": int(self.priority.value()),
            "category": self.category.currentText().strip() or None,
        }
        fields["due_at"] = self.due.dateTime().toPython()
        UpdateTask(self.repo, self.bus).execute(UpdateTaskInput(self.current_id, fields))

    def _on_due_changed(self):
        self._save_now()
        self._update_timers()

    def _update_timers(self):
        if not self.current_id:
            return
        now = QDateTime.currentDateTime()
        due = self.due.dateTime()
        secs = now.secsTo(due)  # >0 осталось, <0 просрочено

        def fmt(total):
            s = abs(int(total))
            d, s = divmod(s, 86400)
            h, s = divmod(s, 3600)
            m, s = divmod(s, 60)
            parts = []
            if d: parts.append(f"{d}д")
            if h or d: parts.append(f"{h}ч")
            if m or h or d: parts.append(f"{m}м")
            parts.append(f"{s}с")
            return " ".join(parts)

        if secs >= 0:
            self.countdown.setText(fmt(secs))
            self.overdue.setText("-")
        else:
            self.countdown.setText("0с")
            self.overdue.setText(fmt(secs))

    def _auto_resize_desc(self):
        doc = self.desc.document()
        doc.adjustSize()
        h = int(doc.size().height()) + 24
        h = max(100, min(h, 300))  # минимум 100, максимум 300
        self.desc.setMinimumHeight(h)

    # даблклик по описанию — полноэкранный редактор
    def eventFilter(self, obj, ev):
        from PySide6.QtCore import QEvent
        if obj is self.desc.viewport() and ev.type() == QEvent.MouseButtonDblClick:
            self._open_fullscreen_desc()
            return True
        return super().eventFilter(obj, ev)

    def _open_fullscreen_desc(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Описание")
        v = QVBoxLayout(dlg)
        te = QTextEdit()
        te.setAcceptRichText(False)
        te.setPlainText(self.desc.toPlainText())
        te.setWordWrapMode(QTextOption.WordWrap)
        v.addWidget(te)
        btns = QHBoxLayout()
        btn_ok = QPushButton("OK"); btn_cancel = QPushButton("Отмена")
        btn_ok.setProperty("accent", True)
        btns.addStretch(1); btns.addWidget(btn_cancel); btns.addWidget(btn_ok)
        v.addLayout(btns)

        def apply_and_close():
            self.desc.setPlainText(te.toPlainText())
            dlg.accept()

        btn_ok.clicked.connect(apply_and_close)
        btn_cancel.clicked.connect(dlg.reject)
        dlg.resize(700, 500)
        dlg.exec()     