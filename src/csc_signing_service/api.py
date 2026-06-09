import base64
import binascii
import logging
import secrets
import uuid
from contextlib import asynccontextmanager
from typing import Any, Optional

import aiohttp
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import ValidationError

from .config import Settings, get_settings
from .errors import CSCProviderError, CSCProviderTimeoutError, InvalidPDFError
from .models import (
    ElectronicSealMetadata,
    SignaturePlaceholdersMetadata,
    SigningMetadata,
    StampMetadata,
)
from .pdf_preview import render_pdf_page
from .signing import PDFSigningService
from .web import DEMO_HTML

AUTH_EXEMPT_PATHS = {"/healthz"}
LOGGER = logging.getLogger("csc_signing_service.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    async with aiohttp.ClientSession() as session:
        app.state.settings = settings
        app.state.signing_service = PDFSigningService(settings, session)
        yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="CSC PDF Signing API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def request_diagnostics_and_auth(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id
        settings = getattr(request.app.state, "settings", None) or get_settings()
        try:
            if settings.app_password and request.url.path not in AUTH_EXEMPT_PATHS:
                if not _basic_auth_matches(
                    request.headers.get("Authorization"),
                    username=settings.app_username,
                    password=settings.app_password,
                ):
                    response = _auth_challenge()
                else:
                    response = await call_next(request)
            else:
                response = await call_next(request)
        except Exception as exc:
            LOGGER.exception(
                "unhandled request error request_id=%s method=%s path=%s",
                request_id,
                request.method,
                request.url.path,
            )
            message = (
                f"{type(exc).__name__}: {exc}"
                if settings.app_error_details_enabled
                else "Unexpected server error"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": _error_detail(
                        request,
                        code="internal_error",
                        message=message,
                    )
                },
                headers={"X-Request-ID": request_id},
            )
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(HTTPException)
    async def structured_http_exception_handler(
        request: Request,
        exc: HTTPException,
    ):
        if isinstance(exc.detail, dict) and "message" in exc.detail:
            return await http_exception_handler(request, exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": _error_detail(
                    request,
                    code=_default_error_code(exc.status_code),
                    message=_stringify_detail(exc.detail),
                    errors=exc.detail if isinstance(exc.detail, list) else None,
                )
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def structured_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        LOGGER.info(
            "request validation failed request_id=%s method=%s path=%s errors=%s",
            _request_id(request),
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": _error_detail(
                    request,
                    code="request_validation_error",
                    message="Request validation failed",
                    errors=exc.errors(),
                )
            },
        )

    @app.get("/", include_in_schema=False)
    async def demo_ui():
        return HTMLResponse(DEMO_HTML)

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz(
        request: Request,
        x_csc_oauth_token: Optional[str] = Header(default=None),
    ):
        service = _service(request)
        try:
            await service.check_ready(oauth_token=x_csc_oauth_token)
        except CSCProviderTimeoutError as exc:
            raise _http_error(request, 503, "csc_timeout", str(exc), exc) from exc
        except CSCProviderError as exc:
            raise _http_error(
                request,
                503,
                "csc_provider_error",
                str(exc),
                exc,
            ) from exc
        return {"status": "ready"}

    @app.get("/readyz/seal")
    async def readyz_seal(
        request: Request,
        x_csc_oauth_token: Optional[str] = Header(default=None),
        x_csc_seal_oauth_token: Optional[str] = Header(default=None),
    ):
        service = _service(request)
        settings = _settings(request)
        try:
            await service.check_ready(
                oauth_token=x_csc_seal_oauth_token or x_csc_oauth_token,
                credential_id=settings.seal_credential_id,
                for_seal=True,
            )
        except CSCProviderTimeoutError as exc:
            raise _http_error(request, 503, "csc_timeout", str(exc), exc) from exc
        except CSCProviderError as exc:
            raise _http_error(
                request,
                503,
                "csc_provider_error",
                str(exc),
                exc,
            ) from exc
        return {"status": "ready", "credential_type": "electronic_seal"}

    @app.post("/v1/sign/pdf")
    async def sign_pdf(
        request: Request,
        pdf: UploadFile = File(...),
        metadata: Optional[str] = Form(default=None),
        x_csc_oauth_token: Optional[str] = Header(default=None),
    ):
        settings = _settings(request)
        pdf_bytes = await _read_upload(pdf, max_bytes=settings.max_pdf_bytes)
        signing_metadata = _parse_signing_metadata(metadata)
        service = _service(request)

        try:
            signed_pdf = await service.sign_pdf(
                pdf_bytes,
                signing_metadata,
                oauth_token=x_csc_oauth_token,
            )
        except InvalidPDFError as exc:
            raise _http_error(request, 422, "invalid_pdf", str(exc), exc) from exc
        except CSCProviderTimeoutError as exc:
            raise _http_error(request, 504, "csc_timeout", str(exc), exc) from exc
        except CSCProviderError as exc:
            raise _http_error(
                request,
                502,
                "csc_provider_error",
                str(exc),
                exc,
            ) from exc

        return Response(
            content=signed_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="signed.pdf"'
            },
        )

    @app.post("/v1/seal/pdf")
    async def seal_pdf(
        request: Request,
        pdf: UploadFile = File(...),
        metadata: Optional[str] = Form(default=None),
        x_csc_oauth_token: Optional[str] = Header(default=None),
        x_csc_seal_oauth_token: Optional[str] = Header(default=None),
    ):
        settings = _settings(request)
        pdf_bytes = await _read_upload(pdf, max_bytes=settings.max_pdf_bytes)
        seal_metadata = _parse_seal_metadata(metadata)
        service = _service(request)

        try:
            sealed_pdf = await service.seal_pdf(
                pdf_bytes,
                seal_metadata,
                oauth_token=x_csc_seal_oauth_token or x_csc_oauth_token,
            )
        except InvalidPDFError as exc:
            raise _http_error(request, 422, "invalid_pdf", str(exc), exc) from exc
        except CSCProviderTimeoutError as exc:
            raise _http_error(request, 504, "csc_timeout", str(exc), exc) from exc
        except CSCProviderError as exc:
            raise _http_error(
                request,
                502,
                "csc_provider_error",
                str(exc),
                exc,
            ) from exc

        return Response(
            content=sealed_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="sealed.pdf"'
            },
        )

    @app.post("/v1/stamp/pdf")
    async def stamp_pdf(
        request: Request,
        pdf: UploadFile = File(...),
        metadata: Optional[str] = Form(default=None),
    ):
        settings = _settings(request)
        pdf_bytes = await _read_upload(pdf, max_bytes=settings.max_pdf_bytes)
        stamp_metadata = _parse_stamp_metadata(metadata)
        service = _service(request)

        try:
            stamped_pdf = service.stamp_pdf(pdf_bytes, stamp_metadata)
        except InvalidPDFError as exc:
            raise _http_error(request, 422, "invalid_pdf", str(exc), exc) from exc

        return Response(
            content=stamped_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="stamped.pdf"'
            },
        )

    @app.post("/v1/signature-placeholders/pdf")
    async def signature_placeholders_pdf(
        request: Request,
        pdf: UploadFile = File(...),
        metadata: Optional[str] = Form(default=None),
        x_csc_oauth_token: Optional[str] = Header(default=None),
    ):
        settings = _settings(request)
        pdf_bytes = await _read_upload(pdf, max_bytes=settings.max_pdf_bytes)
        placeholders_metadata = _parse_signature_placeholders_metadata(metadata)
        service = _service(request)

        try:
            placeholders_pdf = service.add_signature_placeholders(
                pdf_bytes,
                placeholders_metadata,
            )
            if placeholders_metadata.sign_first:
                first_placeholder = placeholders_metadata.placeholders[0]
                placeholders_pdf = await service.sign_existing_field_pdf(
                    placeholders_pdf,
                    SigningMetadata(
                        field_name=first_placeholder.field_name,
                        reason=placeholders_metadata.sign_reason,
                        location=placeholders_metadata.sign_location,
                    ),
                    oauth_token=x_csc_oauth_token,
                )
        except InvalidPDFError as exc:
            raise _http_error(request, 422, "invalid_pdf", str(exc), exc) from exc
        except CSCProviderTimeoutError as exc:
            raise _http_error(request, 504, "csc_timeout", str(exc), exc) from exc
        except CSCProviderError as exc:
            raise _http_error(
                request,
                502,
                "csc_provider_error",
                str(exc),
                exc,
            ) from exc

        return Response(
            content=placeholders_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="signature-placeholders.pdf"'
            },
        )

    @app.post("/v1/pdf/page-image")
    async def pdf_page_image(
        request: Request,
        pdf: UploadFile = File(...),
        page: int = Form(default=0),
    ):
        settings = _settings(request)
        pdf_bytes = await _read_upload(pdf, max_bytes=settings.max_pdf_bytes)

        try:
            preview = render_pdf_page(pdf_bytes, page_index=page)
        except InvalidPDFError as exc:
            raise _http_error(request, 422, "invalid_pdf", str(exc), exc) from exc

        return Response(
            content=preview.image_bytes,
            media_type="image/png",
            headers={
                "X-PDF-Page-Count": str(preview.page_count),
                "X-PDF-Page-Index": str(preview.page_index),
                "X-PDF-Page-Width": f"{preview.page_width:.4f}",
                "X-PDF-Page-Height": f"{preview.page_height:.4f}",
            },
        )

    return app


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _service(request: Request) -> PDFSigningService:
    return request.app.state.signing_service


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _error_detail(
    request: Request,
    *,
    code: str,
    message: str,
    errors: Any = None,
) -> dict[str, Any]:
    detail: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": _request_id(request),
    }
    if errors is not None:
        detail["errors"] = errors
    return detail


