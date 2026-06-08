from fastapi.testclient import TestClient

from csc_signing_service.api import create_app
from csc_signing_service.config import get_settings


def test_app_password_protects_demo_ui(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD", "secret")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            response = client.get("/")
    finally:
        get_settings.cache_clear()

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == 'Basic realm="CSC PDF Signer"'


def test_app_password_allows_basic_auth(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD", "secret")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            response = client.get("/", auth=("admin", "secret"))
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
    assert "CSC PDF SIGNER" in response.text


def test_healthz_stays_public_when_app_password_is_set(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD", "secret")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            response = client.get("/healthz")
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
