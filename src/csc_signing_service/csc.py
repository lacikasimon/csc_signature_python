import asyncio
from typing import List

import aiohttp
from pyhanko.sign.general import SigningError
from pyhanko.sign.signers.csc_signer import (
    CSCAuthorizationInfo,
    CSCAuthorizationManager,
    CSCServiceSessionInfo,
)

from .errors import CSCProviderError, CSCProviderTimeoutError


class HashPinnedCSCAuthManager(CSCAuthorizationManager):
    """CSC authorization manager that always binds SAD to pyHanko hashes."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        csc_session_info: CSCServiceSessionInfo,
        credential_info,
        request_timeout: int,
    ):
        self.session = session
        self.request_timeout = request_timeout
        super().__init__(
            csc_session_info=csc_session_info,
            credential_info=credential_info,
        )

    async def authorize_signature(
        self, hash_b64s: List[str]
    ) -> CSCAuthorizationInfo:
        request_body = self.format_csc_auth_request(hash_b64s=hash_b64s)
        url = self.csc_session_info.endpoint_url("credentials/authorize")

        try:
            async with self.session.post(
                url,
                headers=self.auth_headers,
                json=request_body,
                raise_for_status=True,
                timeout=self.request_timeout,
            ) as response:
                response_data = await response.json()
        except asyncio.TimeoutError as exc:
            raise CSCProviderTimeoutError(
                "CSC credentials/authorize request timed out"
            ) from exc
        except aiohttp.ClientResponseError as exc:
            raise CSCProviderError(
                "CSC credentials/authorize request failed "
                f"with HTTP {exc.status}"
            ) from exc
        except (aiohttp.ClientError, ValueError) as exc:
            raise CSCProviderError(
                "CSC credentials/authorize response could not be processed"
            ) from exc

        try:
            return self.parse_csc_auth_response(response_data)
        except SigningError as exc:
            raise CSCProviderError(
                "CSC credentials/authorize response did not contain usable SAD"
            ) from exc
