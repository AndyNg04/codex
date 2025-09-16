"""Data models used by the todo application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, Optional
import uuid


ISO_FORMAT = "%Y-%m-%d"


def _now() -> str:
    """Return an ISO timestamp without microseconds."""
    return datetime.now().replace(microsecond=0).isoformat()


@dataclass(slots=True)
class Task:
    """Representation of a todo entry."""

    title: str
    description: str = ""
    due_date: Optional[str] = None
    completed: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def mark_completed(self) -> None:
        self.completed = True
        self.updated_at = _now()

    def mark_active(self) -> None:
        self.completed = False
        self.updated_at = _now()

    def toggle_completed(self) -> None:
        self.completed = not self.completed
        self.updated_at = _now()

    def is_overdue(self) -> bool:
        if not self.due_date or self.completed:
            return False
        try:
            due = datetime.strptime(self.due_date, ISO_FORMAT).date()
        except ValueError:
            return False
        return due < date.today()

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON serialisable representation."""
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "completed": self.completed,
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create a :class:`Task` from a serialised payload."""
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            completed=data.get("completed", False),
            id=data.get("id", uuid.uuid4().hex),
            created_at=data.get("created_at", _now()),
            updated_at=data.get("updated_at", _now()),
        )

    def short_due_date(self) -> str:
        """Return the due date formatted for list display."""
        return self.due_date or "-"

    def status_label(self) -> str:
        return "已完成" if self.completed else "进行中"
