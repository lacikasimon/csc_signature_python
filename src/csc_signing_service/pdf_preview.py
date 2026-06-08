from dataclasses import dataclass

import fitz

from .errors import InvalidPDFError


@dataclass(frozen=True)
class PagePreview:
    image_bytes: bytes
    page_count: int
    page_index: int
    page_width: float
    page_height: float


def render_pdf_page(
    pdf_bytes: bytes,
    page_index: int = 0,
    scale: float = 2.0,
) -> PagePreview:
    if not pdf_bytes:
        raise InvalidPDFError("PDF upload is empty")
    if not pdf_bytes.startswith(b"%PDF-"):
        raise InvalidPDFError("PDF upload does not start with a PDF header")
    if page_index < 0:
        raise InvalidPDFError("Page index must be zero or greater")

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            page_count = document.page_count
            if page_count == 0:
                raise InvalidPDFError("PDF does not contain pages")
            if page_index >= page_count:
                raise InvalidPDFError("Requested page does not exist")

            page = document.load_page(page_index)
            page_rect = page.rect
            matrix = fitz.Matrix(scale, scale)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            return PagePreview(
                image_bytes=pixmap.tobytes("png"),
                page_count=page_count,
                page_index=page_index,
                page_width=page_rect.width,
                page_height=page_rect.height,
            )
    except InvalidPDFError:
        raise
    except (fitz.FileDataError, fitz.EmptyFileError, RuntimeError) as exc:
        raise InvalidPDFError("Input is not a readable PDF") from exc
