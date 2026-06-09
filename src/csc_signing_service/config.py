from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_username: str = "admin"
    app_password: Optional[str] = None
    local_signing_enabled: bool = False
    local_signing_common_name: str = Field(
        default="CSC Demo Local Signer",
        min_length=1,
    )
    local_signing_valid_days: int = Field(default=3650, ge=1)
    csc_service_url: str = "http://csc-dummy:9000"
    csc_api_version: str = "v1"
    csc_credential_id: str = "testing-ca/signer1-long"
    csc_seal_credential_id: Optional[str] = None
    csc_oauth_token: Optional[str] = None
    csc_seal_oauth_token: Optional[str] = None
    signing_timeout_seconds: int = Field(default=300, ge=1)
    max_pdf_mb: int = Field(default=25, ge=1)
    pdf_digest_algorithm: str = "sha256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def max_pdf_bytes(self) -> int:
        return self.max_pdf_mb * 1024 * 1024

    def oauth_token_for_request(
        self,
        request_token: Optional[str] = None,
        *,
        for_seal: bool = False,
    ) -> Optional[str]:
        if for_seal:
            return request_token or self.csc_seal_oauth_token or self.csc_oauth_token
        return request_token or self.csc_oauth_token

    @property
    def seal_credential_id(self) -> str:
        return self.csc_seal_credential_id or self.csc_credential_id


@lru_cache
def get_settings() -> Settings:
    return Settings()
