"""GPU metrics collection using NVML."""
from __future__ import annotations

import csv
import logging
import time
from pathlib import Path
from threading import Event
from typing import Optional

logger = logging.getLogger(__name__)


def collect_gpu_metrics(
    output_path: str | Path,
    interval_s: float = 1.0,
    duration_s: Optional[float] = 20.0,
    stop_event: Optional[Event] = None,
) -> None:
    """Capture GPU telemetry via NVML and write it to CSV."""

    try:
        import pynvml  # type: ignore
    except ImportError:
        logger.warning("pynvml not available; writing empty metrics file")
        _write_header_only(output_path)
        return

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["t", "gpu_util", "mem_util", "vram_mb", "power_w", "temp_c"])

        pynvml.nvmlInit()
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            start = time.time()
            while True:
                now = time.time()
                if stop_event and stop_event.is_set():
                    break
                if duration_s is not None and now - start > duration_s:
                    break

                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                power = _safe_nvml_call(pynvml.nvmlDeviceGetPowerUsage, handle)
                temp = _safe_nvml_call(pynvml.nvmlDeviceGetTemperature, handle, pynvml.NVML_TEMPERATURE_GPU)

                writer.writerow(
                    [
                        round(now - start, 2),
                        getattr(util, "gpu", 0),
                        getattr(util, "memory", 0),
                        round(mem_info.used / (1024 * 1024), 2),
                        round(power / 1000 if power is not None else 0, 2),
                        temp if temp is not None else 0,
                    ]
                )
                csvfile.flush()
                time.sleep(interval_s)
        finally:
            pynvml.nvmlShutdown()


def _write_header_only(output_path: str | Path) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["t", "gpu_util", "mem_util", "vram_mb", "power_w", "temp_c"])


def _safe_nvml_call(func, *args):  # type: ignore[no-untyped-def]
    try:
        return func(*args)
    except Exception:  # pylint: disable=broad-except
        logger.debug("NVML call %s failed", func.__name__)
        return None
