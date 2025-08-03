# Chat History Export

This file captures the recent conversation and key actions taken while building the MCP server project with OAuth, OPA, and Streamlit.

---

## Timeline

- Initialize repo and write PRD for MCP server with OAuth2.0, OPA, and Streamlit UI.
- Commit PRD; enforce Conventional Commits via commit-msg hook.
- Add docs: dependencies and inventory, architecture diagram (diagrams-as-code), and dataflow.
- Install Graphviz, render and export architecture PNG via diagrams.mingrammer.com.
- Scaffold Docker Compose stack:
  - Services: auth-server (FastAPI), mcp-server (FastAPI), opa, streamlit.
  - OPA policies for admin/user.
  - Streamlit 2 pages: Tools & Chat.
- Docker Desktop issues resolved; build and run containers.
- Health checks:
  - Auth: http://localhost:8001/healthz
  - MCP: http://localhost:9000/healthz
  - OPA: http://localhost:8181
  - Streamlit: http://localhost:8501
- Implement Excel/CSV reader, OPA tool, and token mapping:
  - `Bearer admin-key` → role=admin (rw)
  - `Bearer demo-key` → role=user (r)
- Streamlit Tools UI improvements:
  - Initially JSON toggle; later replaced with tabs (Table, JSON).
  - Styled decisions, rights display.
- Add Upload flow:
  - Upload CSV to MCP `/mcp/upload` (saved under `/data/uploads`).
  - Read via `excel_csv_reader` using relative path.
- Fixes:
  - OPA image tag pinned to multi-arch (e.g., `openpolicyagent/opa:0.67.1`).
  - Retry/backoff and better error handling between MCP and OPA.
  - Ensure `MCP_SERVER_URL` available for Streamlit container.
- Remote repository created and pushed:  
  https://github.com/jaideepbir/mcp-server-oauth2.0

---

## Key Errors & Resolutions

1) Streamlit diagram export error:
   - `ModuleNotFoundError: No module named 'diagrams'`
   - Resolution: Install `diagrams` and `graphviz` in venv; install Graphviz system binary via Homebrew.

2) OPA platform/timeouts on Apple Silicon:
   - `httpx.ConnectTimeout` connecting to `http://opa:8181`
   - Resolution: Pin OPA image to multi-arch tag (`openpolicyagent/opa:0.67.1`) and add retry/backoff in MCP server.

3) Streamlit/mcp-server DNS timeout:
   - ConnectTimeout to `mcp-server:9000`
   - Resolution: Ensure `MCP_SERVER_URL=http://mcp-server:9000` set in Streamlit environment; rebuild and restart. Add timeout/retry logic as needed.

4) NameError in Streamlit:
   - `NameError: name 'source' is not defined` in `1_Tools.py` when mode is "Upload"
   - Resolution: Initialize resource defaults safely based on mode; rebuild streamlit.

5) Default sample not loading/upload freezing:
   - Confirmed container paths and OPA allow rules.
   - Ensured `/data/public/sample.csv` exists and read allowed for user.
   - Upload requires admin-key (write); reading uploads path allowed for user.

---

## Test Commands

Direct MCP read (host):
```
curl -s -X POST http://localhost:9000/mcp/tools/excel_csv_reader \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{"source":"public/sample.csv","max_rows":5}'
```

Upload (host):
```
curl -s -X POST http://localhost:9000/mcp/upload \
  -H "Authorization: Bearer admin-key" \
  -F "file=@data/public/sample.csv"
```

Read uploaded file (host):
```
curl -s -X POST http://localhost:9000/mcp/tools/excel_csv_reader \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{"source":"uploads/sample.csv","max_rows":5}'
```

Container checks:
```
docker compose -f compose/docker-compose.yml exec mcp-server sh -c 'ls -l /data/public && ls -l /data/uploads || true'
docker compose -f compose/docker-compose.yml logs --tail=200 mcp-server
docker compose -f compose/docker-compose.yml exec streamlit sh -c 'echo $MCP_SERVER_URL'
```

---

## Current UI Behavior

- Tools page:
  - Access Token: `Bearer admin-key` (rw) or `Bearer demo-key` (r)
  - Select source: Default or Upload
    - Default: choose a default file and click “Read File”
    - Upload: choose a CSV and click “Upload & Read” (admin-key required for write)
  - Results appear in tabs: Table (default) and JSON
  - OPA eval shows decision and rights:
    - admin-key → rights: `rw` (ALLOW everywhere)
    - demo-key → rights: `r` (ALLOW under `/data/public` and uploads read)
- Chat page:
  - LLM stubs and tool-call integration (future expansions planned)

---

## Next Steps

- Surface clearer errors in UI for user vs admin actions (e.g., upload denied for demo-key).
- Add default file dropdown population from `/data/public` dynamically.
- Expand OPA policies for DB/table resources (schema/table-based decisions).
- Add CI/CD, tests (unit/integration), and more robust logging/metrics.

---

## Repo

- GitHub: https://github.com/jaideepbir/mcp-server-oauth2.0
