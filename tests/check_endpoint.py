import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import config

url = sys.argv[1] if len(sys.argv) > 1 else f"http://127.0.0.1:{config.PORT}/mcp"
base = {"Accept": "application/json, text/event-stream"}


def status(token):
    headers = dict(base)
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.post(url, json={}, headers=headers, timeout=15).status_code


print("no token      ->", status(None), "(expect 401)")
print("wrong token   ->", status("wrong"), "(expect 401)")
print("correct token ->", status(config.MCP_TOKEN), "(expect anything but 401)")