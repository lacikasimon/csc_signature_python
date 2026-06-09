import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Optional

import aiohttp
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from pyhanko.keys import (
    load_certs_from_pemder_data,
    load_private_key_from_pemder_data,
)
from pyhanko.pdf_utils import layout
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.misc import PdfReadError, PdfWriteError
from pyhanko.sign import fields
from pyhanko.sign.general import SigningError
from pyhanko.sign.signers import PdfSignatureMetadata, PdfSigner, SimpleSigner
from pyhanko.sign.signers.csc_signer import (
    CSCServiceSessionInfo,
    CSCSigner,
    fetch_certs_in_csc_credential,
)
from pyhanko_certvalidator.registry import SimpleCertificateStore
from pyhanko.stamp import TextStamp, TextStampStyle
from pyhanko.pdf_utils.text import TextBoxStyle

from .config import Settings
from .csc import HashPinnedCSCAuthManager
from .errors import CSCProviderError, CSCProviderTimeoutError, InvalidPDFError
from .models import (
    ElectronicSealMetadata,
    SignaturePlaceholder,
    SignaturePlaceholdersMetadata,
    SigningMetadata,
    StampMetadata,
)


@dataclass(frozen=True)
class ModernSignatureStampStyle(TextStampStyle):
    fill_color: tuple[float, float, float] = (0.99, 1.0, 1.0)
    accent_color: tuple[float, float, float] = (0.02, 0.19, 0.42)
    border_color: tuple[float, float, float] = (0.74, 0.82, 0.91)
    avatar_fill_color: tuple[float, float, float] = (0.90, 0.94, 0.98)
    watermark_color: tuple[float, float, float] = (0.91, 0.95, 0.98)
    divider_color: tuple[float, float, float] = (0.03, 0.22, 0.47)
    border_width: int = 1

    def create_stamp(
        self,
        writer,
        box: layout.BoxConstraints,
        text_params: dict,
    ) -> "ModernSignatureStamp":
        return ModernSignatureStamp(
            writer=writer,
            style=self,
            box=box,
            text_params=text_params,
        )


