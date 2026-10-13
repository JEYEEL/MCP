from sandbox import resolve_path, WORKSPACE_ROOT, SandboxError

MAX_CHARS = 20000  # keeps outputs small so the agent doesn't flood its context


def register(mcp):
    @mcp.tool()
    def list_files(path: str = ".") -> str:
        """List files and folders inside a workspace folder.
        Use path "." for the workspace root. Folders end with "/"."""
        try:
            folder = resolve_path(path)
        except SandboxError as e:
            raise ValueError(str(e))
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
        try:
            file = resolve_path(path)
        except SandboxError as e:
            raise ValueError(str(e))
        if not file.is_file():
            raise ValueError(f"File not found: {path}. Use list_files to see what exists.")
        lines = file.read_text(encoding="utf-8").splitlines()
        end = end_line or len(lines)
        chunk = "\n".join(lines[start_line - 1:end])
        if len(chunk) > MAX_CHARS:
            chunk = chunk[:MAX_CHARS] + f"\n...[truncated. File has {len(lines)} lines. Use start_line/end_line to read more.]"
        return chunk