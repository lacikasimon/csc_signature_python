from types import SimpleNamespace

import pytest
from pyhanko.sign.signers.csc_signer import CSCServiceSessionInfo

from csc_signing_service.csc import HashPinnedCSCAuthManager


class DummyResponse:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def json(self):
        return {"SAD": "sad-token"}


class DummySession:
    def __init__(self):
        self.last_request = None

    def post(self, url, headers, json, raise_for_status, timeout):
        self.last_request = {
            "url": url,
            "headers": headers,
            "json": json,
            "raise_for_status": raise_for_status,
            "timeout": timeout,
        }
        return DummyResponse()


@pytest.mark.asyncio
async def test_authorize_signature_posts_hash_pinned_request():
    session = DummySession()
    session_info = CSCServiceSessionInfo(
        service_url="http://csc.example",
        credential_id="testing-ca/signer1-long",
        oauth_token="token",
        api_ver="v1",
    )
    credential_info = SimpleNamespace(hash_pinning_required=True)
    manager = HashPinnedCSCAuthManager(
        session=session,
        csc_session_info=session_info,
        credential_info=credential_info,
        request_timeout=12,
    )

    auth_info = await manager.authorize_signature(["abc123"])

    assert auth_info.sad == "sad-token"
    assert session.last_request["url"] == (
        "http://csc.example/csc/v1/credentials/authorize"
    )
    assert session.last_request["headers"] == {
        "Authorization": "Bearer token"
    }
    assert session.last_request["json"]["credentialID"] == (
        "testing-ca/signer1-long"
    )
    assert session.last_request["json"]["numSignatures"] == 1
    assert session.last_request["json"]["hash"] == ["abc123"]
    assert session.last_request["raise_for_status"] is True
    assert session.last_request["timeout"] == 12
