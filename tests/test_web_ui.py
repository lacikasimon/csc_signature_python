from fastapi.testclient import TestClient

from csc_signing_service.api import create_app
from csc_signing_service.signing import PDFSigningService


def test_demo_ui_is_served():
    with TestClient(create_app()) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "id=\"pdfFile\"" in response.text
    assert "2. FUNCȚII" in response.text
    assert "id=\"functionMenuLayer\"" in response.text
    assert "id=\"functionDetailLayer\"" in response.text
    assert "id=\"backToFunctionList\"" in response.text
    assert "id=\"detailTitle\"" in response.text
    assert "id=\"sidebarActions\" class=\"sidebar-actions hidden\"" in response.text
    assert "class=\"mode-copy\"" in response.text
    assert "id=\"stampSection\"" in response.text
    assert "id=\"signatureSection\"" in response.text
    assert "id=\"placeholdersSection\"" in response.text
    assert "id=\"sealSection\"" in response.text
    assert "function-section-hidden" in response.text
    assert "id=\"stampText\"" in response.text
    assert "id=\"stampTextColor\"" in response.text
    assert "id=\"stampBorderColor\"" in response.text
    assert "id=\"visibleSignature\"" in response.text
    assert "id=\"signatureDisplayName\"" in response.text
    assert "id=\"signerRole\"" in response.text
    assert "id=\"contactEmail\"" in response.text
    assert "id=\"placeholdersToggle\"" in response.text
    assert "id=\"placeholderLayer\"" in response.text
    assert "id=\"signFirstPlaceholder\"" in response.text
    assert "Semnează prima poziție acum" in response.text
    assert "Semnături multiple" in response.text
    assert ".placement-box.placeholder[data-placeholder-id=" in response.text
    assert "id=\"sealToggle\"" in response.text
    assert "id=\"sealBox\"" in response.text
    assert "Sigiliu electronic" in response.text
    assert "CSC PDF SIGNER &amp; STAMPER DEMO" in response.text
    assert "Semnarea și ștampilarea documentelor" in response.text
    assert "id=\"clearButton\"" in response.text
    assert "id=\"resultStatus\"" in response.text
    assert "id=\"downloadResultLink\"" in response.text
    assert "function formatApiError" in response.text
    assert "Request ID:" in response.text
    assert "class=\"signature-avatar\"" in response.text
    assert "class=\"signature-watermark\"" in response.text
    assert "/v1/sign/pdf" in response.text
    assert "/v1/signature-placeholders/pdf" in response.text
    assert "/v1/seal/pdf" in response.text
    assert "/v1/stamp/pdf" in response.text
    assert "/v1/pdf/page-image" in response.text


def test_pdf_page_image_endpoint_returns_png(sample_pdf_bytes):
    with TestClient(create_app()) as client:
        response = client.post(
            "/v1/pdf/page-image",
            files={"pdf": ("input.pdf", sample_pdf_bytes, "application/pdf")},
            data={"page": "0"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG")
    assert response.headers["x-pdf-page-count"] == "1"
    assert float(response.headers["x-pdf-page-width"]) > 0
    assert float(response.headers["x-pdf-page-height"]) > 0


def test_pdf_page_image_endpoint_rejects_missing_page(sample_pdf_bytes):
    with TestClient(create_app()) as client:
        response = client.post(
            "/v1/pdf/page-image",
            files={"pdf": ("input.pdf", sample_pdf_bytes, "application/pdf")},
            data={"page": "99"},
        )

    assert response.status_code == 422


def test_signature_placeholders_endpoint_returns_pdf(sample_pdf_bytes):
    metadata = (
        '{"placeholders": ['
        '{"field_name": "Semnatar1", "box": {"page": 0, "x1": 72, "y1": 72, "x2": 190, "y2": 120}},'
        '{"field_name": "Semnatar2", "box": {"page": 0, "x1": 220, "y1": 72, "x2": 340, "y2": 120}}'
        ']}'
    )
    with TestClient(create_app()) as client:
        response = client.post(
            "/v1/signature-placeholders/pdf",
            files={"pdf": ("input.pdf", sample_pdf_bytes, "application/pdf")},
            data={"metadata": metadata},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")


def test_signature_placeholders_endpoint_can_sign_first(
    monkeypatch,
    sample_pdf_bytes,
):
    calls = {}

    def fake_add_signature_placeholders(self, pdf_bytes, metadata):
        calls["placeholder_metadata"] = metadata
        return b"%PDF-1.7\n% placeholders\n"

    async def fake_sign_existing_field_pdf(self, pdf_bytes, metadata, oauth_token=None):
        calls["sign_metadata"] = metadata
        calls["oauth_token"] = oauth_token
        return b"%PDF-1.7\n% signed first placeholder\n"

    monkeypatch.setattr(
        PDFSigningService,
        "add_signature_placeholders",
        fake_add_signature_placeholders,
    )
    monkeypatch.setattr(
        PDFSigningService,
        "sign_existing_field_pdf",
        fake_sign_existing_field_pdf,
    )

    metadata = (
        '{"sign_first": true, "sign_reason": "Aprobare", '
        '"sign_location": "București", "placeholders": ['
        '{"field_name": "Semnatar1", "box": {"page": 0, "x1": 72, "y1": 72, "x2": 190, "y2": 120}},'
        '{"field_name": "Semnatar2", "box": {"page": 0, "x1": 220, "y1": 72, "x2": 340, "y2": 120}}'
        ']}'
    )
    with TestClient(create_app()) as client:
        response = client.post(
            "/v1/signature-placeholders/pdf",
            files={"pdf": ("input.pdf", sample_pdf_bytes, "application/pdf")},
            data={"metadata": metadata},
            headers={"X-CSC-OAuth-Token": "request-token"},
        )

    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-")
    assert calls["placeholder_metadata"].sign_first is True
    assert calls["sign_metadata"].field_name == "Semnatar1"
    assert calls["sign_metadata"].reason == "Aprobare"
    assert calls["sign_metadata"].location == "București"
    assert calls["oauth_token"] == "request-token"
