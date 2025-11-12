from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlmodel import Session

from ..deps import get_session, session_scope
from ..services.runs import RunService
from ..services.security import get_current_user

router = APIRouter(prefix="/prepare", tags=["prepare"])


def _finish_prepare(run_id: str, gpu_id: str) -> None:
    with session_scope() as session:
        service = RunService(session)
        run = service.get(run_id)
        if run is None:
            return
        run.progress = 100
        service.update_phase(run, "prepared", gpu_id=gpu_id)


@router.post("/start")
def start_prepare(
    runId: str,
    gpuId: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
    _: dict = Depends(get_current_user),
) -> dict:
    service = RunService(db)
    try:
        UUID(runId)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid run id")
    run = service.get(runId)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    run.progress = 10
    service.update_phase(run, "preparing", gpu_id=gpuId)
    background_tasks.add_task(_finish_prepare, runId, gpuId)
    return {"runId": runId, "phase": "preparing"}
