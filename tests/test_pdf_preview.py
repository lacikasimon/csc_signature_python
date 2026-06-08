from csc_signing_service.pdf_preview import render_pdf_page


def test_render_pdf_page_returns_png_and_dimensions(sample_pdf_bytes):
    preview = render_pdf_page(sample_pdf_bytes, page_index=0)

    assert preview.image_bytes.startswith(b"\x89PNG")
    assert preview.page_count == 1
    assert preview.page_index == 0
    assert preview.page_width > 0
    assert preview.page_height > 0
