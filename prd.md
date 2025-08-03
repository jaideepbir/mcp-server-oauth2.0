# Product Requirements Document (PRD)

## Project: MCP Server with OAuth2.0, OPA, and Streamlit Frontend

### 1. Goal
Build an MCP server that:
- Runs using Docker’s official Python image.
- Integrates OAuth2.0 via a dedicated Auth server container.
- Uses secure JWT with ID token and Access Token to drive authorization flows.
- Exposes two MCP tools:
  1) Excel/CSV Reader.
  2) OPA agent to evaluate admin vs user policies.
- Provides a Streamlit frontend with two pages:
  - Tools page: directly invoke Excel/CSV Reader and OPA Policy tool.
  - Chat page: chat with an LLM with MCP tool-calling.

### 2. Scope
In-scope
- Two Dockerized services:
  - mcp-server: Implements MCP protocol + tools.
  - auth-server: OAuth2 Authorization Server + JWT issuance (ID token + access token).
- Policy enforcement via OPA:
  - OPA sidecar or library-based evaluator invoked by the MCP server tool.
  - Policies define admin vs user capabilities for tool invocations.
- Streamlit web UI:
  - OAuth2 login flow.
  - Page 1: Direct tool access (upload/select files, run validations, see results).
  - Page 2: Chat UI with LLM integration and tool-calling capability via MCP.
- Secure token handling:
  - Frontend obtains tokens via Authorization Code w/ PKCE.
  - Streamlit passes bearer tokens to MCP server for authorization checks.
  - MCP server verifies tokens and uses OPA for fine-grained authz.
- Observability basics: structured logs for auth decisions and tool invocations.
- Local dev and docker-compose orchestration.

Out-of-scope (initial)
- Multi-tenant production scaling or external IdP integration.
- Persistent databases for users/sessions.
- Advanced RBAC beyond admin/user.

### 3. Architecture
Components
- Auth Server (Container)
  - OAuth2/OIDC provider issuing ID token and Access Token (JWT).
  - Endpoints: /.well-known/openid-configuration, /authorize, /token, /userinfo, /jwks.
  - Grant: Authorization Code with PKCE.
  - Signing keys: RS256.
  - User store: in-memory for dev.
- MCP Server (Container)
  - Implements MCP protocol over HTTP/WebSocket.
  - Registers tools:
    1) Excel/CSV Reader Tool.
    2) OPA Policy Eval Tool.
  - AuthN/AuthZ:
    - Verify JWT via JWKS from Auth Server.
    - Extract roles/claims from ID/Access tokens.
    - Use OPA for fine-grained policies.
- OPA Policy Engine
  - Preferred: Separate sidecar container with REST API.
  - Policies:
    - Tool invocation policies: admin vs user.
    - Resource policies: file path whitelist per role.
- Streamlit Frontend (Container)
  - Implements OAuth2 Authorization Code with PKCE.
  - Stores tokens in session state.
  - Page 1 “Tools”: upload/select files, run reader, test OPA.
  - Page 2 “Chat”: chat with LLM; MCP tool-calls enabled.
- LLM Provider
  - Pluggable via env: OpenAI-compatible or local.

Data flows
- Login: Streamlit → Auth /authorize → code → /token → ID + Access Token → session.
- Tool Invocation: Streamlit → MCP (Bearer) → verify → OPA → execute/deny.
- Chat: Streamlit ↔ LLM via MCP; tool-calls authorized by OPA.

### 4. Functional Requirements
Auth Server
- OIDC discovery, JWKS, RS256 JWT.
- Scopes: openid, profile, email, mcp.tools.
- Custom claim: role.

MCP Server
- Expose MCP protocol endpoints and tools:
  - Tool: excel_csv_reader
    - Inputs: source (upload_id or path), format_hint (csv/xlsx/auto), sheet?, columns?, max_rows?, summary? (bool).
    - Outputs: rows/summary; errors on invalid file/format/permission.
  - Tool: opa_policy_eval
    - Inputs: action, resource, context (claims), policy_path?.
    - Outputs: allow (bool), reason, matched_rule.
- Validate Bearer token on every call.
- Call OPA with inputs: subject (claims), action, resource.
- Log decisions and denials.

OPA
- Load policy bundle on startup.
- Expose REST API for queries.
- Policies example:
  - Admins can use all tools and read all files.
  - Users can only read files in /data/public or uploads they own.

Streamlit
- OAuth2 Authorization Code with PKCE.
- Store tokens in session state; no refresh initially.
- Tools page: upload CSV/XLSX, invoke reader; run OPA tool.
- Chat page: chat UI; LLM responses; tool-call traces; auth errors visible.

### 5. Non-Functional Requirements
Security
- RS256 JWTs; validate iss, aud, exp, nbf; least-privilege policies.
Performance
- Read files up to ~25MB; default max_rows 1,000; policy eval <500ms; file read <2s typical.
Reliability
- Graceful error handling; health endpoints.
Observability
- Structured logs (JSON), correlation IDs; basic metrics.

### 6. API/Interfaces
Auth Server
- /.well-known/openid-configuration, /authorize, /token, /userinfo, /jwks
MCP Server
- /mcp (HTTP/WebSocket), /healthz
OPA
- POST /v1/data/<package>/<rule>
Streamlit
- / (home), /tools, /chat, /oauth/callback

### 7. Policies (Rego example)
```
package mcp.authz

default allow = false

allow {
  input.subject.role == "admin"
}

allow {
  input.subject.role == "user"
  input.action == "excel.read"
  startswith(input.resource.path, "/data/public")
}
```

### 8. Configuration
Environment variables
- AUTH_ISSUER_URL, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET, AUTH_REDIRECT_URI, JWT_AUDIENCE
- OPA_URL, LLM_API_BASE, LLM_API_KEY
- DATA_DIR=/data, STREAMLIT_SERVER_PORT=8501

Docker images
- python:3.11-slim; openpolicyagent/opa:latest

### 9. Dev/Build/Run
- docker-compose: services auth-server, mcp-server, opa, streamlit
- Networks: internal; Volumes: data dir, uploads
- Make targets: up/down/logs; seed sample policies/data

### 10. Testing
Unit
- JWT verification, OPA client/policies, Excel/CSV parsing
Integration
- OAuth login flow; tool invocations admin vs user
E2E
- Streamlit Tools and Chat flows

### 11. Risks & Mitigations
- OAuth complexity → use reliable libs; minimal flows
- Token leakage → never log tokens; redact secrets
- LLM tool-calling safety → strict validation; OPA checks before execution

### 12. Milestones
- M1: Boilerplate & docker-compose; PRD committed
- M2: Auth server OIDC operational
- M3: MCP server skeleton with JWT verify
- M4: OPA sidecar wired with base policies
- M5: Excel/CSV reader end-to-end
- M6: OPA policy tool end-to-end
- M7: Streamlit Tools page with OAuth + tools
- M8: Streamlit Chat page with LLM + tool-calls
- M9: Tests and docs
