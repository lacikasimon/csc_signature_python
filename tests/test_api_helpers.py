from io import BytesIO

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from csc_signing_service.api import (
    _parse_metadata,
    _parse_seal_metadata,
    _parse_signature_placeholders_metadata,
    _parse_stamp_metadata,
    _read_upload,
)


def test_parse_empty_metadata_uses_defaults():
    metadata = _parse_metadata(None)

    assert metadata.field_name == "Signature1"
    assert metadata.signature_box is None
    assert metadata.stamp is None


def test_parse_invalid_metadata_raises_422():
    with pytest.raises(HTTPException) as exc_info:
        _parse_metadata('{"signature_box": {"page": 0, "x1": 10}}')

    assert exc_info.value.status_code == 422


def test_parse_signing_metadata_with_stamp():
    metadata = _parse_metadata(
        '{"field_name": "Sig1", "stamp": {"text": "Reviewed", '
        '"x": 10, "y": 20, "width": 100, "height": 40}, '
        '"display_name": "Kovacs David", '
        '"signer_role": "Consilier juridic", '
        '"contact_email": "kovacs.david@institutie.ro"}'
    )

    assert metadata.field_name == "Sig1"
    assert metadata.display_name == "Kovacs David"
    assert metadata.signer_role == "Consilier juridic"
    assert metadata.contact_email == "kovacs.david@institutie.ro"
    assert metadata.stamp is not None
    assert metadata.stamp.text == "Reviewed"
    assert metadata.stamp.x == 10


def test_parse_empty_stamp_metadata_uses_defaults():
    metadata = _parse_stamp_metadata(None)

    assert metadata.text == "Demo stamp %(ts)s"
    assert metadata.page == 0
    assert metadata.width == 220


def test_parse_empty_seal_metadata_uses_defaults():
    metadata = _parse_seal_metadata(None)

    assert metadata.field_name == "SigiliuElectronic1"
    assert metadata.reason == "Sigiliu electronic instituțional"
    assert metadata.location == "București, România"
    assert metadata.signature_box is None


def test_parse_seal_metadata_rejects_invalid_box():
    with pytest.raises(HTTPException) as exc_info:
        _parse_seal_metadata(
            '{"signature_box": {"page": 0, "x1": 5, '
            '"y1": 5, "x2": 5, "y2": 20}}'
        )

    assert exc_info.value.status_code == 422


def test_parse_signature_placeholders_metadata():
    metadata = _parse_signature_placeholders_metadata(
        '{"sign_first": true, "sign_reason": "Aprobare", '
        '"sign_location": "București", "placeholders": ['
        '{"field_name": "Semnatar1", "box": {"page": 0, "x1": 10, "y1": 10, "x2": 80, "y2": 40}},'
        '{"field_name": "Semnatar2", "box": {"page": 0, "x1": 100, "y1": 10, "x2": 170, "y2": 40}}'
        ']}'
    )

    assert len(metadata.placeholders) == 2
    assert metadata.sign_first is True
    assert metadata.sign_reason == "Aprobare"
    assert metadata.sign_location == "București"
    assert metadata.placeholders[0].field_name == "Semnatar1"
    assert metadata.placeholders[1].box.x2 == 170


def test_parse_signature_placeholders_metadata_rejects_duplicates():
    with pytest.raises(HTTPException) as exc_info:
        _parse_signature_placeholders_metadata(
            '{"placeholders": ['
            '{"field_name": "Semnatar1", "box": {"page": 0, "x1": 10, "y1": 10, "x2": 80, "y2": 40}},'
            '{"field_name": "Semnatar1", "box": {"page": 0, "x1": 100, "y1": 10, "x2": 170, "y2": 40}}'
            ']}'
        )

    assert exc_info.value.status_code == 422


def test_parse_invalid_stamp_metadata_raises_422():
    with pytest.raises(HTTPException) as exc_info:
        _parse_stamp_metadata('{"text": "   "}')

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_read_upload_rejects_missing_filename(sample_pdf_bytes):
    upload = UploadFile(filename="", file=None)

    with pytest.raises(HTTPException) as exc_info:
        await _read_upload(upload, max_bytes=10)

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_read_upload_rejects_oversized_file(sample_pdf_bytes):
    upload = UploadFile(filename="input.pdf", file=BytesIO(sample_pdf_bytes))

    with pytest.raises(HTTPException) as exc_info:
        await _read_upload(upload, max_bytes=5)

    assert exc_info.value.status_code == 400
