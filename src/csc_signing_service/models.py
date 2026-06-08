from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator


class SignatureBox(BaseModel):
    page: int = Field(default=0, ge=0)
    x1: int
    y1: int
    x2: int
    y2: int

    @model_validator(mode="after")
    def validate_box(self) -> "SignatureBox":
        if self.x2 <= self.x1:
            raise ValueError("x2 must be greater than x1")
        if self.y2 <= self.y1:
            raise ValueError("y2 must be greater than y1")
        return self

    def as_tuple(self) -> Tuple[int, int, int, int]:
        return self.x1, self.y1, self.x2, self.y2


class StampMetadata(BaseModel):
    text: str = Field(default="Demo stamp %(ts)s", min_length=1)
    page: int = Field(default=0, ge=0)
    x: int = Field(default=72, ge=0)
    y: int = Field(default=72, ge=0)
    width: int = Field(default=220, gt=0)
    height: int = Field(default=60, gt=0)
    font_size: int = Field(default=10, gt=0, le=72)
    background_opacity: float = Field(default=0.35, ge=0, le=1)
    border_width: float = Field(default=1, ge=0, le=20)
    text_color: str = Field(default="#0b3b82")
    border_color: str = Field(default="#0b3b82")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("text cannot be empty")
        return normalized

    @field_validator("text_color", "border_color")
    @classmethod
    def validate_hex_color(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) != 7 or not normalized.startswith("#"):
            raise ValueError("color must use #RRGGBB format")
        try:
            int(normalized[1:], 16)
        except ValueError as exc:
            raise ValueError("color must use #RRGGBB format") from exc
        return normalized.lower()

    def text_color_rgb(self) -> Tuple[float, float, float]:
        return self._hex_to_rgb(self.text_color)

    def border_color_rgb(self) -> Tuple[float, float, float]:
        return self._hex_to_rgb(self.border_color)

    @staticmethod
    def _hex_to_rgb(value: str) -> Tuple[float, float, float]:
        return tuple(
            int(value[index : index + 2], 16) / 255
            for index in (1, 3, 5)
        )


class SigningMetadata(BaseModel):
    field_name: str = Field(default="Signature1", min_length=1)
    reason: Optional[str] = "Demo CSC signing"
    location: Optional[str] = None
    signature_box: Optional[SignatureBox] = None
    stamp: Optional[StampMetadata] = None

    @field_validator("field_name")
    @classmethod
    def validate_field_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("field_name cannot be empty")
        if "." in normalized:
            raise ValueError("field_name cannot contain dots")
        return normalized


class ElectronicSealMetadata(SigningMetadata):
    field_name: str = Field(default="SigiliuElectronic1", min_length=1)
    reason: Optional[str] = "Sigiliu electronic instituțional"
    location: Optional[str] = "București, România"


class SignaturePlaceholder(BaseModel):
    field_name: str = Field(default="Signature1", min_length=1)
    box: SignatureBox

    @field_validator("field_name")
    @classmethod
    def validate_field_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("field_name cannot be empty")
        if "." in normalized:
            raise ValueError("field_name cannot contain dots")
        return normalized


def default_signature_placeholders() -> List[SignaturePlaceholder]:
    return [
        SignaturePlaceholder(
            field_name="Signature1",
            box=SignatureBox(page=0, x1=72, y1=72, x2=260, y2=140),
        )
    ]


class SignaturePlaceholdersMetadata(BaseModel):
    placeholders: List[SignaturePlaceholder] = Field(
        default_factory=default_signature_placeholders,
        min_length=1,
        max_length=20,
    )
    empty_field_appearance: bool = True
    sign_first: bool = False
    sign_reason: Optional[str] = "Semnare prima poziție"
    sign_location: Optional[str] = "București, România"

    @model_validator(mode="after")
    def validate_unique_field_names(self) -> "SignaturePlaceholdersMetadata":
        names = [placeholder.field_name for placeholder in self.placeholders]
        if len(names) != len(set(names)):
            raise ValueError("placeholder field names must be unique")
        return self
