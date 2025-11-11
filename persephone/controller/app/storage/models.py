"""Storage models for Persephone runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


RunStatus = str


@dataclass(slots=True)
class Run:
    """Representation of a benchmark run."""

    id: str
    gpu_type: str
    model_ref: str
    samples: int
    status: RunStatus
    latency_p50_ms: Optional[float] = None
    latency_p95_ms: Optional[float] = None
    throughput_rps: Optional[float] = None
    artifacts: Dict[str, str] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def mark_running(self) -> None:
        self.status = "running"

    def mark_succeeded(
        self,
        latency_p50_ms: float,
        latency_p95_ms: float,
        throughput_rps: float,
        artifacts: Dict[str, str],
        finished_at: datetime,
    ) -> None:
        self.status = "succeeded"
        self.latency_p50_ms = latency_p50_ms
        self.latency_p95_ms = latency_p95_ms
        self.throughput_rps = throughput_rps
        self.artifacts = artifacts
        self.finished_at = finished_at

    def mark_failed(self, error_message: str, finished_at: datetime) -> None:
        self.status = "failed"
        self.error_message = error_message
        self.finished_at = finished_at
