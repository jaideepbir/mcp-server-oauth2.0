# Dependencies, Inventory, and Folder Structure

## Dependencies

### Runtime
- Python 3.11 (Docker base: python:3.11-slim)
- Streamlit >= 1.32
- FastAPI or Litestar (for MCP + Auth servers; FastAPI assumed)
- Uvicorn (ASGI server)
- Authlib (OAuth2/OIDC provider & client)
- PyJWT (JWT handling) or authlib.jwt
- python-jose[cryptography] (JWT verification) — optional if using Authlib
- requests/httpx (HTTP client)
- pandas (CSV/XLSX parsing)
- openpyxl (XLSX engine)
- pyarrow (optional; accelerate CSV/Parquet)
- pydantic (schema validation)
- orjson/ujson (fast JSON) — optional
- loguru/structlog (structured logging)
- tenacity (retries)

### Policy Engine
- OPA container: openpolicyagent/opa:latest
- Rego policy bundles in repo under `policies/`

### LLM Integration (pluggable)
- openai (or compatible client, e.g., `openai`/`litellm`)

### Dev/Test
- pytest, pytest-asyncio
- httpx[http2]
- ruff/flake8 + black/isort
- mypy (optional)

### Container/Orchestration
- Docker, docker-compose

## Inventory

### Services
- auth-server: OAuth2/OIDC provider issuing ID/Access tokens
- mcp-server: MCP protocol server exposing tools
  - Tools:
    - excel_csv_reader
    - opa_policy_eval
- opa: OPA sidecar
- streamlit: UI with two pages (Tools, Chat)

### Endpoints
- Auth: /.well-known/openid-configuration, /authorize, /token, /userinfo, /jwks
- MCP: /mcp (WS/HTTP), /healthz
- OPA: /v1/data/mcp/authz/allow (example)
- Streamlit: /tools, /chat, /oauth/callback

### Config (env vars)
- AUTH_ISSUER_URL, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET, AUTH_REDIRECT_URI, JWT_AUDIENCE
- OPA_URL
- LLM_API_BASE, LLM_API_KEY
- DATA_DIR, STREAMLIT_SERVER_PORT

### Data
- Sample CSV/XLSX under `data/public/`
- Uploaded files under `data/uploads/` (per-user scoping)

## Suggested Folder Structure

```
projects/mcp-server-oauth2.0/
├─ prd.md
├─ docs/
│  ├─ dependencies-and-inventory.md
│  ├─ architecture-diagram.md
│  └─ dataflow.py                 # Diagrams as code (mingrammer/diagrams)
├─ compose/
│  └─ docker-compose.yml
├─ services/
│  ├─ auth-server/
│  │  ├─ app/
│  │  │  ├─ main.py
│  │  │  ├─ routes/
│  │  │  ├─ security/
│  │  │  └─ models/
│  │  ├─ requirements.txt
│  │  └─ Dockerfile
│  ├─ mcp-server/
│  │  ├─ app/
│  │  │  ├─ main.py
│  │  │  ├─ mcp/
│  │  │  │  ├─ tools/
│  │  │  │  │  ├─ excel_csv_reader.py
│  │  │  │  │  └─ opa_policy_eval.py
│  │  │  │  └─ protocol.py
│  │  │  ├─ auth/
│  │  │  ├─ clients/
│  │  │  └─ utils/
│  │  ├─ requirements.txt
│  │  └─ Dockerfile
│  ├─ opa/
│  │  ├─ policies/
│  │  │  └─ mcp/
│  │  │     └─ authz.rego
│  │  └─ Dockerfile (optional; can use official image directly)
│  └─ streamlit/
│     ├─ app/
│     │  ├─ pages/
│     │  │  ├─ 1_Tools.py
│     │  │  └─ 2_Chat.py
│     │  ├─ auth/
│     │  └─ mcp_client/
│     ├─ requirements.txt
│     └─ Dockerfile
├─ data/
│  ├─ public/
│  └─ uploads/  # gitignored
├─ scripts/
│  ├─ dev_up.sh
│  ├─ dev_down.sh
│  └─ seed_data.sh
├─ .env.example
├─ .gitignore
└─ Makefile
```

## Notes
- Keep `data/uploads/` out of git via .gitignore.
- Use `.env.example` to document required env vars.
- Consider `ruff` + `black` pre-commit hooks.
