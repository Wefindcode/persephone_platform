"""RunPod orchestrator abstraction."""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Dict

import requests


@dataclass
class RunpodOrchestrator:
    """Facade around the RunPod Dedicated API."""

    api_key: str
    agent_image: str
    timeout_s: int
    base_url: str = "https://api.runpod.io/v2"

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def create_pod(self, gpu_type: str, env: Dict[str, str]) -> str:
        """Create a pod and return its identifier.

        The implementation is stubbed for MVP while the RunPod contract is finalized.
        """

        if not self.api_key:
            # Without an API key we cannot reach RunPod; return a generated identifier for mocks.
            return f"mock-pod-{uuid.uuid4()}"

        payload = {
            "name": "persephone-agent",
            "imageName": self.agent_image,
            "gpuTypeId": gpu_type,
            "cloudType": "ALL",  # TODO: confirm cloud type
            "env": env,
            "containerDiskInGb": 20,
        }
        try:
            response = requests.post(
                f"{self.base_url}/pods",
                headers=self._headers(),
                data=json.dumps(payload),
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("id", f"mock-pod-{uuid.uuid4()}")
        except requests.RequestException:
            return f"mock-pod-{uuid.uuid4()}"

    def exec(self, pod_id: str, command: list[str]) -> None:
        """Execute a command inside the pod.

        For the MVP we assume success and rely on wait_and_fetch to surface failures.
        """

        if not self.api_key:
            return
        payload = {"podId": pod_id, "command": command}
        try:
            response = requests.post(
                f"{self.base_url}/pods/{pod_id}/exec",
                headers=self._headers(),
                data=json.dumps(payload),
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            # TODO: log error for observability
            return

    def wait_and_fetch(self, pod_id: str, timeout_s: int | None = None) -> Dict[str, str]:
        """Wait for completion and fetch artifacts from the pod.

        Returns a mapping of artifact name to its textual contents.
        """

        timeout_s = timeout_s or self.timeout_s
        if not self.api_key:
            # Return mock artifacts suitable for local testing.
            time.sleep(1)
            result = {
                "result.json": json.dumps(
                    {
                        "samples": 8,
                        "latency_p50_ms": 25.0,
                        "latency_p95_ms": 35.0,
                        "throughput_rps": 40.0,
                        "note": "mocked RunPod execution",
                    }
                ),
                "gpu_timeseries.csv": "t,gpu_util,mem_util,vram_mb,power_w,temp_c\n"
                "0,50,40,1800,120,60\n",
            }
            return result

        # TODO: poll RunPod status until completion and retrieve files via storage API.
        # Placeholder polling loop simulating completion.
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            time.sleep(5)
            break
        # TODO: download artifacts from RunPod once available.
        return {
            "result.json": json.dumps(
                {
                    "samples": 0,
                    "latency_p50_ms": 0,
                    "latency_p95_ms": 0,
                    "throughput_rps": 0,
                    "note": "TODO: fetch from RunPod",
                }
            ),
            "gpu_timeseries.csv": "",
        }

    def stop_pod(self, pod_id: str) -> None:
        """Terminate the pod."""

        if not self.api_key:
            return
        try:
            response = requests.delete(
                f"{self.base_url}/pods/{pod_id}",
                headers=self._headers(),
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            # TODO: log error for observability
            return
