import pytest
from pydantic import ValidationError

from csc_signing_service.models import (
    ElectronicSealMetadata,
    SignatureBox,
    SigningMetadata,
    StampMetadata,
)


def test_metadata_defaults_to_invisible_signature():
    metadata = SigningMetadata()

    assert metadata.field_name == "Signature1"
    assert metadata.reason == "Demo CSC signing"
    assert metadata.location is None
    assert metadata.signature_box is None


def test_signature_box_must_have_positive_area():
    with pytest.raises(ValidationError):
        SignatureBox(page=0, x1=10, y1=10, x2=10, y2=20)

    with pytest.raises(ValidationError):
        SignatureBox(page=0, x1=10, y1=20, x2=20, y2=20)


def test_field_name_cannot_contain_dots():
    with pytest.raises(ValidationError):
        SigningMetadata(field_name="Sig.1")


def test_electronic_seal_metadata_defaults():
    metadata = ElectronicSealMetadata()

    assert metadata.field_name == "SigiliuElectronic1"
    assert metadata.reason == "Sigiliu electronic instituțional"
    assert metadata.location == "București, România"
    assert metadata.signature_box is None
    assert metadata.stamp is None


def test_electronic_seal_field_name_uses_signature_rules():
    with pytest.raises(ValidationError):
        ElectronicSealMetadata(field_name="Seal.1")


def test_stamp_metadata_defaults():
    metadata = StampMetadata()

    assert metadata.text == "Demo stamp %(ts)s"
    assert metadata.page == 0
    assert metadata.x == 72
    assert metadata.y == 72
    assert metadata.background_opacity == 0.35
    assert metadata.text_color == "#0b3b82"
    assert metadata.border_color == "#0b3b82"
    assert metadata.text_color_rgb() == pytest.approx((11 / 255, 59 / 255, 130 / 255))


def test_stamp_metadata_validates_text_dimensions_and_opacity():
    with pytest.raises(ValidationError):
        StampMetadata(text=" ")

    with pytest.raises(ValidationError):
        StampMetadata(width=0)

    with pytest.raises(ValidationError):
        StampMetadata(background_opacity=1.1)

    with pytest.raises(ValidationError):
        StampMetadata(text_color="065f5b")
