from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Session

from ..models.run import Run
from ..repositories.runs import RunRepository


class RunService:
    def __init__(self, session: Session) -> None:
        self.repo = RunRepository(session)

    def create_uploaded(self, artifact_key: str, run_id: Optional[str] = None) -> Run:
        data = {"phase": "uploaded", "artifact_key": artifact_key}
        if run_id is not None:
            data["id"] = run_id
        run = Run(**data)
        now = datetime.utcnow()
        run.created_at = now
        run.updated_at = now
        return self.repo.create(run)

    def get(self, run_id: str) -> Optional[Run]:
        return self.repo.get(run_id)

    def update_phase(
        self, run: Run, phase: str, *, gpu_id: Optional[str] = None, service_url: Optional[str] = None
    ) -> Run:
        run.phase = phase
        if gpu_id is not None:
            run.gpu_id = gpu_id
        if service_url is not None:
            run.service_url = service_url
        run.updated_at = datetime.utcnow()
        return self.repo.save(run)

    def cancel(self, run: Run) -> Run:
        run.phase = "canceled"
        run.updated_at = datetime.utcnow()
        return self.repo.save(run)
