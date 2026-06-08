# CSC PDF Signing, Stamping And Electronic Seal Demo

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

The demo writes `artifacts/signed-demo.pdf`. The web UI is available at
`http://127.0.0.1:8100/` when the API is running.

## API

The demo UI is served at `/`.

- `GET /healthz` returns process health.
- `GET /readyz` verifies that the configured CSC credential can be fetched.
- `GET /readyz/seal` verifies that the electronic seal credential can be
  fetched. If no dedicated seal credential is configured, it falls back to the
  signing credential for demos.
- `POST /v1/pdf/page-image` renders one PDF page as `image/png` for visual
  placement previews. Form fields:
  - `pdf`: PDF file.
  - `page`: zero-based page index.
- `POST /v1/stamp/pdf` adds a text stamp and returns `application/pdf`.
- `POST /v1/signature-placeholders/pdf` adds one or more empty visible PDF
  signature fields for multi-signature workflows and returns
  `application/pdf`.
- `POST /v1/sign/pdf` accepts `multipart/form-data`:
  - `pdf`: PDF file.
  - `metadata`: optional JSON. It can include an optional `stamp` block to
    stamp the PDF before signing.
- `POST /v1/seal/pdf` applies a CSC-backed electronic seal and returns
  `application/pdf`. It accepts the same `pdf` form field and an optional
  `metadata` JSON body with seal-specific defaults.

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

Multi-signature placeholder metadata:

```json
{
  "empty_field_appearance": true,
  "sign_first": true,
  "sign_reason": "Semnare prima poziție",
  "sign_location": "București, România",
  "placeholders": [
    {
      "field_name": "Semnatar1",
      "box": {
        "page": 0,
        "x1": 72,
        "y1": 72,
        "x2": 190,
        "y2": 120
      }
    },
    {
      "field_name": "Semnatar2",
      "box": {
        "page": 0,
        "x1": 220,
        "y1": 72,
        "x2": 340,
        "y2": 120
      }
    }
  ]
}
```

When `sign_first` is `true`, the service creates all placeholder fields first
and then signs the first field in the `placeholders` array using the configured
CSC signer. Use `X-CSC-OAuth-Token` to pass a request-scoped CSC token.

Electronic seal metadata:

```json
{
  "field_name": "SigiliuElectronic1",
  "reason": "Sigiliu electronic instituțional",
  "location": "București, România",
  "signature_box": {
    "page": 0,
    "x1": 340,
    "y1": 142,
    "x2": 510,
    "y2": 227
  }
}
```

The web UI lets users place the stamp, visible signature, multi-signature
placeholders, and electronic seal visually on a rendered PDF page. UI
coordinates are edited in millimeters and converted to PDF points before
calling the API.

## Configuration

The signing service is configured with environment variables:

- `CSC_SERVICE_URL`, default `http://csc-dummy:9000`
- `CSC_API_VERSION`, default `v1`
- `CSC_CREDENTIAL_ID`, default `testing-ca/signer1-long`
- `CSC_SEAL_CREDENTIAL_ID`, optional. Defaults to `CSC_CREDENTIAL_ID` when
  omitted, which is useful for local demos only.
- `CSC_OAUTH_TOKEN`, optional fallback token
- `CSC_SEAL_OAUTH_TOKEN`, optional token for the electronic seal credential.
  Defaults to `CSC_OAUTH_TOKEN` when omitted.
- `SIGNING_TIMEOUT_SECONDS`, default `300`
- `MAX_PDF_MB`, default `25`
- `PDF_DIGEST_ALGORITHM`, default `sha256`

Requests can override the configured CSC OAuth token with
`X-CSC-OAuth-Token`. Electronic seal calls can use
`X-CSC-Seal-OAuth-Token`; if omitted, they fall back to `X-CSC-OAuth-Token`
and then to the configured environment token. In production, expose this
service only behind internal auth such as mTLS, a gateway, or trusted
service-to-service authentication.

## Production Notes

For production, deploy only `signing-api` and point `CSC_SERVICE_URL`,
`CSC_CREDENTIAL_ID`, `CSC_SEAL_CREDENTIAL_ID`, and OAuth handling at the real
CSC provider. The `csc-dummy` image intentionally omits production security
controls and binds a generated test keypair into a local CSC API.

The upstream `certomancer-csc` CLI binds to `localhost`, so this repo uses a
tiny wrapper that runs the same CSC app on `0.0.0.0` for container networking.
