import os

import httpx
import pytest
from pyhanko.pdf_utils.reader import PdfFileReader

from csc_signing_service.demo_client import generate_sample_pdf


@pytest.mark.skipif(
    not os.getenv("LIVE_SIGNING_API_URL"),
    reason="set LIVE_SIGNING_API_URL to run live signing integration tests",
)
def test_live_signing_api_signs_pdf(tmp_path):
    api_url = os.environ["LIVE_SIGNING_API_URL"].rstrip("/")
    output_path = tmp_path / "signed.pdf"

    with httpx.Client(timeout=300) as client:
        ready = client.get(f"{api_url}/readyz")
        ready.raise_for_status()
        response = client.post(
            f"{api_url}/v1/sign/pdf",
            files={
                "pdf": ("input.pdf", generate_sample_pdf(), "application/pdf")
            },
            data={
                "metadata": (
                    '{"stamp": {"text": "Live integration stamp", '
                    '"x": 72, "y": 72, "width": 220, "height": 60}}'
                )
            },
        )
        response.raise_for_status()

    output_path.write_bytes(response.content)
    with output_path.open("rb") as inf:
        reader = PdfFileReader(inf)
        assert len(reader.embedded_signatures) == 1
        assert reader.embedded_signatures[0].field_name == "Signature1"
