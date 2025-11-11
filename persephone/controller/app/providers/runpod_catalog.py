"""GPU catalog providers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import requests


MOCK_GPUS = [
    {
        "id": "l4-24gb",
        "name": "NVIDIA L4 24GB",
        "vram_gb": 24,
        "hourly_usd": 0.55,
        "regions": ["EU", "US"],
        "availability": "high",
    },
    {
        "id": "rtx4090",
        "name": "RTX 4090 24GB",
        "vram_gb": 24,
        "hourly_usd": 0.65,
        "regions": ["US"],
        "availability": "medium",
    },
    {
        "id": "l40s-48gb",
        "name": "NVIDIA L40S 48GB",
        "vram_gb": 48,
        "hourly_usd": 1.20,
        "regions": ["EU", "US"],
        "availability": "medium",
    },
    {
        "id": "a100-80gb",
        "name": "NVIDIA A100 80GB",
        "vram_gb": 80,
        "hourly_usd": 2.90,
        "regions": ["US"],
        "availability": "low",
    },
]


@dataclass
class RunpodCatalog:
    """Catalog provider pulling offers from RunPod API."""

    api_key: str
    base_url: str = "https://api.runpod.io/graphql"

    def list_gpus(self) -> List[dict]:
        """Return normalized GPU offers from RunPod."""

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "query": """
            query AvailableGPUs {
              gpuTypes {
                id
                displayName
                memoryInGb
                communityCloudHourlyCost
                regions
              }
            }
            """,
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            # TODO: log error details when logging subsystem is configured
            return []

        gpu_types = data.get("data", {}).get("gpuTypes", [])
        normalized: List[dict] = []
        for gpu in gpu_types:
            normalized.append(
                {
                    "id": gpu.get("id"),
                    "name": gpu.get("displayName"),
                    "vram_gb": gpu.get("memoryInGb"),
                    "hourly_usd": gpu.get("communityCloudHourlyCost"),
                    "regions": gpu.get("regions", []),
                    "availability": "unknown",
                }
            )
        return normalized
