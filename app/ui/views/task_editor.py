from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateTimeEdit
from PySide6.QtCore import Qt, QDateTime
from app.data.repositories import TaskRepository
from app.core.events import EventBus
from app.usecases.update_task import UpdateTask, UpdateTaskInput
from app.domain.models import Status

class TaskEditor(QWidget):
    def __init__(self, repo: TaskRepository, bus: EventBus):
        super().__init__()
        self.repo = repo
        self.bus = bus
        self.current_id: int | None = None

        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)

        self.title = QLineEdit()
        self.desc = QTextEdit()
        self.status = QComboBox(); self.status.addItems([Status.TODO, Status.IN_PROGRESS, Status.DONE])
        self.priority = QSpinBox(); self.priority.setRange(1,5); self.priority.setValue(3)
        self.due = QDateTimeEdit(); self.due.setCalendarPopup(True); self.due.setDisplayFormat("yyyy-MM-dd HH:mm")

        lay.addRow("Заголовок", self.title)
        lay.addRow("Описание", self.desc)
        lay.addRow("Статус", self.status)
        lay.addRow("Приоритет", self.priority)
        lay.addRow("Дедлайн", self.due)

        self.title.editingFinished.connect(self._save)
        self.desc.textChanged.connect(self._save)
        self.status.currentIndexChanged.connect(self._save)
        self.priority.valueChanged.connect(self._save)
        self.due.dateTimeChanged.connect(self._save)

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
        if obj.due_at:
            self.due.setDateTime(QDateTime.fromSecsSinceEpoch(int(obj.due_at.timestamp())))
        else:
            self.due.setDateTime(QDateTime.currentDateTime())

    def _clear(self):
        self.current_id = None
        self.title.clear(); self.desc.clear(); self.priority.setValue(3)

    def _save(self, *args):
        if not self.current_id:
            return
        fields = {
            "title": self.title.text(),
            "description": self.desc.toPlainText(),
            "status": self.status.currentText(),
            "priority": int(self.priority.value()),
        }
        dt = self.due.dateTime().toPython()
        fields["due_at"] = dt
        UpdateTask(self.repo, self.bus).execute(UpdateTaskInput(self.current_id, fields))