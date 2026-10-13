from sandbox import WORKSPACE_ROOT, resolve_path, SandboxError

MAX_LINE_CHARS = 200


def register(mcp):
    @mcp.tool()
    def search_files(query: str, path: str = ".", max_results: int = 30) -> str:
        """Search for text inside workspace files (case-insensitive).
        Returns matching lines as 'file:line: text'. Use this instead of
        reading whole files to find where something is."""
        if not query.strip():
            raise ValueError("query is empty.")
        try:
            start = resolve_path(path)
        except SandboxError as e:
            raise ValueError(str(e))
        if not start.exists():
            raise ValueError(f"Path not found: {path}. Use list_files to see what exists.")

        files = [start] if start.is_file() else sorted(p for p in start.rglob("*") if p.is_file())
        needle = query.lower()
        results = []
        for f in files:
            if ".git" in f.parts:
                continue
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue  # skip binary or unreadable files
            for i, line in enumerate(lines, start=1):
                if needle in line.lower():
                    rel = f.relative_to(WORKSPACE_ROOT).as_posix()
                    results.append(f"{rel}:{i}: {line.strip()[:MAX_LINE_CHARS]}")
                    if len(results) >= max_results:
                        results.append(f"...[stopped at {max_results} results. Narrow your query or path.]")
                        return "\n".join(results)
        return "\n".join(results) if results else f"No matches for '{query}'."