from typing import Iterable
from .models import Task, Status

def branch_progress(tasks: Iterable[Task]) -> float:
    items = list(tasks)
    if not items:
        return 0.0
    done = sum(1 for t in items if t.status == Status.DONE)
    return done / len(items)