class ModernSignatureStamp(TextStamp):
    _CIRCLE_KAPPA = 0.5522847498

    def render(self):
        width = self.box.width
        height = self.box.height
        fill = self.style.fill_color
        accent = self.style.accent_color
        border = self.style.border_color
        commands = [
            b"q",
            b"%g %g %g rg 0 0 %g %g re f" % (*fill, width, height),
        ]
        commands.extend(self._soft_corner_commands(width, height))
        commands.extend(
            self._watermark_commands(
                width,
                height,
                self.style.watermark_color,
            )
        )
        commands.append(b"%g %g %g rg 0 0 2.2 %g re f" % (*accent, height))
        commands.extend(
            self._avatar_commands(
                width,
                height,
                accent_color=accent,
                fill_color=self.style.avatar_fill_color,
            )
        )
        commands.extend(
            self._divider_commands(width, height, self.style.divider_color)
        )
        commands.append(
            b"%g %g %g RG %g w 0.5 0.5 %g %g re S"
            % (*border, self.style.border_width, width - 1, height - 1)
        )
        commands.extend(self._render_inner_content())
        commands.append(b"Q")
        return b" ".join(commands)

    @staticmethod
    def _soft_corner_commands(width: float, height: float) -> list[bytes]:
        radius = min(width * 0.28, height * 1.2)
        return [
            ModernSignatureStamp._filled_circle_command(
                cx=-radius * 0.35,
                cy=-radius * 0.58,
                radius=radius,
                color=(0.92, 0.96, 0.99),
            )
        ]

    @staticmethod
    def _avatar_commands(
        width: float,
        height: float,
        *,
        accent_color: tuple[float, float, float],
        fill_color: tuple[float, float, float],
    ) -> list[bytes]:
        radius = min(height * 0.30, width * 0.12)
        if radius < 10:
            return []

        center_x = max(radius + 12, min(width * 0.22, radius + 34))
        center_y = height * 0.56
        head_radius = radius * 0.27
        body_width = radius * 0.92
        body_y = center_y - radius * 0.38
        line_width = max(1.1, min(2.2, height * 0.028))

        return [
            ModernSignatureStamp._filled_circle_command(
                cx=center_x,
                cy=center_y,
                radius=radius,
                color=fill_color,
            ),
            ModernSignatureStamp._stroked_circle_command(
                cx=center_x,
                cy=center_y + radius * 0.18,
                radius=head_radius,
                color=accent_color,
                line_width=line_width,
            ),
            b"%g %g %g RG %g w 1 J 1 j %g %g m "
            b"%g %g %g %g %g %g c S"
            % (
                *accent_color,
                line_width,
                center_x - body_width * 0.52,
                body_y,
                center_x - body_width * 0.52,
                body_y + radius * 0.34,
                center_x + body_width * 0.52,
                body_y + radius * 0.34,
                center_x + body_width * 0.52,
                body_y,
            ),
        ]

    @staticmethod
    def _watermark_commands(
        width: float,
        height: float,
        color: tuple[float, float, float],
    ) -> list[bytes]:
        if width < 145 or height < 55:
            return []

        mark_width = min(width * 0.30, height * 1.1)
        mark_height = min(height * 0.72, mark_width * 0.76)
        x = width - mark_width - 8
        y = height * 0.16
        roof_y = y + mark_height * 0.58
        top_y = y + mark_height * 0.86
        base_y = y + mark_height * 0.32
        line_width = max(1.7, min(4.0, height * 0.034))
        commands = [
            b"%g %g %g RG %g w 1 J 1 j %g %g m %g %g l %g %g l S"
            % (
                *color,
                line_width,
                x,
                roof_y,
                x + mark_width * 0.5,
                top_y,
                x + mark_width,
                roof_y,
            ),
            b"%g %g %g RG %g w %g %g m %g %g l S"
            % (
                *color,
                line_width,
                x + mark_width * 0.08,
                base_y,
                x + mark_width * 0.92,
                base_y,
            ),
            b"%g %g %g RG %g w %g %g m %g %g l S"
            % (
                *color,
                line_width,
                x + mark_width * 0.5,
                top_y,
                x + mark_width * 0.5,
                top_y + mark_height * 0.20,
            ),
        ]
        for index in range(4):
            column_x = x + mark_width * (0.22 + index * 0.17)
            commands.append(
                b"%g %g %g RG %g w %g %g m %g %g l S"
                % (
                    *color,
                    line_width,
                    column_x,
                    y + mark_height * 0.08,
                    column_x,
                    base_y,
                )
            )
        commands.extend(
            [
                b"%g %g %g RG %g w %g %g m %g %g l S"
                % (
                    *color,
                    line_width,
                    x + mark_width * 0.10,
                    y + mark_height * 0.08,
                    x + mark_width * 0.90,
                    y + mark_height * 0.08,
                ),
                b"%g %g %g RG %g w %g %g m %g %g l S"
                % (
                    *color,
                    line_width,
                    x,
                    y,
                    x + mark_width,
                    y,
                ),
            ]
        )
        return commands

    @staticmethod
    def _divider_commands(
        width: float,
        height: float,
        color: tuple[float, float, float],
    ) -> list[bytes]:
        if width < 150 or height < 58:
            return []
        start_x = min(width * 0.34, 108)
        end_x = width - min(width * 0.10, 34)
        y = height * 0.12
        return [
            b"%g %g %g RG 0.75 w %g %g m %g %g l S"
            % (*color, start_x, y, end_x, y)
        ]

    @staticmethod
    def _filled_circle_command(
        *,
        cx: float,
        cy: float,
        radius: float,
        color: tuple[float, float, float],
    ) -> bytes:
        return (
            b"%g %g %g rg " % (*color,)
            + ModernSignatureStamp._circle_path(cx, cy, radius)
            + b" f"
        )

    @staticmethod
    def _stroked_circle_command(
        *,
        cx: float,
        cy: float,
        radius: float,
        color: tuple[float, float, float],
        line_width: float,
    ) -> bytes:
        return (
            b"%g %g %g RG %g w "
            % (
                *color,
                line_width,
            )
            + ModernSignatureStamp._circle_path(cx, cy, radius)
            + b" S"
        )

    @staticmethod
    def _circle_path(cx: float, cy: float, radius: float) -> bytes:
        control = radius * ModernSignatureStamp._CIRCLE_KAPPA
        return (
            b"%g %g m %g %g %g %g %g %g c "
            b"%g %g %g %g %g %g c "
            b"%g %g %g %g %g %g c "
            b"%g %g %g %g %g %g c h"
            % (
                cx + radius,
                cy,
                cx + radius,
                cy + control,
                cx + control,
                cy + radius,
                cx,
                cy + radius,
                cx - control,
                cy + radius,
                cx - radius,
                cy + control,
                cx - radius,
                cy,
                cx - radius,
                cy - control,
                cx - control,
                cy - radius,
                cx,
                cy - radius,
                cx + control,
                cy - radius,
                cx + radius,
                cy - control,
                cx + radius,
                cy,
            )
        )


