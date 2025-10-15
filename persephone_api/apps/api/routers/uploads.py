from __future__ import annotations

import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session

from ..deps import get_session
from ..schemas.uploads import UploadResponse
from ..services import s3
from ..services.runs import RunService
from ..services.security import get_current_user

router = APIRouter(tags=["uploads"])

MAX_UPLOAD_SIZE = 500 * 1024 * 1024


@router.post("/upload", response_model=UploadResponse)
async def upload_artifact(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    _: dict = Depends(get_current_user),
) -> UploadResponse:
    # TODO: plug a real rate limiter here
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
    run_id = str(uuid4())
    artifact_key = f"{run_id}/input/{file.filename}"
    s3.put_object_from_upload(artifact_key, file)
    run_service = RunService(db)
    run = run_service.create_uploaded(artifact_key, run_id=run_id)
    return UploadResponse(runId=run.id)
