from csc_signing_service.config import Settings


def test_settings_defaults():
    settings = Settings(_env_file=None)

    assert settings.csc_service_url == "http://csc-dummy:9000"
    assert settings.csc_api_version == "v1"
    assert settings.csc_credential_id == "testing-ca/signer1-long"
    assert settings.seal_credential_id == "testing-ca/signer1-long"
    assert settings.max_pdf_bytes == 25 * 1024 * 1024


def test_request_oauth_token_overrides_env_token():
    settings = Settings(csc_oauth_token="env-token", _env_file=None)

    assert settings.oauth_token_for_request("request-token") == "request-token"
    assert settings.oauth_token_for_request() == "env-token"


def test_seal_credential_and_token_can_be_configured_separately():
    settings = Settings(
        csc_oauth_token="sign-token",
        csc_seal_oauth_token="seal-token",
        csc_seal_credential_id="testing-ca/institution-seal",
        _env_file=None,
    )

    assert settings.seal_credential_id == "testing-ca/institution-seal"
    assert settings.oauth_token_for_request(for_seal=True) == "seal-token"
    assert (
        settings.oauth_token_for_request("request-token", for_seal=True)
        == "request-token"
    )


def test_seal_token_falls_back_to_signing_token():
    settings = Settings(csc_oauth_token="sign-token", _env_file=None)

    assert settings.oauth_token_for_request(for_seal=True) == "sign-token"
