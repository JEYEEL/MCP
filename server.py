from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from tools import files, search, git_lite

INSTRUCTIONS = """You work inside a sandboxed workspace. Rules for every session:
1. START: read PROJECT_STATE.md, PLAN_LOG.md, CHECKPOINTS.md and DECISIONS.md first.
2. Before acting, append your plan for this session to PLAN_LOG.md.
3. Prefer search_files and read_file with line ranges over reading whole files.
4. Do not retry a failed call without new information. Read the error message first.
5. END: update PROJECT_STATE.md, add a checkpoint to CHECKPOINTS.md, record any
   decisions in DECISIONS.md, then call git_commit.
"""

mcp = FastMCP(
    "file-server",
    instructions=INSTRUCTIONS,
    # The tunnel uses a changing hostname, and every request needs the bearer
    # token anyway, so the host-header check is turned off.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)
files.register(mcp)
search.register(mcp)
git_lite.register(mcp)

if __name__ == "__main__":
    mcp.run()