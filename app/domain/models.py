from __future__ import annotations
from typing import Optional
from datetime import datetime
from enum import Enum, IntEnum
from sqlmodel import SQLModel, Field


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(IntEnum):
    HIGH = 1
    MEDIUM = 3
    LOW = 5


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(default=None, index=True, foreign_key="task.id")
    title: str = Field(index=True)
    description: Optional[str] = None
    status: str = Field(default=Status.TODO.value, index=True)
    priority: Optional[int] = Field(default=Priority.MEDIUM, index=True)
    due_at: Optional[datetime] = Field(default=None, index=True)

    category: Optional[str] = Field(default=None, index=True)

    order_index: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
