from __future__ import annotations

from typing import Optional

import boto3
from fastapi import UploadFile

from ..settings import settings

_s3_client: Optional[boto3.client] = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
    return _s3_client


def put_object_from_upload(key: str, file: UploadFile) -> None:
    client = get_s3_client()
    file.file.seek(0)
    client.upload_fileobj(file.file, settings.s3_bucket, key)


def generate_presigned_url(key: str, expires: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires,
    )
