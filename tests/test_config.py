from csc_signing_service.config import Settings


def test_settings_defaults():
    settings = Settings(_env_file=None)

    assert settings.csc_service_url == "http://csc-dummy:9000"
    assert settings.csc_api_version == "v1"
    assert settings.csc_credential_id == "testing-ca/signer1-long"
    assert settings.max_pdf_bytes == 25 * 1024 * 1024


def test_request_oauth_token_overrides_env_token():
    settings = Settings(csc_oauth_token="env-token", _env_file=None)

    assert settings.oauth_token_for_request("request-token") == "request-token"
    assert settings.oauth_token_for_request() == "env-token"
