import logging

from fastapi.testclient import TestClient

from csc_signing_service.api import create_app
from csc_signing_service.errors import InvalidPDFError
from csc_signing_service.signing import PDFSigningService


def test_handled_error_response_includes_reason_and_request_id(
    monkeypatch,
    sample_pdf_bytes,
    caplog,
):
    def fail_stamp(self, pdf_bytes, metadata):
        raise InvalidPDFError("Stamp metadata is not valid for this PDF")

    monkeypatch.setattr(PDFSigningService, "stamp_pdf", fail_stamp)
    caplog.set_level(logging.WARNING, logger="csc_signing_service.api")

    with TestClient(create_app()) as client:
        response = client.post(
            "/v1/stamp/pdf",
            files={"pdf": ("input.pdf", sample_pdf_bytes, "application/pdf")},
            data={"metadata": "{}"},
            headers={"X-Request-ID": "test-request-id"},
        )

    assert response.status_code == 422
    assert response.headers["x-request-id"] == "test-request-id"
    assert response.json()["detail"] == {
        "code": "invalid_pdf",
        "message": "Stamp metadata is not valid for this PDF",
        "request_id": "test-request-id",
    }
    assert "request failed request_id=test-request-id" in caplog.text


def test_unhandled_error_response_includes_debug_reason_when_enabled(
    monkeypatch,
    sample_pdf_bytes,
):
    def fail_stamp(self, pdf_bytes, metadata):
        raise RuntimeError("local signer failed")

    monkeypatch.setattr(PDFSigningService, "stamp_pdf", fail_stamp)

    with TestClient(create_app(), raise_server_exceptions=False) as client:
        response = client.post(
            "/v1/stamp/pdf",
            files={"pdf": ("input.pdf", sample_pdf_bytes, "application/pdf")},
            data={"metadata": "{}"},
            headers={"X-Request-ID": "unhandled-request-id"},
        )

    assert response.status_code == 500
    assert response.headers["x-request-id"] == "unhandled-request-id"
    assert response.json()["detail"] == {
        "code": "internal_error",
        "message": "RuntimeError: local signer failed",
        "request_id": "unhandled-request-id",
    }
