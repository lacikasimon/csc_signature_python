from io import BytesIO

from pyhanko.pdf_utils.reader import PdfFileReader
import pytest

from csc_signing_service.config import Settings
from csc_signing_service.errors import InvalidPDFError
from csc_signing_service.models import StampMetadata
from csc_signing_service.signing import PDFSigningService


def test_stamp_pdf_returns_readable_pdf(sample_pdf_bytes):
    service = PDFSigningService(Settings(_env_file=None), session=None)
    stamped = service.stamp_pdf(
        sample_pdf_bytes,
        StampMetadata(
            text="Reviewed",
            page=0,
            x=72,
            y=72,
            width=180,
            height=48,
            text_color="#064e3b",
            border_color="#1d4ed8",
            border_width=1.5,
        ),
    )

    assert stamped.startswith(b"%PDF-")
    assert len(stamped) > len(sample_pdf_bytes)
    reader = PdfFileReader(BytesIO(stamped))
    assert len(reader.root["/Pages"]["/Kids"]) == 1


def test_stamp_pdf_rejects_missing_template_parameter(sample_pdf_bytes):
    service = PDFSigningService(Settings(_env_file=None), session=None)

    with pytest.raises(InvalidPDFError):
        service.stamp_pdf(
            sample_pdf_bytes,
            StampMetadata(text="Missing %(unknown)s"),
        )


def test_seal_session_info_uses_seal_credential_and_token():
    settings = Settings(
        csc_service_url="http://csc.example",
        csc_oauth_token="sign-token",
        csc_seal_oauth_token="seal-token",
        csc_seal_credential_id="testing-ca/institution-seal",
        _env_file=None,
    )
    service = PDFSigningService(settings, session=None)

    session_info = service._session_info(
        credential_id=settings.seal_credential_id,
        for_seal=True,
    )

    assert session_info.service_url == "http://csc.example"
    assert session_info.credential_id == "testing-ca/institution-seal"
    assert session_info.oauth_token == "seal-token"
