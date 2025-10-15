from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Configure environment for testing before importing the app
TMP_DIR = Path(__file__).parent / "tmp"
TMP_DIR.mkdir(exist_ok=True)
TEST_DB_PATH = TMP_DIR / "test.db"
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ.setdefault("DB_URL", f"sqlite:///{TEST_DB_PATH}")
os.environ.setdefault("S3_ENDPOINT", "http://localhost:9000")
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("S3_ACCESS_KEY", "minioadmin")
os.environ.setdefault("S3_SECRET_KEY", "minioadmin")
os.environ.setdefault("AUTH_SECRET", "test-secret")
os.environ.setdefault("WEBHOOK_SECRET", "webhook-secret")
os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://localhost:3000")

from apps.api.main import app  # noqa: E402
from apps.api.deps import init_db  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_db() -> Generator[None, None, None]:
    init_db()
    yield


@pytest.fixture(scope="function", autouse=True)
def clean_db() -> Generator[None, None, None]:
    # For sqlite we can simply recreate the schema for each test
    from sqlmodel import SQLModel, create_engine

    engine = create_engine(os.environ["DB_URL"], echo=False)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    init_db()
    yield


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    monkeypatch.setattr("apps.api.services.s3.put_object_from_upload", lambda key, file: None)
    with TestClient(app) as test_client:
        yield test_client
