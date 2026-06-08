import asyncio
from io import BytesIO
from typing import Optional

import aiohttp
from pyhanko.pdf_utils import layout
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.misc import PdfReadError, PdfWriteError
from pyhanko.sign import fields
from pyhanko.sign.general import SigningError
from pyhanko.sign.signers import PdfSignatureMetadata, async_sign_pdf
from pyhanko.sign.signers.csc_signer import (
    CSCServiceSessionInfo,
    CSCSigner,
    fetch_certs_in_csc_credential,
)
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


class PDFSigningService:
    def __init__(self, settings: Settings, session: aiohttp.ClientSession):
        self.settings = settings
        self.session = session

    async def check_ready(
        self,
        oauth_token: Optional[str] = None,
        *,
        credential_id: Optional[str] = None,
        for_seal: bool = False,
    ) -> None:
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

        try:
            await async_sign_pdf(
                writer,
                signature_meta=signature_meta,
                signer=signer,
                new_field_spec=new_field_spec,
                existing_fields_only=existing_fields_only,
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
            raise CSCProviderError("pyHanko CSC signing failed") from exc

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

    @staticmethod
    def _assert_pdf(pdf_bytes: bytes) -> None:
        if not pdf_bytes:
            raise InvalidPDFError("PDF upload is empty")
        if not pdf_bytes.startswith(b"%PDF-"):
            raise InvalidPDFError("PDF upload does not start with a PDF header")
