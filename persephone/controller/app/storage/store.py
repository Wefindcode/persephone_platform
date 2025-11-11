"""In-memory storage implementation for runs."""
from __future__ import annotations

from threading import Lock
from typing import Dict, Iterable, Optional

from .models import Run


class InMemoryRunStore:
    """Thread-safe in-memory run storage."""

    def __init__(self) -> None:
        self._runs: Dict[str, Run] = {}
        self._lock = Lock()

    def list_runs(self) -> Iterable[Run]:
        with self._lock:
            return list(self._runs.values())

    def get(self, run_id: str) -> Optional[Run]:
        with self._lock:
            return self._runs.get(run_id)

    def save(self, run: Run) -> None:
        with self._lock:
            self._runs[run.id] = run

    def update(self, run: Run) -> None:
        self.save(run)
