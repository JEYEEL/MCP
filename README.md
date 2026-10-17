# Sandboxed MCP File Server & Multi-Agent Handoff

A sandboxed Model Context Protocol (MCP) file server built with FastMCP and Python 3.13, featuring 9 single-purpose tools, Git-Lite versioning, token authentication, and an automated 2-session agent handoff protocol.

## Features
- 9 Registered Tools: list_files, read_file, write_file, str_replace, delete_file, search_files, git_status, git_commit, git_log.
- Sandbox Security: Path normalization and boundary checks blocking directory traversal (../, absolute paths, symlinks).
- Audit Trail: Synchronous logging of all tool invocations to logs/tool_calls.log.
- Token Auth: Bearer token validation on HTTP endpoints.
- Agent Handoff Protocol: Dual-session context persistence via PROJECT_STATE.md, PLAN_LOG.md, CHECKPOINTS.md, and DECISIONS.md.

## Reproduction & Verification

### 1. Run Unit Tests (24 Tests)
pytest -v

### 2. Run 2-Session Agent Demo
python run_handoff_demo.py

## Deliverables & Evidence
- Architecture Report: REPORT.md
- Tool Call Transcript: transcript.json
- Audit Log: logs/tool_calls.log
- Handoff Files: workspace/ (PROJECT_STATE.md, PLAN_LOG.md, CHECKPOINTS.md, DECISIONS.md)
