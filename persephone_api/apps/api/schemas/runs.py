from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RunResponse(BaseModel):
    runId: UUID
    phase: str
    progress: Optional[int]
    artifactKey: str
    gpuId: Optional[str]
    serviceUrl: Optional[str]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
