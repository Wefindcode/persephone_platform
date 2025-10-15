from __future__ import annotations

import hashlib
import hmac
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import Session

from ..deps import get_session
from ..services.runs import RunService
from ..settings import settings

router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.post("/webhook")
async def webhook(
    request: Request,
    x_signature: str = Header(..., alias="X-Signature"),
    db: Session = Depends(get_session),
) -> Dict[str, Any]:
    raw_body = await request.body()
    expected = hmac.new(settings.webhook_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    payload = await request.json()
    run_id = payload.get("run_id")
    phase = payload.get("phase")
    if not run_id or not phase:
        raise HTTPException(status_code=400, detail="Invalid payload")
    try:
        UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run id")
    service = RunService(db)
    run = service.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    run.progress = payload.get("progress", run.progress)
    service.update_phase(run, phase, service_url=payload.get("service_url"))
    return {"ok": True}
