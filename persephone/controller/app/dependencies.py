"""Application dependency wiring."""
from __future__ import annotations

from fastapi import Depends

from .core.config import Settings, get_settings
from .providers.runpod_orch import RunpodOrchestrator
from .services.run_service import RunService
from .storage.store import InMemoryRunStore


_store = InMemoryRunStore()


def get_run_service(settings: Settings = Depends(get_settings)) -> RunService:
    orchestrator = RunpodOrchestrator(
        api_key=settings.runpod_api_key or "",
        agent_image=settings.agent_image,
        timeout_s=settings.request_timeout_s,
    )
    return RunService(_store, orchestrator, settings.request_timeout_s)
