from pathlib import Path

WORKSPACE_ROOT = (Path(__file__).parent / "workspace").resolve()


class SandboxError(Exception):
    """Raised when a path tries to leave the workspace."""


def resolve_path(user_path: str) -> Path:
    """Turn a user-supplied path into a safe absolute path inside the workspace."""
    if not user_path or not user_path.strip():
        raise SandboxError("Path is empty.")

    candidate = Path(user_path)
    if candidate.is_absolute():
        raise SandboxError(f"Absolute paths are not allowed: {user_path}")

    # resolve() removes '..' and follows symlinks
    full = (WORKSPACE_ROOT / candidate).resolve()

    if not full.is_relative_to(WORKSPACE_ROOT):
        raise SandboxError(f"Path escapes the workspace: {user_path}")

    return full