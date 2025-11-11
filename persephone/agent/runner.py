"""Mock inference runner for the Persephone agent."""
from __future__ import annotations

import math
import time
from typing import Dict, List


def run_probe(model_ref: str, samples: int) -> Dict[str, float | int | str]:
    """Execute a mock inference workload and collect latency metrics."""

    if samples <= 0:
        raise ValueError("samples must be positive")

    latencies_ms: List[float] = []
    start_time = time.perf_counter()

    for _ in range(samples):
        iter_start = time.perf_counter()
        time.sleep(0.02)
        latency_ms = (time.perf_counter() - iter_start) * 1000
        latencies_ms.append(latency_ms)

    duration_s = max(time.perf_counter() - start_time, 1e-6)

    p50 = _percentile(latencies_ms, 0.50)
    p95 = _percentile(latencies_ms, 0.95)
    throughput = samples / duration_s

    return {
        "samples": samples,
        "latency_p50_ms": round(p50, 3),
        "latency_p95_ms": round(p95, 3),
        "throughput_rps": round(throughput, 3),
        "note": f"mock model {model_ref}; replace with vLLM later",
    }


def _percentile(values: List[float], percentile: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * percentile
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return d0 + d1