def _http_error(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    exc: Exception,
) -> HTTPException:
    LOGGER.warning(
        "request failed request_id=%s method=%s path=%s status=%s code=%s message=%s",
        _request_id(request),
        request.method,
        request.url.path,
        status_code,
        code,
        message,
        exc_info=True,
    )
    return HTTPException(
        status_code=status_code,
        detail=_error_detail(request, code=code, message=message),
    )


def _default_error_code(status_code: int) -> str:
    if status_code == 400:
        return "bad_request"
    if status_code == 401:
        return "authentication_required"
    if status_code == 422:
        return "validation_error"
    if status_code >= 500:
        return "server_error"
    return "http_error"


def _stringify_detail(detail: Any) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        return "Request validation failed"
    if detail is None:
        return "Request failed"
    return str(detail)


def _basic_auth_matches(
    authorization: Optional[str],
    *,
    username: str,
    password: str,
) -> bool:
    if not authorization:
        return False
    scheme, _, credentials = authorization.partition(" ")
    if scheme.lower() != "basic" or not credentials:
        return False
    try:
        decoded = base64.b64decode(credentials, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return False
    supplied_username, separator, supplied_password = decoded.partition(":")
    if not separator:
        return False
    return secrets.compare_digest(
        supplied_username,
        username,
    ) and secrets.compare_digest(supplied_password, password)


def _auth_challenge() -> Response:
    return Response(
        content="Authentication required",
        media_type="text/plain",
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="CSC PDF Signer"'},
    )


async def _read_upload(upload: UploadFile, max_bytes: int) -> bytes:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Missing PDF filename")
    data = await upload.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(status_code=400, detail="PDF exceeds size limit")
    return data


def _parse_metadata(raw_metadata: Optional[str]) -> SigningMetadata:
    return _parse_signing_metadata(raw_metadata)


def _parse_signing_metadata(raw_metadata: Optional[str]) -> SigningMetadata:
    return _parse_json_metadata(raw_metadata, SigningMetadata)


def _parse_seal_metadata(raw_metadata: Optional[str]) -> ElectronicSealMetadata:
    return _parse_json_metadata(raw_metadata, ElectronicSealMetadata)


def _parse_stamp_metadata(raw_metadata: Optional[str]) -> StampMetadata:
    return _parse_json_metadata(raw_metadata, StampMetadata)


def _parse_signature_placeholders_metadata(
    raw_metadata: Optional[str],
) -> SignaturePlaceholdersMetadata:
    return _parse_json_metadata(raw_metadata, SignaturePlaceholdersMetadata)


def _parse_json_metadata(raw_metadata: Optional[str], model_cls):
    if raw_metadata is None or not raw_metadata.strip():
        return model_cls()
    try:
        return model_cls.model_validate_json(raw_metadata)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
