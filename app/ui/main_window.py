from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Optional, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
)

from app.core.events import EventBus
from app.data.repositories import TaskRepository
from app.domain.models import Task

# наши новые/существующие вьюшки
from app.ui.views.toolbar import MainToolbar        # твой тулбар
from app.ui.views.task_tree import TaskTree        # твоё дерево задач
from app.ui.views.task_editor import TaskEditor    # твой редактор
from app.ui.views.statusbar import MainStatusBar   # твой статусбар
from app.ui.views.sidebar import SideBar           # новый сайдбар
from app.ui.views.kanban import KanbanBoard        # новая канбан-доска
from app.ui.views.calendar_panel import CalendarPanel  # новый календарь
from app.usecases.add_task import AddTask, AddTaskInput
from app.usecases.delete_task import DeleteTask, DeleteTaskInput


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("TasPy — Task Manager")

        # доменная часть
        self.bus = EventBus()
        self.repo = TaskRepository()

        # ui
        self._build_ui()

        # если БД пустая — засеять примером
        self._seed_if_empty()

        # первый прогруз канбана/календаря
        self._reload_kanban()
        self._reload_calendar_for_date(self.calendar_panel.current_date())

    # ==============================
    #   UI построение
    # ==============================

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- toolbar сверху ----
        # MainToolbar signature in project is (parent, repo, bus)
        self.toolbar = MainToolbar(self, self.repo, self.bus)
        self.addToolBar(self.toolbar)

        # ---- центральный сплиттер ----
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.setHandleWidth(3)

        # ---- левая колонка: sidebar + tree ----
        left_container = QWidget(self)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(4)

        self.sidebar = SideBar(self)
        self.task_tree = TaskTree(self.repo, self.bus)

        left_layout.addWidget(self.sidebar)
        left_layout.addWidget(self.task_tree, 1)

        splitter.addWidget(left_container)

        # ---- центр: вкладки Дерево / Канбан ----
        center_tabs = QTabWidget(self)
        center_tabs.setDocumentMode(True)

        # во вкладку "Дерево" кладём то же самое дерево (чтобы можно было разворачивать на центр)
        # если не нужно дублировать — можно сделать другой layout
        tree_container = QWidget(self)
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(4, 4, 4, 4)
        tree_layout.setSpacing(4)
        tree_layout.addWidget(self.task_tree)
        center_tabs.addTab(tree_container, "Дерево")

        self.kanban = KanbanBoard(self.repo, self.bus)
        center_tabs.addTab(self.kanban, "Канбан")

        splitter.addWidget(center_tabs)

        # ---- правая колонка: Календарь / Редактор ----
        right_tabs = QTabWidget(self)
        right_tabs.setDocumentMode(True)

        self.calendar_panel = CalendarPanel(self.repo, self.bus)
        self.task_editor = TaskEditor(self.repo, self.bus)

        right_tabs.addTab(self.calendar_panel, "Календарь")
        right_tabs.addTab(self.task_editor, "Редактор")

        splitter.addWidget(right_tabs)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)

        main_layout.addWidget(splitter, 1)

        # ---- статусбар ----
        self.statusbar = MainStatusBar(self.repo, self.bus)
        self.setStatusBar(self.statusbar)

        # ======================
        #   сигналы/слоты
        # ======================

        # выбор задачи в дереве → загрузка в редактор
        self.task_tree.selection_changed.connect(self._on_task_selected)
        if hasattr(self.task_tree, "context_action"):
            self.task_tree.context_action.connect(self._on_task_context)

        # сайдбар фильтры
        self.sidebar.searchChanged.connect(self._on_search_changed)
        self.sidebar.statusChanged.connect(self._on_status_filter_changed)
        self.sidebar.categoryChanged.connect(self._on_category_filter_changed)
        self.sidebar.quickFilterSelected.connect(self._on_quick_filter)

        if hasattr(self.kanban, "context_action"):
            self.kanban.context_action.connect(self._on_task_context)

        # канбан drag&drop → смена статуса (Kanban сам обновляет статус в репозитории)
        # if your Kanban emits a statusChangeRequested signal, connect it here

        # календарь
        self.calendar_panel.dateChanged.connect(self._on_calendar_date_changed)
        self.calendar_panel.taskActivated.connect(self._on_calendar_task_activated)

        # обновлять статусбар при изменениях
        # предполагаю, что MainStatusBar сам подписан на EventBus,
        # но на всякий случай можно дергать ручной апдейт, если там есть метод update_counts()
        if hasattr(self.statusbar, "update_counts"):
            self.bus.subscribe("*", lambda _: self.statusbar.update_counts())  # примитивный вариант

    # ==============================
    #   Seed данных
    # ==============================

    def _seed_if_empty(self) -> None:
        roots = self.repo.all_roots()
        if roots:
            return

        root = Task(
            title="Учёба",
            description="Корневая задача для учебы",
            status="todo",
            priority=2,
            category="Учёба",
        )
        root = self.repo.add(root)

        child = Task(
            title="DevOps",
            parent_id=root.id,
            status="todo",
            priority=3,
            category="Учёба",
        )
        self.repo.add(child)

        child2 = Task(
            title="Cloud Computing",
            parent_id=root.id,
            status="todo",
            priority=3,
            category="Учёба",
        )
        self.repo.add(child2)

        # обновим дерево и канбан
        if hasattr(self.task_tree, "reload"):
            self.task_tree.reload()
        self._reload_kanban()
        self._reload_calendar_for_date(self.calendar_panel.current_date())

    # ==============================
    #   Канбан / календарь
    # ==============================

    def _all_tasks(self) -> List[Task]:
        tasks: List[Task] = []
        for root in self.repo.all_roots():
            subtree = self.repo.subtree(root.id) if root.id is not None else []
            tasks.extend(subtree)
        return tasks

    def _reload_kanban(self) -> None:
        tasks = self._all_tasks()
        self.kanban.set_tasks(tasks)

    def _reload_calendar_for_date(self, d: date) -> None:
        tasks_for_day: List[Task] = []
        for t in self._all_tasks():
            if t.due_at and t.due_at.date() == d:
                tasks_for_day.append(t)
        self.calendar_panel.set_tasks_for_day(tasks_for_day)

    # ==============================
    #   Обработчики сигналов
    # ==============================

    def _on_task_selected(self, task_id: int) -> None:
        if task_id <= 0:
            self.task_editor.clear()
            return
        self.task_editor.load_task(task_id)

    def _on_search_changed(self, text: str) -> None:
        # здесь зависит от реализации TaskTree — часто там есть метод apply_filter(...)
        if hasattr(self.task_tree, "apply_text_filter"):
            self.task_tree.apply_text_filter(text)

    def _on_status_filter_changed(self, status: str) -> None:
        if hasattr(self.task_tree, "apply_status_filter"):
            self.task_tree.apply_status_filter(status)

    def _on_category_filter_changed(self, category: str) -> None:
        if hasattr(self.task_tree, "apply_category_filter"):
            self.task_tree.apply_category_filter(category)

    def _on_quick_filter(self, key: str) -> None:
        # пока можно просто логировать или в будущем сделать умный фильтр
        print("[TasPy] quick filter selected:", key)

    def _on_task_context(self, action: str, task_id: int) -> None:
        new_task = None
        if action == "new":
            new_task = AddTask(self.repo, self.bus).execute(AddTaskInput(None, "Новая задача"))
        elif action == "add_sub" and task_id > 0:
            new_task = AddTask(self.repo, self.bus).execute(AddTaskInput(task_id, "Подзадача"))
        elif action == "delete" and task_id > 0:
            DeleteTask(self.repo, self.bus).execute(DeleteTaskInput(task_id, cascade=True))

        self._refresh_after_mutation(new_task.id if new_task else None)

    def _on_kanban_status_change(self, task_id: int, new_status: str) -> None:
        # меняем статус задачи и обновляем канбан/дерево
        task = self.repo.get(task_id)
        if not task:
            return
        self.repo.update(task_id, status=new_status)

        if hasattr(self.task_tree, "reload"):
            self.task_tree.reload()
        self._reload_kanban()
        self._reload_calendar_for_date(self.calendar_panel.current_date())

    def _on_calendar_date_changed(self, d: date) -> None:
        self._reload_calendar_for_date(d)

    def _on_calendar_task_activated(self, task_id: int) -> None:
        # например, выделить её в дереве (если у TaskTree есть select_task)
        if hasattr(self.task_tree, "select_task"):
            self.task_tree.select_task(task_id)
        self.task_editor.load_task(task_id)

    # Helper used by toolbar to get currently selected task id
    def get_current_id(self) -> Optional[int]:
        if hasattr(self.task_tree, "current_task_id"):
            return self.task_tree.current_task_id()
        return None

    def _refresh_after_mutation(self, select_id: int | None = None) -> None:
        if hasattr(self.task_tree, "reload"):
            self.task_tree.reload()
        self._reload_kanban()
        self._reload_calendar_for_date(self.calendar_panel.current_date())
        if hasattr(self.statusbar, "update_counts"):
            self.statusbar.update_counts()
        if select_id:
            if hasattr(self.task_tree, "select_task"):
                self.task_tree.select_task(select_id)
            self.task_editor.load_task(select_id)
        else:
            self.task_editor.clear()