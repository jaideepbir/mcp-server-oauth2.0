# Architecture & Dataflow

This document describes the high-level architecture and the dataflow across services. Diagrams are generated using `mingrammer/diagrams` in `docs/dataflow.py`.

## Components
- Auth Server: OAuth2/OIDC provider issuing ID & Access tokens (JWT, RS256)
- MCP Server: Implements MCP protocol and tools (excel_csv_reader, opa_policy_eval)
- OPA: Policy decision point (Rego policies)
- Streamlit: Frontend with Tools page and Chat page
- LLM API: Pluggable (OpenAI-compatible)

## Dataflow Scenarios

1) Login (Authorization Code with PKCE)
- Streamlit → Auth Server /authorize
- Redirect back to Streamlit with code
- Streamlit → Auth Server /token → ID token + Access Token (JWT)

2) Tool Invocation (Tools page)
- Streamlit → MCP Server (Bearer access token)
- MCP Server → JWKS from Auth Server to validate JWT (cached)
- MCP Server → OPA with input {subject, action, resource}
- If allow:
  - excel_csv_reader: reads CSV/XLSX from /data/public or /data/uploads (per policy)
  - Returns rows/summary
- Else: deny with reason

3) Chat with LLM and Tool-Calling (Chat page)
- Streamlit ↔ MCP Server: chat messages
- MCP Server ↔ LLM Provider: responses, tool-use suggestions
- On tool-call:
  - MCP Server performs the same authZ check via OPA before execution

See `docs/dataflow.py` to render PNG diagrams.
