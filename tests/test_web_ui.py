from fastapi.testclient import TestClient

from csc_signing_service.api import create_app


def test_demo_ui_is_served():
    with TestClient(create_app()) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "id=\"pdfFile\"" in response.text
    assert "id=\"stampText\"" in response.text
    assert "id=\"stampTextColor\"" in response.text
    assert "id=\"stampBorderColor\"" in response.text
    assert "id=\"visibleSignature\"" in response.text
    assert "CSC PDF SIGNER &amp; STAMPER DEMO" in response.text
    assert "Semnarea și ștampilarea documentelor" in response.text
    assert "id=\"clearButton\"" in response.text
    assert "id=\"resultStatus\"" in response.text
    assert "id=\"downloadResultLink\"" in response.text
    assert "class=\"sig-script\"" in response.text
    assert "/v1/sign/pdf" in response.text
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
