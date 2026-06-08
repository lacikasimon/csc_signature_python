# CSC PDF Signing Demo

FastAPI + pyHanko service for PDF signing through a CSC-compatible remote
signing provider. The Compose setup includes a local demo CSC server backed by
`certomancer-csc-dummy`; that container is only for demos and tests, never for
production keys.

## Run The Demo

```bash
docker compose up --build csc-dummy signing-api
```

In another terminal:

```bash
docker compose --profile demo run --rm demo-client
```

The demo writes `artifacts/signed-demo.pdf`.

## API

The demo UI is served at `/`.

- `GET /healthz` returns process health.
- `GET /readyz` verifies that the configured CSC credential can be fetched.
- `POST /v1/pdf/page-image` renders one PDF page as `image/png` for visual
  placement previews. Form fields:
  - `pdf`: PDF file.
  - `page`: zero-based page index.
- `POST /v1/stamp/pdf` adds a text stamp and returns `application/pdf`.
- `POST /v1/sign/pdf` accepts `multipart/form-data`:
  - `pdf`: PDF file.
  - `metadata`: optional JSON. It can include an optional `stamp` block to
    stamp the PDF before signing.

Default metadata:

```json
{
  "field_name": "Signature1",
  "reason": "Demo CSC signing",
  "location": null,
  "signature_box": null,
  "stamp": null
}
```

`signature_box` is optional. When present, it creates a visible signature field
using pyHanko's zero-based page index:

```json
{
  "signature_box": {
    "page": 0,
    "x1": 72,
    "y1": 72,
    "x2": 260,
    "y2": 140
  }
}
```

Standalone stamp metadata:

```json
{
  "text": "Reviewed %(ts)s",
  "page": 0,
  "x": 72,
  "y": 72,
  "width": 220,
  "height": 60,
  "font_size": 10,
  "background_opacity": 0.35,
  "border_width": 1,
  "text_color": "#0b3b82",
  "border_color": "#0b3b82"
}
```

## Configuration

The signing service is configured with environment variables:

- `CSC_SERVICE_URL`, default `http://csc-dummy:9000`
- `CSC_API_VERSION`, default `v1`
- `CSC_CREDENTIAL_ID`, default `testing-ca/signer1-long`
- `CSC_OAUTH_TOKEN`, optional fallback token
- `SIGNING_TIMEOUT_SECONDS`, default `300`
- `MAX_PDF_MB`, default `25`
- `PDF_DIGEST_ALGORITHM`, default `sha256`

Requests can override the configured CSC OAuth token with
`X-CSC-OAuth-Token`. In production, expose this service only behind internal
auth such as mTLS, a gateway, or trusted service-to-service authentication.

## Production Notes

For production, deploy only `signing-api` and point `CSC_SERVICE_URL`,
`CSC_CREDENTIAL_ID`, and OAuth handling at the real CSC provider. The
`csc-dummy` image intentionally omits production security controls and binds a
generated test keypair into a local CSC API.

The upstream `certomancer-csc` CLI binds to `localhost`, so this repo uses a
tiny wrapper that runs the same CSC app on `0.0.0.0` for container networking.
