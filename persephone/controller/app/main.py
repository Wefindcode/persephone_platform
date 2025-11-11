"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import Depends, FastAPI

from .api import api_compute, api_runs
from .core.auth import require_api_key
from .core.config import get_settings

logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Persephone Controller",
        version="0.1.0",
        description="MVP controller for orchestrating GPU benchmark runs.",
    )

    dependency = [Depends(require_api_key)]

    app.include_router(api_compute.router, dependencies=dependency)
    app.include_router(api_runs.router, dependencies=dependency)

    @app.get("/health", tags=["system"], summary="Health check")
    def health_check() -> dict:
        return {"status": "ok", "catalog_mode": settings.catalog_mode}

    return app


app = create_app()
