from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from ..deps import get_session, session_scope
from ..services.runs import RunService
from ..services.security import get_current_user

router = APIRouter(prefix="/deploy", tags=["deploy"])


def _finish_deploy(run_id: str) -> None:
    with session_scope() as session:
        service = RunService(session)
        run = service.get(run_id)
        if run is None:
            return
        service.update_phase(
            run,
            "running",
            service_url=f"http://inference.local/{run_id}",
        )


@router.post("/start")
def start_deploy(
    runId: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
    _: dict = Depends(get_current_user),
) -> dict:
    service = RunService(db)
    try:
        UUID(runId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run id")
    run = service.get(runId)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    service.update_phase(run, "deploying")
    background_tasks.add_task(_finish_deploy, runId)
    return {"runId": runId, "phase": "deploying"}
