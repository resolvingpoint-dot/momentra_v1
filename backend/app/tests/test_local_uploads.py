from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api import local_uploads
from app.main import app


def test_local_upload_put_and_get(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(local_uploads, "_ROOT", tmp_path)
    client = TestClient(app)

    path = "trip-attachments/demo/file.jpg"
    put = client.put(
        f"/local-uploads/{path}",
        content=b"fake-image-bytes",
        headers={"Content-Type": "image/jpeg"},
    )
    assert put.status_code == 200, put.text
    assert (tmp_path / path).is_file()

    get = client.get(f"/local-uploads/{path}")
    assert get.status_code == 200
    assert get.content == b"fake-image-bytes"
    assert get.headers["content-type"].startswith("image/jpeg")


def test_local_upload_rejects_traversal(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(local_uploads, "_ROOT", tmp_path)
    client = TestClient(app)
    bad = client.put(
        "/local-uploads/../secrets.txt",
        content=b"nope",
        headers={"Content-Type": "text/plain"},
    )
    # Starlette may normalize `../` away from the route (404) before our guard runs.
    assert bad.status_code in (400, 404)
    assert not (tmp_path / "secrets.txt").exists()
