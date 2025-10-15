from __future__ import annotations

from typing import Any, Dict, List


def list_gpus() -> List[Dict[str, Any]]:
    return [
        {
            "id": "mi300x",
            "name": "AMD MI300X",
            "vendor": "AMD",
            "vram_gb": 192,
            "price_secure": 8.5,
            "price_community": 6.0,
            "spot_secure": 7.0,
            "spot_community": 5.0,
            "max_gpu": 8,
            "min_pod_gpu": 1,
        },
        {
            "id": "a100-80gb",
            "name": "NVIDIA A100 80GB",
            "vendor": "NVIDIA",
            "vram_gb": 80,
            "price_secure": 6.5,
            "price_community": 5.2,
            "spot_secure": 4.0,
            "spot_community": 3.5,
            "max_gpu": 8,
            "min_pod_gpu": 1,
        },
        {
            "id": "l4",
            "name": "NVIDIA L4",
            "vendor": "NVIDIA",
            "vram_gb": 24,
            "price_secure": 1.2,
            "price_community": 0.9,
            "spot_secure": 0.8,
            "spot_community": 0.6,
            "max_gpu": 4,
            "min_pod_gpu": 1,
        },
        {
            "id": "t4",
            "name": "NVIDIA T4",
            "vendor": "NVIDIA",
            "vram_gb": 16,
            "price_secure": 0.7,
            "price_community": 0.5,
            "spot_secure": 0.4,
            "spot_community": 0.3,
            "max_gpu": 4,
            "min_pod_gpu": 1,
        },
    ]
