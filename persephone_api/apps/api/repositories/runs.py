from __future__ import annotations

from typing import Optional

from sqlmodel import Session

from ..models.run import Run


class RunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, run: Run) -> Run:
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def get(self, run_id: str) -> Optional[Run]:
        return self.session.get(Run, run_id)

    def save(self, run: Run) -> Run:
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run
