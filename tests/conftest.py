from io import BytesIO

import pytest
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 720, "Test PDF")
    pdf.showPage()
    pdf.save()
    return output.getvalue()
