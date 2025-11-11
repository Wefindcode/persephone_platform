"""Compute related API routes."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from ..core.config import Settings, get_settings
from ..providers.runpod_catalog import MOCK_GPUS, RunpodCatalog

router = APIRouter(prefix="/compute", tags=["compute"])


@router.get("/gpus", response_model=List[dict])
def list_gpus(settings: Settings = Depends(get_settings)) -> List[dict]:
    """Return available GPU offerings."""

    if settings.catalog_mode == "mock":
        return MOCK_GPUS

    if not settings.runpod_api_key:
        return []

    catalog = RunpodCatalog(api_key=settings.runpod_api_key)
    return catalog.list_gpus()
