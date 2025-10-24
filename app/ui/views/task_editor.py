from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QSpinBox, QDateTimeEdit, QLabel, QVBoxLayout, QHBoxLayout,
    QDialog, QPushButton, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QDateTime, QTimer, QEvent
from PySide6.QtGui import QTextOption
from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.usecases.update_task import UpdateTask, UpdateTaskInput
from app.domain.models import Status


def _status_values():
    vals = []
    for n in ("TODO", "IN_PROGRESS", "DONE"):
        v = getattr(Status, n, None)
        if v is None:
            continue
        vals.append(getattr(v, "value", v))
    if not vals:
        vals = ["todo", "in_progress", "done"]
    return vals


class TaskEditor(QWidget):
    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo
        self.bus = bus
        self.current_id: int | None = None

        # --- Верхняя часть (заголовок)
        self.title = QLineEdit()
        self.title.setPlaceholderText("Название задачи")
        self.title.setMinimumHeight(36)

        # --- Короткое описание
        self.desc = QTextEdit()
        self.desc.setPlaceholderText("Описание (markdown-lite)")
        self.desc.setAcceptRichText(False)
        self.desc.setWordWrapMode(QTextOption.WordWrap)
        self.desc.setMinimumHeight(70)  # 👈 меньше, чем было
        self.desc.setMaximumHeight(150)
        self.desc.viewport().installEventFilter(self)  # даблклик → полноэкран

        # --- Блок параметров
        self.status = QComboBox()
        for s in _status_values():
            self.status.addItem(s)

        self.priority = QSpinBox()
        self.priority.setRange(1, 5)
        self.priority.setValue(3)

        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(["", "Работа", "Быт", "Учёба", "Важное"])

        self.due = QDateTimeEdit()
        self.due.setCalendarPopup(True)
        self.due.setDisplayFormat("yyyy-MM-dd HH:mm")

        # --- Таймеры
        self.countdown = QLabel("-")
        self.overdue = QLabel("-")

        # --- Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)
        form.addRow("Заголовок:", self.title)
        form.addRow("Описание:", self.desc)
        layout.addLayout(form)

        # --- Полоса статусов и параметров
        params = QHBoxLayout()
        params.setSpacing(10)
        params.addWidget(QLabel("Статус:"))
        params.addWidget(self.status)
        params.addWidget(QLabel("Приоритет:"))
        params.addWidget(self.priority)
        params.addWidget(QLabel("Тип:"))
        params.addWidget(self.category)
        params.addStretch(1)
        layout.addLayout(params)

        # --- Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # --- Нижний блок с таймерами
        bottom = QFormLayout()
        bottom.setLabelAlignment(Qt.AlignRight)
        bottom.addRow("Дедлайн:", self.due)
        bottom.addRow("До дедлайна:", self.countdown)
        bottom.addRow("После дедлайна:", self.overdue)
        layout.addLayout(bottom)

        # --- Таймер обновления
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timers)
        self.timer.start(1000)

        # --- Сигналы
        self.title.editingFinished.connect(self._save)
        self.desc.textChanged.connect(self._save)
        self.status.currentIndexChanged.connect(self._save)
        self.priority.valueChanged.connect(self._save)
        self.category.editTextChanged.connect(self._save)
        self.due.dateTimeChanged.connect(self._save)

    # --- загрузка задачи ---
    def load_task(self, task_id: int):
        if task_id == -1:
            self._clear()
            return
        obj = self.repo.get(task_id)
        self.current_id = task_id
        self.title.setText(obj.title or "")
        self.desc.setPlainText(obj.description or "")
        self.status.setCurrentText(obj.status)
        self.priority.setValue(obj.priority or 3)
        self.category.setCurrentText(getattr(obj, "category", "") or "")
        if obj.due_at:
            self.due.setDateTime(QDateTime.fromSecsSinceEpoch(int(obj.due_at.timestamp())))
        else:
            self.due.setDateTime(QDateTime.currentDateTime())
        self._update_timers()

    def _clear(self):
        self.current_id = None
        self.title.clear()
        self.desc.clear()
        self.priority.setValue(3)
        self.category.setCurrentIndex(0)
        self.countdown.setText("-")
        self.overdue.setText("-")

    # --- сохранение ---
    def _save(self):
        if not self.current_id:
            return
        fields = {
            "title": self.title.text(),
            "description": self.desc.toPlainText(),
            "status": self.status.currentText(),
            "priority": self.priority.value(),
            "category": self.category.currentText(),
            "due_at": self.due.dateTime().toPython(),
        }
        UpdateTask(self.repo, self.bus).execute(UpdateTaskInput(self.current_id, fields))

    # --- обновление таймеров ---
    def _update_timers(self):
        if not self.current_id:
            return
        now = QDateTime.currentDateTime()
        due = self.due.dateTime()
        secs = now.secsTo(due)
        if secs >= 0:
            self.countdown.setText(self._fmt(secs))
            self.overdue.setText("-")
        else:
            self.countdown.setText("0с")
            self.overdue.setText(self._fmt(secs))

    def _fmt(self, total):
        s = abs(int(total))
        d, s = divmod(s, 86400)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        parts = []
        if d: parts.append(f"{d}д")
        if h: parts.append(f"{h}ч")
        if m: parts.append(f"{m}м")
        parts.append(f"{s}с")
        return " ".join(parts)

    # --- даблклик по описанию ---
    def eventFilter(self, obj, ev):
        if obj is self.desc.viewport() and ev.type() == QEvent.MouseButtonDblClick:
            self._open_full_desc()
            return True
        return super().eventFilter(obj, ev)

    def _open_full_desc(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Редактирование описания")
        layout = QVBoxLayout(dlg)
        edit = QTextEdit()
        edit.setPlainText(self.desc.toPlainText())
        layout.addWidget(edit)
        btns = QHBoxLayout()
        ok = QPushButton("OK"); cancel = QPushButton("Отмена")
        btns.addStretch(1)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

        ok.clicked.connect(lambda: (self.desc.setPlainText(edit.toPlainText()), dlg.accept()))
        cancel.clicked.connect(dlg.reject)
        dlg.resize(700, 500)
        dlg.exec()
