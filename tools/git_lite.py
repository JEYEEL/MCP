import os
import subprocess
from pathlib import Path
from sandbox import WORKSPACE_ROOT
from audit import log_call

# Git data lives OUTSIDE the workspace so agents can't tamper with it
GIT_DIR = Path(__file__).resolve().parent.parent / ".workspace-git"


def _git(*args: str) -> str:
    """Run a git command on the workspace and return its output."""
    WORKSPACE_ROOT.mkdir(exist_ok=True)
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}  # never wait for a prompt
    try:
        if not GIT_DIR.exists():
            subprocess.run(
                ["git", "init", "--bare", str(GIT_DIR)],
                capture_output=True, text=True, timeout=20,
                stdin=subprocess.DEVNULL, env=env,
            )
        result = subprocess.run(
            ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false",
             f"--git-dir={GIT_DIR}", f"--work-tree={WORKSPACE_ROOT}", *args],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            stdin=subprocess.DEVNULL,  # never touch the MCP stdio channel
            env=env,
        )
    except FileNotFoundError:
        raise ValueError("git is not installed or not on PATH.")
    except subprocess.TimeoutExpired:
        raise ValueError("git command timed out.")
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "git command failed.")
    return result.stdout.strip()


def register(mcp):
    @mcp.tool()
    def git_status() -> str:
        """Show which workspace files are new, changed or deleted since the last commit."""
        log_call("git_status", "")
        out = _git("status", "--short")
        return out or "Working tree clean. Nothing to commit."

    @mcp.tool()
    def git_commit(message: str) -> str:
        """Save all current workspace changes as a git commit with the given message."""
        if not message.strip():
            raise ValueError("Commit message is empty.")
        _git("add", "-A")
        if not _git("status", "--short"):
            raise ValueError("Nothing to commit. Use git_status to check.")
        _git("commit", "-m", message)
        log_call("git_commit", message)
        return f"Committed: {message}"

    @mcp.tool()
    def git_log(limit: int = 10) -> str:
        """Show recent commits in the workspace, newest first."""
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50.")
        log_call("git_log", f"limit={limit}")
        try:
            out = _git("log", f"-{limit}", "--oneline")
        except ValueError as e:
            if "does not have any commits" in str(e):
                return "No commits yet."
            raise
        return out or "No commits yet."