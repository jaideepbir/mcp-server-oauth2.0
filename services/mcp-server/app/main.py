# python
from fastapi import FastAPI, Depends, HTTPException, Header, status, UploadFile, File
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

UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

async def verify_bearer_token(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    role = "user"
    sub = "" # Initialize sub
    if token == "admin-key":
        role = "admin"
        sub = "admin-subject"
    elif token == "demo-key":
        role = "user"
        sub = "demo" # Set sub to "demo" for demo-key to match streamlit's owner logic
    else:
        sub = f"{role}-subject" # Default for other roles/tokens
    # TODO: replace with real JWT validation later
    return {"sub": sub, "role": role, "token": token}

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
    print(f"excel_csv_reader: Received request with payload: {payload} and subject: {subject}")
    source = payload.get("source")
    if not source:
        raise HTTPException(status_code=400, detail="Missing 'source' path relative to DATA_DIR")
    max_rows = int(payload.get("max_rows", 1000))
    owner = payload.get("owner", "")
    resource = {"path": os.path.join(DATA_DIR, source), "owner": owner}
    print(f"excel_csv_reader: Evaluating OPA for action 'excel.read' on resource: {resource}")
    allowed, details = await opa_evaluate(OPA_URL, subject, "excel.read", resource)
    print(f"excel_csv_reader: OPA evaluation result: allowed={allowed}, details={details}")
    # Rights if present in details
    rights = None
    if isinstance(details, dict):
        rights = details.get("rights") or (details.get("result", {}) if isinstance(details.get("result"), dict) else {}).get("rights")
    if not allowed and isinstance(details, dict) and str(details.get("reason", "")).startswith("OPA unreachable"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=details)
    if not allowed:
        raise HTTPException(status_code=403, detail=details)
    path = resource["path"]
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail=f"File not found: {path}")
    print(f"excel_csv_reader: Reading CSV from path: {path}")
    rows = read_csv(path, max_rows=max_rows)
    print(f"excel_csv_reader: Successfully read {len(rows)} rows.")
    return {"rights": rights, "rows": rows, "count": len(rows)}

@app.post("/mcp/tools/opa_policy_eval")
async def opa_policy_eval(payload: dict, subject=Depends(verify_bearer_token)):
    action = payload.get("action")
    resource = payload.get("resource", {})
    allowed, data = await opa_evaluate(OPA_URL, subject, action or "", resource)
    rights = None
    if isinstance(data, dict):
        rights = data.get("rights") or (data.get("result", {}) if isinstance(data.get("result"), dict) else {}).get("rights")
    if not allowed and isinstance(data, dict) and str(data.get("reason", "")).startswith("OPA unreachable"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=data)
    return {"allow": allowed, "rights": rights, "engine": data}

@app.post("/mcp/upload")
async def upload_file(file: UploadFile = File(...), subject=Depends(verify_bearer_token)):
    print(f"upload_file: Received upload request for file: {file.filename} with subject: {subject}")
    dest_path = os.path.join(UPLOADS_DIR, file.filename)
    owner = subject.get("sub", "") # Get owner from subject
    resource = {"path": dest_path, "owner": owner}
    print(f"upload_file: Evaluating OPA for action 'excel.write' on resource: {resource}")
    allowed, details = await opa_evaluate(OPA_URL, subject, "excel.write", resource)
    print(f"upload_file: OPA evaluation result: allowed={allowed}, details={details}")
    if not allowed: # Removed the redundant subject.get("role") != "admin" check as OPA should handle it
        raise HTTPException(status_code=403, detail=details) # Return OPA details for better debugging
    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)
    print(f"upload_file: Successfully wrote file to: {dest_path}")
    # Return relative path from DATA_DIR for downstream tool
    rel = os.path.relpath(dest_path, DATA_DIR)
    return {"relative_path": rel, "size": len(content)}
