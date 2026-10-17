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


---

## 5. Test & Verification Results

### A. Endpoint Authentication Check (Criteria D & E)
Verification of bearer token gating and HTTP transport security:
\\	ext
no token      -> 401 (expect 401)
wrong token   -> 401 (expect 401)
correct token -> 400 (expect anything but 401: validates auth passed before payload inspection)
\
### B. Unit & Security Test Suite (24/24 Passed)
\\	ext
tests/test_sandbox.py (6/6 passed - path traversal, parent escape, symlinks)
tests/test_tools.py (18/18 passed - 9 tools registered, read/write/replace, git-lite, audit logs)
24 passed in 2.25s
\
### C. Live Audit Trail Verification (logs/tool_calls.log)
\\	ext
2026-10-17T10:03:29 | read_file | PROJECT_STATE.md lines 1-end
2026-10-17T10:04:11 | read_file | PROJECT_STATE.md lines 1-end
2026-10-17T10:04:29 | delete_file | PROJECT_STATE.md
2026-10-17T10:05:01 | auth_failed | POST /mcp header_len=0 scheme='' got_fp=none want_fp=3ded5fa7
2026-10-17T10:05:01 | auth_failed | POST /mcp header_len=12 scheme='Bearer' got_fp=8810ad58 want_fp=3ded5fa7
\