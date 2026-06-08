from io import BytesIO

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from csc_signing_service.api import (
    _parse_metadata,
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
        '"x": 10, "y": 20, "width": 100, "height": 40}}'
    )

    assert metadata.field_name == "Sig1"
    assert metadata.stamp is not None
    assert metadata.stamp.text == "Reviewed"
    assert metadata.stamp.x == 10


def test_parse_empty_stamp_metadata_uses_defaults():
    metadata = _parse_stamp_metadata(None)

    assert metadata.text == "Demo stamp %(ts)s"
    assert metadata.page == 0
    assert metadata.width == 220


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
