"""Flask based todo list web application."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable, List, Optional

from flask import Flask, Response, flash, redirect, render_template, request, url_for

from .models import ISO_FORMAT, Task
from .storage import TaskStorage


def _timestamp() -> str:
    """Return the current timestamp without microseconds."""
    return datetime.now().replace(microsecond=0).isoformat()


def create_app(storage: Optional[TaskStorage] = None) -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = os.environ.get("TODO_APP_SECRET_KEY", "todo-app-secret")
    task_storage = storage or TaskStorage()

    def load_tasks() -> List[Task]:
        return list(task_storage.load())

    def save_tasks(tasks: Iterable[Task]) -> None:
        task_storage.save(tasks)

    def find_task(tasks: List[Task], task_id: str) -> Task | None:
        return next((task for task in tasks if task.id == task_id), None)

    def validate_due_date(raw_value: str) -> str | None:
        raw_value = (raw_value or "").strip()
        if not raw_value:
            return None
        datetime.strptime(raw_value, ISO_FORMAT)
        return raw_value

    def apply_completion(task: Task, completed: bool) -> None:
        task.completed = completed
        task.updated_at = _timestamp()

    def redirect_to_index(**extra: str) -> Response:
        params: dict[str, str] = {}
        query = request.form.get("q", "").strip()
        if query:
            params["q"] = query
        status_value = request.form.get("status", "").strip()
        if status_value in {"all", "active", "completed"} and (
            status_value != "all" or "status" in request.form
        ):
            params["status"] = status_value
        params.update(extra)
        return redirect(url_for("index", **params))

    @app.context_processor
    def inject_globals() -> dict[str, object]:
        return {"ISO_FORMAT": ISO_FORMAT}

    @app.route("/", methods=["GET"])
    def index() -> str:
        tasks = load_tasks()
        search = request.args.get("q", "").strip()
        status = request.args.get("status", "all")
        edit_id = request.args.get("edit")

        filtered: List[Task] = tasks
        if search:
            keyword = search.lower()
            filtered = [
                task
                for task in filtered
                if keyword in task.title.lower() or keyword in task.description.lower()
            ]

        if status == "active":
            filtered = [task for task in filtered if not task.completed]
        elif status == "completed":
            filtered = [task for task in filtered if task.completed]

        def sort_key(task: Task) -> tuple[bool, str, str]:
            due_key = task.due_date or "9999-12-31"
            return (task.completed, due_key, task.updated_at)

        filtered = sorted(filtered, key=sort_key)

        edit_task = find_task(tasks, edit_id) if edit_id else None

        return render_template(
            "index.html",
            tasks=filtered,
            search=search,
            status=status,
            edit_task=edit_task,
        )

    @app.post("/tasks")
    def create_task() -> str:
        tasks = load_tasks()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_raw = request.form.get("due_date", "").strip()

        if not title:
            flash("任务标题不能为空。", "error")
            return redirect_to_index()

        try:
            due_date = validate_due_date(due_raw)
        except ValueError:
            flash("截止日期格式必须为 YYYY-MM-DD。", "error")
            return redirect_to_index()

        task = Task(title=title, description=description, due_date=due_date)
        tasks.append(task)
        save_tasks(tasks)
        flash("任务已创建。", "success")
        return redirect_to_index()

    @app.post("/tasks/<task_id>/status")
    def update_status(task_id: str) -> str:
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if not task:
            flash("未找到对应的任务。", "error")
            return redirect_to_index()

        state = request.form.get("state")
        if state not in {"completed", "active"}:
            flash("未知的任务状态。", "error")
            return redirect_to_index()

        apply_completion(task, state == "completed")
        save_tasks(tasks)
        flash("任务状态已更新。", "success")
        return redirect_to_index()

    @app.post("/tasks/<task_id>/update")
    def update_task(task_id: str) -> str:
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if not task:
            flash("未找到对应的任务。", "error")
            return redirect_to_index()

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_raw = request.form.get("due_date", "").strip()
        completed = request.form.get("completed") == "1"

        if not title:
            flash("任务标题不能为空。", "error")
            return redirect_to_index(edit=task_id)

        try:
            due_date = validate_due_date(due_raw)
        except ValueError:
            flash("截止日期格式必须为 YYYY-MM-DD。", "error")
            return redirect_to_index(edit=task_id)

        task.title = title
        task.description = description
        task.due_date = due_date
        apply_completion(task, completed)
        save_tasks(tasks)
        flash("任务已更新。", "success")
        return redirect_to_index()

    @app.post("/tasks/<task_id>/delete")
    def delete_task(task_id: str) -> str:
        tasks = load_tasks()
        remaining = [task for task in tasks if task.id != task_id]
        if len(remaining) == len(tasks):
            flash("未找到需要删除的任务。", "error")
            return redirect_to_index()

        save_tasks(remaining)
        flash("任务已删除。", "success")
        return redirect_to_index()

    return app


def main() -> None:
    """Start a development server for the todo application."""

    app = create_app()
    host = os.environ.get("TODO_APP_HOST", "127.0.0.1")
    port = int(os.environ.get("TODO_APP_PORT", "5000"))
    debug = os.environ.get("TODO_APP_DEBUG") == "1"
    app.run(host=host, port=port, debug=debug)


__all__ = ["create_app", "main"]
