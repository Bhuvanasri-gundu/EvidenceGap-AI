"""Background task manager for asynchronous research pipeline jobs."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, Optional

logger = logging.getLogger(__name__)


class TaskManager:
    """Manages long-running async background tasks for research pipelines."""

    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._task_metadata: Dict[str, Dict[str, Any]] = {}

    def spawn(
        self,
        task_id: str,
        coro_func: Callable[..., Coroutine[Any, Any, None]],
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task:
        """Spawn a background task without blocking."""
        if task_id in self._active_tasks and not self._active_tasks[task_id].done():
            logger.warning("Task %s is already running", task_id)
            return self._active_tasks[task_id]

        async def _wrapper():
            logger.info("Starting background task %s", task_id)
            try:
                await coro_func(*args, **kwargs)
                logger.info("Successfully finished background task %s", task_id)
            except asyncio.CancelledError:
                logger.warning("Background task %s was cancelled", task_id)
            except Exception as exc:
                logger.exception("Background task %s failed with exception: %s", task_id, exc)
            finally:
                if task_id in self._active_tasks:
                    del self._active_tasks[task_id]

        task = asyncio.create_task(_wrapper(), name=f"task_{task_id}")
        self._active_tasks[task_id] = task
        self._task_metadata[task_id] = {
            "status": "running",
            "name": coro_func.__name__,
        }
        return task

    def is_running(self, task_id: str) -> bool:
        task = self._active_tasks.get(task_id)
        return task is not None and not task.done()

    def cancel(self, task_id: str) -> bool:
        task = self._active_tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            return True
        return False


# Global singleton instance
task_manager = TaskManager()
