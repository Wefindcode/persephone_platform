from __future__ import annotations

import io


def test_upload_creates_run(client):
    login_resp = client.post(
        "/auth/login",
        json={"email": "admin@persephone.local", "password": "admin"},
    )
    cookie = login_resp.cookies.get("psphn_session")
    files = {"file": ("example.txt", io.BytesIO(b"hello"), "text/plain")}
    response = client.post("/upload", files=files, cookies={"psphn_session": cookie})
    assert response.status_code == 200
    data = response.json()
    assert "runId" in data