class PDFSigningService:
    def __init__(self, settings: Settings, session: aiohttp.ClientSession):
        self.settings = settings
        self.session = session
        self._local_signer: Optional[SimpleSigner] = None

    async def check_ready(
        self,
        oauth_token: Optional[str] = None,
        *,
        credential_id: Optional[str] = None,
        for_seal: bool = False,
    ) -> None:
        if self.settings.local_signing_enabled:
            self._local_pdf_signer()
            return
        await self._fetch_credential_info(
            oauth_token=oauth_token,
            credential_id=credential_id,
            for_seal=for_seal,
        )

    async def sign_pdf(
        self,
        pdf_bytes: bytes,
        metadata: SigningMetadata,
        oauth_token: Optional[str] = None,
        *,
        credential_id: Optional[str] = None,
        for_seal: bool = False,
        existing_fields_only: bool = False,
    ) -> bytes:
        self._assert_pdf(pdf_bytes)
        if metadata.stamp is not None:
            pdf_bytes = self.stamp_pdf(pdf_bytes, metadata.stamp)

        signing_backend = (
            "local demo" if self.settings.local_signing_enabled else "CSC"
        )
        if self.settings.local_signing_enabled:
            signer = self._local_pdf_signer()
        else:
            session_info = self._session_info(
                oauth_token=oauth_token,
                credential_id=credential_id,
                for_seal=for_seal,
            )
            credential_info = await self._fetch_credential_info(
                session_info=session_info
            )
            auth_manager = HashPinnedCSCAuthManager(
                self.session,
                csc_session_info=session_info,
                credential_info=credential_info,
                request_timeout=self.settings.signing_timeout_seconds,
            )
            signer = CSCSigner(
                self.session,
                auth_manager=auth_manager,
                sign_timeout=self.settings.signing_timeout_seconds,
            )

        try:
            writer = IncrementalPdfFileWriter(BytesIO(pdf_bytes))
        except PdfReadError as exc:
            raise InvalidPDFError("Input is not a readable PDF") from exc

        signature_meta = PdfSignatureMetadata(
            field_name=metadata.field_name,
            md_algorithm=self.settings.pdf_digest_algorithm,
            reason=metadata.reason,
            location=metadata.location,
            subfilter=fields.SigSeedSubFilter.PADES,
        )
        new_field_spec = (
            None if existing_fields_only else self._new_field_spec(metadata)
        )
        output = BytesIO()
        pdf_signer = PdfSigner(
            signature_meta,
            signer,
            stamp_style=self._signature_stamp_style(for_seal=for_seal),
            new_field_spec=new_field_spec,
        )

        try:
            await pdf_signer.async_sign_pdf(
                writer,
                existing_fields_only=existing_fields_only,
                appearance_text_params=self._signature_appearance_params(
                    metadata,
                    for_seal=for_seal,
                ),
                output=output,
            )
        except CSCProviderTimeoutError:
            raise
        except CSCProviderError:
            raise
        except asyncio.TimeoutError as exc:
            raise CSCProviderTimeoutError("CSC signing request timed out") from exc
        except aiohttp.ClientResponseError as exc:
            raise CSCProviderError(
                f"CSC signatures/signHash request failed with HTTP {exc.status}"
            ) from exc
        except aiohttp.ClientError as exc:
            raise CSCProviderError("CSC signatures/signHash request failed") from exc
        except PdfReadError as exc:
            raise InvalidPDFError("Input is not a readable PDF") from exc
        except SigningError as exc:
            raise CSCProviderError(f"pyHanko {signing_backend} signing failed") from exc

        return output.getvalue()

    async def sign_existing_field_pdf(
        self,
        pdf_bytes: bytes,
        metadata: SigningMetadata,
        oauth_token: Optional[str] = None,
    ) -> bytes:
        return await self.sign_pdf(
            pdf_bytes,
            metadata,
            oauth_token=oauth_token,
            existing_fields_only=True,
        )

    async def seal_pdf(
        self,
        pdf_bytes: bytes,
        metadata: ElectronicSealMetadata,
        oauth_token: Optional[str] = None,
    ) -> bytes:
        return await self.sign_pdf(
            pdf_bytes,
            metadata,
            oauth_token=oauth_token,
            credential_id=self.settings.seal_credential_id,
            for_seal=True,
        )

    def stamp_pdf(self, pdf_bytes: bytes, metadata: StampMetadata) -> bytes:
        self._assert_pdf(pdf_bytes)
        try:
            writer = IncrementalPdfFileWriter(BytesIO(pdf_bytes))
            style = TextStampStyle(
                stamp_text=metadata.text,
                background_opacity=metadata.background_opacity,
                border_width=metadata.border_width,
                border_color=metadata.border_color_rgb(),
                text_box_style=TextBoxStyle(
                    font_size=metadata.font_size,
                    text_color=metadata.text_color_rgb(),
                ),
            )
            text_stamp = TextStamp(
                writer,
                style=style,
                box=layout.BoxConstraints(
                    width=metadata.width,
                    height=metadata.height,
                ),
            )
            text_stamp.apply(metadata.page, metadata.x, metadata.y)
            output = BytesIO()
            writer.write(output)
            return output.getvalue()
        except PdfReadError as exc:
            raise InvalidPDFError("Input is not a readable PDF") from exc
        except (IndexError, ValueError, layout.LayoutError) as exc:
            raise InvalidPDFError("Stamp metadata is not valid for this PDF") from exc

    def add_signature_placeholders(
        self,
        pdf_bytes: bytes,
        metadata: SignaturePlaceholdersMetadata,
    ) -> bytes:
        self._assert_pdf(pdf_bytes)
        try:
            writer = IncrementalPdfFileWriter(BytesIO(pdf_bytes))
            for placeholder in metadata.placeholders:
                fields.append_signature_field(
                    writer,
                    self._placeholder_field_spec(
                        placeholder,
                        empty_field_appearance=metadata.empty_field_appearance,
                    ),
                )
            output = BytesIO()
            writer.write(output)
            return output.getvalue()
        except PdfReadError as exc:
            raise InvalidPDFError("Input is not a readable PDF") from exc
        except (IndexError, ValueError, PdfWriteError) as exc:
            raise InvalidPDFError(
                "Signature placeholder metadata is not valid for this PDF"
            ) from exc

    def _session_info(
        self,
        oauth_token: Optional[str] = None,
        *,
        credential_id: Optional[str] = None,
        for_seal: bool = False,
    ) -> CSCServiceSessionInfo:
        effective_token = self.settings.oauth_token_for_request(
            oauth_token,
            for_seal=for_seal,
        )
        return CSCServiceSessionInfo(
            service_url=self.settings.csc_service_url,
            credential_id=credential_id or self.settings.csc_credential_id,
            oauth_token=effective_token,
            api_ver=self.settings.csc_api_version,
        )

    async def _fetch_credential_info(
        self,
        session_info: Optional[CSCServiceSessionInfo] = None,
        oauth_token: Optional[str] = None,
        credential_id: Optional[str] = None,
        for_seal: bool = False,
    ):
        session_info = session_info or self._session_info(
            oauth_token=oauth_token,
            credential_id=credential_id,
            for_seal=for_seal,
        )
        try:
            return await fetch_certs_in_csc_credential(
                session=self.session,
                csc_session_info=session_info,
                timeout=self.settings.signing_timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            raise CSCProviderTimeoutError(
                "CSC credentials/info request timed out"
            ) from exc
        except aiohttp.ClientResponseError as exc:
            raise CSCProviderError(
                f"CSC credentials/info request failed with HTTP {exc.status}"
            ) from exc
        except aiohttp.ClientError as exc:
            raise CSCProviderError("CSC credentials/info request failed") from exc
        except SigningError as exc:
            raise CSCProviderError(
                "CSC credentials/info response did not contain usable certificates"
            ) from exc

    @staticmethod
    def _new_field_spec(metadata: SigningMetadata) -> fields.SigFieldSpec:
        box = metadata.signature_box
        if box is None:
            return fields.SigFieldSpec(sig_field_name=metadata.field_name)
        return fields.SigFieldSpec(
            sig_field_name=metadata.field_name,
            on_page=box.page,
            box=box.as_tuple(),
        )

    @staticmethod
    def _placeholder_field_spec(
        placeholder: SignaturePlaceholder,
        *,
        empty_field_appearance: bool,
    ) -> fields.SigFieldSpec:
        return fields.SigFieldSpec(
            sig_field_name=placeholder.field_name,
            on_page=placeholder.box.page,
            box=placeholder.box.as_tuple(),
            empty_field_appearance=empty_field_appearance,
        )

    def _local_pdf_signer(self) -> SimpleSigner:
        if self._local_signer is None:
            self._local_signer = _generate_local_demo_signer(
                common_name=self.settings.local_signing_common_name,
                valid_days=self.settings.local_signing_valid_days,
            )
        return self._local_signer

    @staticmethod
    def _signature_stamp_style(*, for_seal: bool) -> ModernSignatureStampStyle:
        title = "SIGILIU ELECTRONIC" if for_seal else "SEMNAT ELECTRONIC"
        stamp_text = (
            "%(signer)s\n"
            "%(role)s\n"
            f"{title} - %(ts)s\n"
            "%(details)s"
        )
        return ModernSignatureStampStyle(
            stamp_text=stamp_text,
            timestamp_format="%d.%m.%Y %H:%M",
            text_box_style=TextBoxStyle(
                font_size=8,
                leading=9,
                text_color=(0.02, 0.12, 0.28),
            ),
            inner_content_layout=layout.SimpleBoxLayoutRule(
                x_align=layout.AxisAlignment.ALIGN_MIN,
                y_align=layout.AxisAlignment.ALIGN_MID,
                margins=layout.Margins(left=96, right=28, top=10, bottom=8),
            ),
        )

    @staticmethod
    def _signature_appearance_params(
        metadata: SigningMetadata,
        *,
        for_seal: bool,
    ) -> dict[str, str]:
        contact_lines = [
            value
            for value in (
                metadata.contact_phone,
                metadata.contact_email,
                metadata.contact_website,
            )
            if value
        ]
        detail_lines = [*contact_lines]
        if metadata.reason:
            detail_lines.append(f"Motiv: {metadata.reason}")
        if metadata.location:
            detail_lines.append(f"Locatie: {metadata.location}")

        role = metadata.signer_role
        if role is None:
            role = "Instituție publică" if for_seal else metadata.field_name

        params = {
            "role": role,
            "details": "\n".join(detail_lines) or "-",
            "reason": metadata.reason or "-",
            "location": metadata.location or "-",
            "kind": "sigiliu electronic" if for_seal else "semnătură electronică",
        }
        if metadata.display_name:
            params["signer"] = metadata.display_name
        return params

    @staticmethod
    def _assert_pdf(pdf_bytes: bytes) -> None:
        if not pdf_bytes:
            raise InvalidPDFError("PDF upload is empty")
        if not pdf_bytes.startswith(b"%PDF-"):
            raise InvalidPDFError("PDF upload does not start with a PDF header")


def _generate_local_demo_signer(
    *,
    common_name: str,
    valid_days: int,
) -> SimpleSigner:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, common_name)]
    )
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=valid_days))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    signing_key = load_private_key_from_pemder_data(key_pem, passphrase=None)
    signing_cert = list(load_certs_from_pemder_data(cert_pem))[0]
    cert_store = SimpleCertificateStore()
    cert_store.register(signing_cert)
    return SimpleSigner(
        signing_cert=signing_cert,
        signing_key=signing_key,
        cert_registry=cert_store,
    )
