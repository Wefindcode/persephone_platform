"""Run management API routes."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..dependencies import get_run_service
from ..services.run_service import RunService
from ..storage.models import Run

router = APIRouter(prefix="/runs", tags=["runs"])


class RunStartRequest(BaseModel):
    """Request payload for starting a run."""

    gpu_type: str = Field(..., description="GPU identifier")
    model_ref: str = Field(..., description="Model reference or tag")
    samples: int = Field(..., gt=0, description="Number of inference samples")
    dataset_profile: Optional[str] = Field(None, description="Dataset profile identifier")


class RunArtifacts(BaseModel):
    result_json: Optional[str] = None
    gpu_csv: Optional[str] = None


class RunResponse(BaseModel):
    id: str
    status: str
    gpu_type: str
    model_ref: str
    samples: int
    latency_p50_ms: Optional[float] = None
    latency_p95_ms: Optional[float] = None
    throughput_rps: Optional[float] = None
    artifacts: RunArtifacts
    started_at: datetime
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

    @classmethod
    def from_run(cls, run: Run) -> "RunResponse":
        return cls(
            id=run.id,
            status=run.status,
            gpu_type=run.gpu_type,
            model_ref=run.model_ref,
            samples=run.samples,
            latency_p50_ms=run.latency_p50_ms,
            latency_p95_ms=run.latency_p95_ms,
            throughput_rps=run.throughput_rps,
            artifacts=RunArtifacts(
                result_json=run.artifacts.get("result_json"),
                gpu_csv=run.artifacts.get("gpu_csv"),
            ),
            started_at=run.started_at,
            finished_at=run.finished_at,
            error_message=run.error_message,
        )


@router.post("/start", status_code=status.HTTP_202_ACCEPTED, response_model=Dict[str, str])
def start_run(
    request: RunStartRequest,
    background_tasks: BackgroundTasks,
    run_service: RunService = Depends(get_run_service),
) -> Dict[str, str]:
    """Start a new benchmark run."""

    run = run_service.start_run(
        gpu_type=request.gpu_type,
        model_ref=request.model_ref,
        samples=request.samples,
        background_tasks=background_tasks,
    )
    return {"run_id": run.id}


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: str, run_service: RunService = Depends(get_run_service)) -> RunResponse:
    """Retrieve run status and metrics."""

    run = run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return RunResponse.from_run(run)
