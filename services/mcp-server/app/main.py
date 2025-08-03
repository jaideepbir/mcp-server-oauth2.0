# python
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx
import os

from .mcp.tools.excel_csv_reader import read_csv
from .mcp.tools.opa_policy_eval import evaluate as opa_evaluate

AUTH_ISSUER_URL = os.environ.get("AUTH_ISSUER_URL", "http://auth-server:8000")
OPA_URL = os.environ.get("OPA_URL", "http://opa:8181")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "mcp-audience")
DATA_DIR = os.environ.get("DATA_DIR", "/data")

app = FastAPI(title="MCP Server (DEV)")

async def verify_bearer_token(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    # TODO: validate JWT via JWKS from AUTH_ISSUER_URL
    return {"sub": "user-123", "role": "admin", "token": token}

async def opa_allow(subject: dict, action: str, resource: dict):
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.post(
            f"{OPA_URL}/v1/data/mcp/authz/allow",
            json={"input": {"subject": subject, "action": action, "resource": resource}},
        )
    if resp.status_code != 200:
        return False, {"reason": f"OPA error {resp.status_code}"}
    data = resp.json()
    allowed = data.get("result") is True or data.get("result", {}).get("allow") is True
    return allowed, data

@app.get("/healthz")
async def health():
    return JSONResponse({"status": "ok"})

@app.post("/mcp/tools/excel_csv_reader")
async def excel_csv_reader(payload: dict, subject=Depends(verify_bearer_token)):
    source = payload.get("source")
    max_rows = int(payload.get("max_rows", 1000))
    resource = {"path": os.path.join(DATA_DIR, source or "")}
    allowed, _ = await opa_evaluate(OPA_URL, subject, "excel.read", resource)
    if not allowed:
        raise HTTPException(status_code=403, detail="Forbidden by policy")
    rows = read_csv(resource["path"], max_rows=max_rows)
    return {"rows": rows, "count": len(rows)}

@app.post("/mcp/tools/opa_policy_eval")
async def opa_policy_eval(payload: dict, subject=Depends(verify_bearer_token)):
    action = payload.get("action")
    resource = payload.get("resource", {})
    allowed, data = await opa_evaluate(OPA_URL, subject, action or "", resource)
    return {"allow": allowed, "engine": data}
