"""Persistent storage helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .models import Task


class TaskStorage:
    """Handle reading and writing tasks from a JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        default_path = Path.home() / ".todo_app_data.json"
        self.path = path or default_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[Task]:
        if not self.path.exists():
            return []
        try:
            content = self.path.read_text(encoding="utf-8")
            if not content.strip():
                return []
            data = json.loads(content)
        except (OSError, json.JSONDecodeError):
            return []
        return [Task.from_dict(item) for item in data]

    def save(self, tasks: Iterable[Task]) -> None:
        payload = [task.to_dict() for task in tasks]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
