from io import BytesIO

from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import fields
import pytest

from csc_signing_service.config import Settings
from csc_signing_service.errors import InvalidPDFError
from csc_signing_service.models import (
    SigningMetadata,
    SignatureBox,
    SignaturePlaceholder,
    SignaturePlaceholdersMetadata,
    StampMetadata,
)
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


def test_add_signature_placeholders_creates_empty_signature_fields(sample_pdf_bytes):
    service = PDFSigningService(Settings(_env_file=None), session=None)
    output = service.add_signature_placeholders(
        sample_pdf_bytes,
        SignaturePlaceholdersMetadata(
            placeholders=[
                SignaturePlaceholder(
                    field_name="Semnatar1",
                    box=SignatureBox(page=0, x1=72, y1=72, x2=190, y2=120),
                ),
                SignaturePlaceholder(
                    field_name="Semnatar2",
                    box=SignatureBox(page=0, x1=220, y1=72, x2=340, y2=120),
                ),
            ]
        ),
    )

    assert output.startswith(b"%PDF-")
    reader = PdfFileReader(BytesIO(output))
    field_names = [
        str(field_name)
        for field_name, value, _ in fields.enumerate_sig_fields(reader)
        if value is None
    ]

    assert field_names == ["Semnatar1", "Semnatar2"]


@pytest.mark.asyncio
async def test_local_demo_signing_replaces_csc_for_demo(sample_pdf_bytes):
    service = PDFSigningService(
        Settings(local_signing_enabled=True, _env_file=None),
        session=None,
    )

    output = await service.sign_pdf(sample_pdf_bytes, SigningMetadata())

    assert output.startswith(b"%PDF-")
    assert len(output) > len(sample_pdf_bytes)
    reader = PdfFileReader(BytesIO(output))
    signed_fields = [
        field_name
        for field_name, value, _ in fields.enumerate_sig_fields(reader)
        if value is not None
    ]
    assert signed_fields == ["Signature1"]


def test_add_signature_placeholders_rejects_invalid_pdf():
    service = PDFSigningService(Settings(_env_file=None), session=None)

    with pytest.raises(InvalidPDFError):
        service.add_signature_placeholders(
            b"not a pdf",
            SignaturePlaceholdersMetadata(),
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
