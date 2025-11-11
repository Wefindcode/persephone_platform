"""Persephone GPU agent entrypoint."""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from threading import Event, Thread

from .gpu_metrics import collect_gpu_metrics
from .runner import run_probe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


WORKSPACE = Path("/workspace")
RESULT_JSON = WORKSPACE / "result.json"
GPU_CSV = WORKSPACE / "gpu_timeseries.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Persephone agent controller")
    subparsers = parser.add_subparsers(dest="command")
    run_parser = subparsers.add_parser("run", help="Execute benchmark run")
    run_parser.add_argument("--model", dest="model_ref", default=os.getenv("MODEL_REF", "mock-v0"))
    run_parser.add_argument("--samples", dest="samples", type=int, default=int(os.getenv("SAMPLES", "1")))

    args = parser.parse_args()

    if args.command == "run":
        execute_run(args.model_ref, args.samples)
    else:
        parser.print_help()


def execute_run(model_ref: str, samples: int) -> None:
    logger.info("Starting agent run model=%s samples=%s", model_ref, samples)
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    stop_event = Event()
    metrics_thread = Thread(
        target=collect_gpu_metrics,
        kwargs={
            "output_path": GPU_CSV,
            "interval_s": 0.5,
            "duration_s": None,
            "stop_event": stop_event,
        },
        daemon=True,
    )
    metrics_thread.start()

    try:
        result = run_probe(model_ref, samples)
    finally:
        stop_event.set()
        metrics_thread.join(timeout=5)

    with open(RESULT_JSON, "w", encoding="utf-8") as result_file:
        json.dump(result, result_file, indent=2)
    logger.info("Run complete; results stored at %s", RESULT_JSON)


if __name__ == "__main__":
    main()
