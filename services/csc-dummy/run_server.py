import os

from aiohttp import web
from certomancer import registry
from csc_dummy.csc_dummy_server import CSCWithCertomancer, DummyServiceParams


def main() -> None:
    config_path = os.getenv("CERTOMANCER_CONFIG", "/app/certomancer.yml")
    port = int(os.getenv("PORT", "9000"))
    host = os.getenv("HOST", "0.0.0.0")
    scal = os.getenv("CSC_SCAL", "2")

    config = registry.CertomancerConfig.from_file(config_path)
    csc_app = CSCWithCertomancer(
        config,
        service_params=DummyServiceParams(hash_pinning_required=scal == "2"),
    )
    csc_app.register_routes()
    web.run_app(csc_app.app, host=host, port=port)


if __name__ == "__main__":
    main()
