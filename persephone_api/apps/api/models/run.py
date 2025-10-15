from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, SQLModel


def _uuid_str() -> str:
    return str(uuid4())


class Run(SQLModel, table=True):
    __tablename__ = "runs"

    id: str = Field(default_factory=_uuid_str, primary_key=True, index=True)
    phase: str = Field(index=True)
    artifact_key: str
    gpu_id: Optional[str] = None
    service_url: Optional[str] = None
    progress: Optional[int] = Field(default=0, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
