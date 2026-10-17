import hashlib
import hmac
import sys

import uvicorn
from starlette.responses import JSONResponse

import config
from audit import log_call
from server import mcp


def _fp(text: str) -> str:
    """Short fingerprint so we can compare tokens without revealing them."""
    return hashlib.sha256(text.encode()).hexdigest()[:8]


class TokenAuth:
    """Reject every HTTP request that lacks the correct bearer token."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            raw = dict(scope["headers"]).get(b"authorization", b"")
            expected = f"Bearer {config.MCP_TOKEN}".encode()
            if not hmac.compare_digest(raw, expected):  # constant-time compare
                supplied = raw.decode("latin-1")
                scheme, _, tok = supplied.partition(" ")
                log_call(
                    "auth_failed",
                    f"{scope.get('method')} {scope.get('path')} "
                    f"header_len={len(supplied)} scheme={scheme!r} "
                    f"got_fp={_fp(tok) if tok else 'none'} want_fp={_fp(config.MCP_TOKEN)}",
                )
                response = JSONResponse({"error": "unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


app = TokenAuth(mcp.streamable_http_app())

if __name__ == "__main__":
    if len(config.MCP_TOKEN) < 20:
        sys.exit("MCP_TOKEN is missing or too short. Set it in .env (see .env.example).")
    uvicorn.run(app, host="127.0.0.1", port=config.PORT)