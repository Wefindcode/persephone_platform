from __future__ import annotations

import io


def _login(client):
    resp = client.post(
        "/auth/login",
        json={"email": "admin@persephone.local", "password": "admin"},
    )
    return resp.cookies.get("psphn_session")


def _create_run(client, cookie: str) -> str:
    files = {"file": ("example.txt", io.BytesIO(b"hello"), "text/plain")}
    response = client.post("/upload", files=files, cookies={"psphn_session": cookie})
    return response.json()["runId"]


def test_prepare_and_deploy_flow(client):
    cookie = _login(client)
    run_id = _create_run(client, cookie)

    prepare_resp = client.post(
        "/prepare/start",
        params={"runId": run_id, "gpuId": "a100"},
        cookies={"psphn_session": cookie},
    )
    assert prepare_resp.status_code == 200

    run_resp = client.get(f"/runs/{run_id}", cookies={"psphn_session": cookie})
    assert run_resp.status_code == 200
    assert run_resp.json()["phase"] in {"prepared", "preparing"}

    deploy_resp = client.post(
        "/deploy/start",
        params={"runId": run_id},
        cookies={"psphn_session": cookie},
    )
    assert deploy_resp.status_code == 200

    run_resp = client.get(f"/runs/{run_id}", cookies={"psphn_session": cookie})
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert run_data["phase"] == "running"
    assert run_data["serviceUrl"].endswith(run_id)
