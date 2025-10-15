from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..deps import get_session
from ..schemas.runs import RunResponse
from ..services.runs import RunService
from ..services.security import get_current_user

router = APIRouter(prefix="/runs", tags=["runs"])


def _to_response(service_run) -> RunResponse:
    return RunResponse(
        runId=service_run.id,
        phase=service_run.phase,
        progress=service_run.progress,
        artifactKey=service_run.artifact_key,
        gpuId=service_run.gpu_id,
        serviceUrl=service_run.service_url,
        createdAt=service_run.created_at,
        updatedAt=service_run.updated_at,
    )


@router.get("/{run_id}", response_model=RunResponse)
def get_run(
    run_id: str,
    db: Session = Depends(get_session),
    _: dict = Depends(get_current_user),
) -> RunResponse:
    service = RunService(db)
    try:
        UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run id")
    run = service.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return _to_response(run)


@router.post("/{run_id}/cancel", response_model=RunResponse)
def cancel_run(
    run_id: str,
    db: Session = Depends(get_session),
    _: dict = Depends(get_current_user),
) -> RunResponse:
    service = RunService(db)
    try:
        UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run id")
    run = service.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.phase in {"canceled", "failed"}:
        raise HTTPException(status_code=400, detail="Cannot cancel run")
    run = service.cancel(run)
    return _to_response(run)
