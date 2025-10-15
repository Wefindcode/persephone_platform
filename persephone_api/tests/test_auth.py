from __future__ import annotations


def test_auth_flow(client):
    login_resp = client.post(
        "/auth/login",
        json={"email": "admin@persephone.local", "password": "admin"},
    )
    assert login_resp.status_code == 200
    cookie = login_resp.cookies.get("psphn_session")
    assert cookie is not None

    me_resp = client.get("/auth/me", cookies={"psphn_session": cookie})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "admin@persephone.local"

    logout_resp = client.post("/auth/logout", cookies={"psphn_session": cookie})
    assert logout_resp.status_code == 200
    assert logout_resp.json()["ok"] is True
