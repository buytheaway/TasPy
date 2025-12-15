from __future__ import annotations

from app.core.config import settings

LANG_OPTIONS = [("ru", "Русский"), ("en", "English")]

_T = {
    "app.title": {"ru": "TasPy Диспетчер задач", "en": "TasPy Task Manager"},
    "toolbar.add": {"ru": "+ Новая задача", "en": "+ New task"},
    "statusbar.summary": {"ru": "Всего: {total}", "en": "Total: {total}"},
    "statusbar.todo": {"ru": "В работе: {todo}", "en": "Todo: {todo}"},
    "statusbar.in_progress": {"ru": "В процессе: {in_progress}", "en": "In progress: {in_progress}"},
    "statusbar.done": {"ru": "Готово: {done}", "en": "Done: {done}"},
    "statusbar.overdue": {"ru": "Просрочено: {overdue}", "en": "Overdue: {overdue}"},
    "sidebar.search": {"ru": "Поиск", "en": "Search"},
    "sidebar.search.placeholder": {"ru": "Искать по заголовку", "en": "Search by title"},
    "sidebar.filters": {"ru": "Фильтры", "en": "Filters"},
    "sidebar.status": {"ru": "Статус:", "en": "Status:"},
    "sidebar.category": {"ru": "Категория:", "en": "Category:"},
    "sidebar.any": {"ru": "Любой", "en": "Any"},
    "sidebar.quick": {"ru": "Быстрые фильтры", "en": "Quick filters"},
    "sidebar.today": {"ru": "Сегодня", "en": "Today"},
    "sidebar.week": {"ru": "Неделя", "en": "Week"},
    "sidebar.overdue": {"ru": "Просрочено", "en": "Overdue"},
    "sidebar.high": {"ru": "Высокий приоритет", "en": "High priority"},
    "kanban.todo": {"ru": "К выполнению", "en": "To Do"},
    "kanban.in_progress": {"ru": "В процессе", "en": "In Progress"},
    "kanban.done": {"ru": "Готово", "en": "Done"},
    "kanban.add_sub": {"ru": "➕ Подзадача", "en": "➕ Add subtask"},
    "kanban.delete": {"ru": "✖ Удалить", "en": "✖ Delete"},
    "kanban.new_task": {"ru": "+ Новая задача", "en": "+ New task"},
    "toolbar.new_task": {"ru": "+ Новая задача", "en": "+ New task"},
    "toolbar.new_task_title": {"ru": "Новая задача", "en": "New task"},
    "toolbar.language": {"ru": "Язык", "en": "Language"},
    "task.subtask_title": {"ru": "Подзадача", "en": "Subtask"},
}


def tr(key: str, **fmt) -> str:
    lang = getattr(settings, "lang", "ru") or "ru"
    bucket = _T.get(key, {})
    text = bucket.get(lang) or bucket.get("en") or key
    if fmt:
        try:
            return text.format(**fmt)
        except Exception:
            return text
    return text


def set_lang(lang: str) -> None:
    if lang not in dict(LANG_OPTIONS):
        return
    try:
        settings.lang = lang  # type: ignore[attr-defined]
    except Exception:
        pass
