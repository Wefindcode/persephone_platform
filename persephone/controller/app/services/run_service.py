"""Run orchestration service."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Dict
from uuid import uuid4

from fastapi import BackgroundTasks

from ..providers.runpod_orch import RunpodOrchestrator
from ..storage.models import Run
from ..storage.store import InMemoryRunStore

logger = logging.getLogger(__name__)


class RunService:
    """Business logic for managing benchmark runs."""

    def __init__(
        self,
        store: InMemoryRunStore,
        orchestrator: RunpodOrchestrator,
        request_timeout_s: int,
    ) -> None:
        self._store = store
        self._orchestrator = orchestrator
        self._request_timeout_s = request_timeout_s

    def start_run(
        self,
        gpu_type: str,
        model_ref: str,
        samples: int,
        background_tasks: BackgroundTasks,
    ) -> Run:
        run = Run(
            id=str(uuid4()),
            gpu_type=gpu_type,
            model_ref=model_ref,
            samples=samples,
            status="pending",
        )
        self._store.save(run)
        background_tasks.add_task(self._execute_run, run.id)
        return run

    def get_run(self, run_id: str) -> Run | None:
        return self._store.get(run_id)

    def _execute_run(self, run_id: str) -> None:
        run = self._store.get(run_id)
        if not run:
            logger.error("Run %s not found in store", run_id)
            return

        run.mark_running()
        self._store.update(run)

        pod_id = None
        try:
            env = {"MODEL_REF": run.model_ref, "SAMPLES": str(run.samples)}
            pod_id = self._orchestrator.create_pod(run.gpu_type, env)
            logger.info("Created pod %s for run %s", pod_id, run_id)

            self._orchestrator.exec(pod_id, ["python", "agent.py", "run"])
            artifacts = self._orchestrator.wait_and_fetch(pod_id, self._request_timeout_s)
            parsed = self._parse_artifacts(artifacts)
            run.mark_succeeded(
                latency_p50_ms=parsed["result"].get("latency_p50_ms", 0.0),
                latency_p95_ms=parsed["result"].get("latency_p95_ms", 0.0),
                throughput_rps=parsed["result"].get("throughput_rps", 0.0),
                artifacts={
                    "result_json": parsed["artifacts"].get("result.json", ""),
                    "gpu_csv": parsed["artifacts"].get("gpu_timeseries.csv", ""),
                },
                finished_at=datetime.utcnow(),
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Run %s failed: %s", run_id, exc)
            run.mark_failed(str(exc), datetime.utcnow())
        finally:
            if pod_id:
                try:
                    self._orchestrator.stop_pod(pod_id)
                except Exception:  # pylint: disable=broad-except
                    logger.exception("Failed to stop pod %s", pod_id)
            self._store.update(run)

    @staticmethod
    def _parse_artifacts(artifacts: Dict[str, str]) -> Dict[str, Dict[str, str | float]]:
        result_blob = artifacts.get("result.json", "{}")
        try:
            result_data = json.loads(result_blob)
        except json.JSONDecodeError:
            result_data = {}

        return {"result": result_data, "artifacts": artifacts}
