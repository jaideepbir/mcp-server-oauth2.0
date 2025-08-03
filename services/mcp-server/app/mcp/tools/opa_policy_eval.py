# python
from typing import Any, Tuple
import httpx
import asyncio

async def evaluate(opa_url: str, subject: dict, action: str, resource: dict, retries: int = 3, timeout: float = 2.0) -> Tuple[bool, Any]:
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{opa_url}/v1/data/mcp/authz/allow",
                    json={"input": {"subject": subject, "action": action, "resource": resource}},
                )
            if resp.status_code == 200:
                data = resp.json()
                # Normalize result to include rights if provided by policy
                result = data.get("result")
                if isinstance(result, dict):
                    allowed = bool(result.get("allow", False)) or result == {}
                else:
                    allowed = bool(result)
                # Rights from policy (rights field) if present
                rights = None
                if isinstance(result, dict) and "rights" in result:
                    rights = result["rights"]
                return allowed, {"result": result, "rights": rights}
            return False, {"reason": f"OPA HTTP {resp.status_code}", "body": resp.text}
        except (httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
            last_exc = exc
            await asyncio.sleep(0.2 * attempt)
        except httpx.HTTPError as exc:
            return False, {"reason": f"OPA HTTP error: {exc}"}
    return False, {"reason": f"OPA unreachable after {retries} attempts", "error": str(last_exc)}
