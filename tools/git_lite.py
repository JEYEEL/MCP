import subprocess
from sandbox import WORKSPACE_ROOT
from audit import log_call


def _git(*args: str) -> str:
    """Run a git command inside the workspace and return its output."""
    WORKSPACE_ROOT.mkdir(exist_ok=True)
    if not (WORKSPACE_ROOT / ".git").exists():
        subprocess.run(["git", "init"], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
    try:
        result = subprocess.run(
            ["git", *args], cwd=WORKSPACE_ROOT,
            capture_output=True, text=True, timeout=20,
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
        out = _git("log", f"-{limit}", "--oneline")
        return out or "No commits yet."