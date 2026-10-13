import hmac
import sys

import uvicorn
from starlette.responses import JSONResponse

import config
from audit import log_call
from server import mcp


class TokenAuth:
    """Reject every HTTP request that lacks the correct bearer token."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            supplied = dict(scope["headers"]).get(b"authorization", b"")
            expected = f"Bearer {config.MCP_TOKEN}".encode()
            if not hmac.compare_digest(supplied, expected):  # constant-time compare
                log_call("auth_failed", scope.get("path", "?"))
                response = JSONResponse({"error": "unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


app = TokenAuth(mcp.streamable_http_app())

if __name__ == "__main__":
    if len(config.MCP_TOKEN) < 20:
        sys.exit("MCP_TOKEN is missing or too short. Set it in .env (see .env.example).")
    uvicorn.run(app, host="127.0.0.1", port=config.PORT)