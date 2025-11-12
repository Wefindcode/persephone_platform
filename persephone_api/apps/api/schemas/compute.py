from __future__ import annotations

from typing import List

from pydantic import BaseModel


class GPUInfo(BaseModel):
    id: str
    name: str
    vendor: str
    vram_gb: int
    price_secure: float
    price_community: float
    spot_secure: float
    spot_community: float
    max_gpu: int
    min_pod_gpu: int


class GPUListResponse(BaseModel):
    gpus: List[GPUInfo]
