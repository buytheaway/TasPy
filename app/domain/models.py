from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Status:
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="tasks.id", index=True)

    title: str = Field(index=True)
    description: Optional[str] = None

    status: str = Field(default=Status.TODO, index=True)
    priority: int = Field(default=3, index=True)

    due_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    order_index: int = Field(default=0, index=True)
    path_cache: Optional[str] = None