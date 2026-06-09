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
from csc_signing_service.signing import ModernSignatureStamp, PDFSigningService


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


@pytest.mark.asyncio
async def test_visible_signature_uses_modern_appearance(sample_pdf_bytes):
    service = PDFSigningService(
        Settings(local_signing_enabled=True, _env_file=None),
        session=None,
    )

    output = await service.sign_pdf(
        sample_pdf_bytes,
        SigningMetadata(
            display_name="KOVACS DAVID",
            signer_role="Consilier juridic",
            contact_email="kovacs.david@institutie.ro",
            reason="Aprobare document",
            location="Bucharest",
            signature_box=SignatureBox(page=0, x1=72, y1=72, x2=280, y2=145),
        ),
    )

    assert b"KOVACS DAVID" in output
    assert b"Consilier juridic" in output
    assert b"SEMNAT ELECTRONIC" in output
    assert b"Aprobare document" in output
    assert b"Bucharest" in output


def test_signature_appearance_params_include_card_details():
    params = PDFSigningService._signature_appearance_params(
        SigningMetadata(
            display_name="Kovacs David",
            signer_role="Consilier juridic",
            contact_phone="+40 721 123 456",
            contact_email="kovacs.david@institutie.ro",
            contact_website="www.institutie.ro",
            reason="Aprobare document",
            location="Bucharest",
        ),
        for_seal=False,
    )

    assert params["signer"] == "Kovacs David"
    assert params["role"] == "Consilier juridic"
    assert "+40 721 123 456" in params["details"]
    assert "kovacs.david@institutie.ro" in params["details"]
    assert "www.institutie.ro" in params["details"]
    assert "Motiv: Aprobare document" in params["details"]
    assert "Locatie: Bucharest" in params["details"]


def test_modern_signature_avatar_uses_configured_colors():
    commands = ModernSignatureStamp._avatar_commands(
        width=260,
        height=90,
        accent_color=(0.11, 0.22, 0.33),
        fill_color=(0.77, 0.88, 0.99),
    )
    command_stream = b" ".join(commands)

    assert b"0.11 0.22 0.33 RG" in command_stream
    assert b"0.77 0.88 0.99 rg" in command_stream


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
