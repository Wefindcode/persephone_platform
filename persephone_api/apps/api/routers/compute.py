from __future__ import annotations

from fastapi import APIRouter

from ..schemas.compute import GPUInfo, GPUListResponse
from ..services.runpod import list_gpus

router = APIRouter(prefix="/compute", tags=["compute"])


@router.get("/gpus", response_model=GPUListResponse)
def get_gpus() -> GPUListResponse:
    gpus = [GPUInfo(**gpu) for gpu in list_gpus()]
    return GPUListResponse(gpus=gpus)
