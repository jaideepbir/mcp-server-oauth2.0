# python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Auth Server (DEV)")

@app.get("/.well-known/openid-configuration")
def discovery():
    return {
        "issuer": "http://auth-server:8000",
        "jwks_uri": "http://auth-server:8000/jwks",
        "authorization_endpoint": "http://auth-server:8000/authorize",
        "token_endpoint": "http://auth-server:8000/token",
        "userinfo_endpoint": "http://auth-server:8000/userinfo",
        "scopes_supported": ["openid", "profile", "email", "mcp.tools"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
    }

@app.get("/jwks")
def jwks():
    # Placeholder JWKS for scaffolding; will be replaced with real keys
    return {"keys": []}

@app.get("/healthz")
def health():
    return JSONResponse({"status": "ok"})
