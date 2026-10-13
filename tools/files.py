from sandbox import resolve_path, SandboxError
from audit import log_call

MAX_CHARS = 20000  # keeps outputs small so the agent doesn't flood its context


def _safe_path(path: str):
    """Resolve a path inside the sandbox, turning sandbox errors into friendly ones."""
    try:
        return resolve_path(path)
    except SandboxError as e:
        raise ValueError(str(e))


def register(mcp):
    @mcp.tool()
    def list_files(path: str = ".") -> str:
        """List files and folders inside a workspace folder.
        Use path "." for the workspace root. Folders end with "/"."""
        folder = _safe_path(path)
        if not folder.is_dir():
            raise ValueError(f"Not a folder: {path}. Use list_files('.') to see what exists.")
        items = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name))
        if not items:
            return "(empty folder)"
        return "\n".join(p.name + ("/" if p.is_dir() else "") for p in items)

    @mcp.tool()
    def read_file(path: str, start_line: int = 1, end_line: int | None = None) -> str:
        """Read a text file from the workspace. Optionally read only lines
        start_line to end_line (1-based, inclusive) to keep output small."""
        file = _safe_path(path)
        if not file.is_file():
            raise ValueError(f"File not found: {path}. Use list_files to see what exists.")
        if start_line < 1:
            raise ValueError("start_line must be 1 or higher.")
        lines = file.read_text(encoding="utf-8").splitlines()
        end = end_line or len(lines)
        chunk = "\n".join(lines[start_line - 1:end])
        if len(chunk) > MAX_CHARS:
            chunk = (
                chunk[:MAX_CHARS]
                + f"\n...[truncated. File has {len(lines)} lines. "
                "Use start_line/end_line to read more.]"
            )
        return chunk

    @mcp.tool()
    def write_file(path: str, content: str) -> str:
        """Create a new file or overwrite an existing one in the workspace.
        Parent folders are created automatically."""
        file = _safe_path(path)
        if file.is_dir():
            raise ValueError(f"{path} is a folder, not a file.")
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
        log_call("write_file", f"{path} ({len(content)} chars)")
        return f"Wrote {len(content)} characters to {path}"

    @mcp.tool()
    def str_replace(path: str, old_str: str, new_str: str) -> str:
        """Replace one exact piece of text in a file with new text.
        old_str must appear exactly once. Use read_file first to copy it exactly."""
        file = _safe_path(path)
        if not file.is_file():
            raise ValueError(f"File not found: {path}. Use list_files to see what exists.")
        text = file.read_text(encoding="utf-8")
        count = text.count(old_str)
        if count == 0:
            raise ValueError("old_str was not found. Use read_file to check the exact text.")
        if count > 1:
            raise ValueError(
                f"old_str appears {count} times. Include more surrounding text so it matches once."
            )
        file.write_text(text.replace(old_str, new_str, 1), encoding="utf-8")
        log_call("str_replace", path)
        return f"Replaced 1 occurrence in {path}"

    @mcp.tool()
    def delete_file(path: str, confirm: bool = False) -> str:
        """Delete a file from the workspace. This cannot be undone.
        You must pass confirm=true or nothing is deleted."""
        file = _safe_path(path)
        if not confirm:
            raise ValueError("Delete not performed. Call again with confirm=true to delete.")
        if not file.is_file():
            raise ValueError(f"File not found: {path}. Only files can be deleted.")
        file.unlink()
        log_call("delete_file", path)
        return f"Deleted {path}"