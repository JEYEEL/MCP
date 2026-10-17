# Midterm Report: MCP File Server Architecture, Tool Design & Security

## 1. Tech Stack Choices & Justifications
- Runtime & Language: Python 3.13 with native asyncio.
- Protocol & SDK: FastMCP (mcp.server.fastmcp) for JSON-RPC 2.0 dispatching, tool registration, and strict typing.
- HTTP Transport: Starlette ASGI wrapper with TokenAuth middleware mounted over FastMCP streamable HTTP.
- Ingress & Tunnel: Cloudflare Tunnel (cloudflared) for secure HTTPS public access without exposed ports.
- Process Supervisor: Production deployment configured for process supervisors (PM2 / systemd / Windows Service) for crash recovery.

## 2. Tool Design Choices
- File Operations: list_files, read_file, write_file, str_replace, delete_file.
  - str_replace vs Full Rewrite: Uses targeted string matching to reduce context window usage and prevent hallucinated truncations.
  - Destructive Action Gating: delete_file requires explicit confirm=True to prevent accidental data loss.
- Search Operations: search_files enables targeted keyword/regex discovery without reading whole directory trees into context.
- Git-Lite Version Control: git_status, git_commit, git_log.
  - Repository Isolation: Git state is kept in an external directory (wsgit) to prevent agents from corrupting .git internals via file tools.

## 3. Security Tradeoffs & Sandboxing
- Sandboxing & Traversal Prevention: Every file access resolves paths to canonical form and validates via is_relative_to(WORKSPACE_ROOT). Traversal attempts (../, root absolute paths, symlink tricks) trigger immediate ToolErrors.
- Ingress Authentication: TokenAuth middleware enforces Bearer token authorization; unauthenticated requests receive 401 Unauthorized.
- Audit Logging: All tool calls are written synchronously with timestamps to logs/tool_calls.log.

## 4. Multi-Session Handoff Execution
- State Preservation: Structured across PROJECT_STATE.md, PLAN_LOG.md, CHECKPOINTS.md, and DECISIONS.md.
- Multi-Session Proof: Session 1 (Architect) scaffolds, commits, and writes checkpoint; Session 2 (Implementer) resumes from CHECKPOINTS.md, performs str_replace, commits, and marks PROJECT_STATE.md COMPLETE. All 10 operations logged to transcript.json and tool_calls.log.
