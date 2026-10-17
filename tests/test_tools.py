import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from mcp.server.fastmcp.exceptions import ToolError

import audit
import sandbox
from server import mcp
from tools import git_lite, search


@pytest.fixture(autouse=True)
def temp_workspace(tmp_path, monkeypatch):
    """Run every test against a throwaway workspace, git repo and log file."""
    ws = (tmp_path / "workspace").resolve()
    ws.mkdir()
    monkeypatch.setattr(sandbox, "WORKSPACE_ROOT", ws)
    monkeypatch.setattr(search, "WORKSPACE_ROOT", ws)
    monkeypatch.setattr(git_lite, "WORKSPACE_ROOT", ws)
    monkeypatch.setattr(git_lite, "GIT_DIR", tmp_path / "wsgit")
    monkeypatch.setattr(audit, "LOG_FILE", tmp_path / "logs" / "tool_calls.log")
    for var in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(var, "Test User")
    for var in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(var, "test@example.com")
    return ws


def call(name, **args):
    """Call a tool the way an MCP client would and return its text output."""
    result = asyncio.run(mcp.call_tool(name, args))
    content = result[0] if isinstance(result, tuple) else result
    return "\n".join(block.text for block in content)


def fails(name, **args):
    """Call a tool that should fail and return its error message."""
    with pytest.raises(ToolError) as info:
        call(name, **args)
    return str(info.value)


def test_all_nine_tools_registered():
    names = {t.name for t in asyncio.run(mcp.list_tools())}
    assert names == {
        "list_files", "read_file", "write_file", "str_replace", "delete_file",
        "search_files", "git_status", "git_commit", "git_log",
    }


def test_write_read_list_roundtrip():
    call("write_file", path="notes/a.txt", content="one\ntwo\nthree")
    assert call("read_file", path="notes/a.txt") == "one\ntwo\nthree"
    assert call("list_files", path="notes") == "a.txt"
    assert "notes/" in call("list_files", path=".")


def test_read_line_range():
    call("write_file", path="a.txt", content="one\ntwo\nthree\nfour")
    assert call("read_file", path="a.txt", start_line=2, end_line=3) == "two\nthree"


def test_read_missing_file_gives_helpful_error():
    assert "File not found" in fails("read_file", path="nope.txt")


def test_str_replace_success_and_errors():
    call("write_file", path="a.txt", content="hello world\nhello again")
    assert "not found" in fails("str_replace", path="a.txt", old_str="zzz", new_str="x")
    assert "appears 2 times" in fails("str_replace", path="a.txt", old_str="hello", new_str="x")
    call("str_replace", path="a.txt", old_str="hello world", new_str="goodbye world")
    assert call("read_file", path="a.txt") == "goodbye world\nhello again"


def test_delete_needs_confirm():
    call("write_file", path="a.txt", content="x")
    assert "confirm=true" in fails("delete_file", path="a.txt")
    assert call("list_files", path=".") == "a.txt"  # still there
    call("delete_file", path="a.txt", confirm=True)
    assert call("list_files", path=".") == "(empty folder)"


@pytest.mark.parametrize("tool,args", [
    ("list_files", {"path": "../"}),
    ("read_file", {"path": "../secret.txt"}),
    ("write_file", {"path": "../escape.txt", "content": "x"}),
    ("str_replace", {"path": "../a.txt", "old_str": "a", "new_str": "b"}),
    ("delete_file", {"path": "../a.txt", "confirm": True}),
    ("search_files", {"query": "x", "path": "../"}),
])
def test_every_file_tool_blocks_path_escape(tool, args, temp_workspace):
    assert "escapes the workspace" in fails(tool, **args)
    assert not (temp_workspace.parent / "escape.txt").exists()


def test_absolute_path_blocked():
    path = "C:\\Windows\\win.ini" if sys.platform == "win32" else "/etc/passwd"
    assert "Absolute paths" in fails("read_file", path=path)


def test_search_finds_and_reports_no_match():
    call("write_file", path="planner/script.js", content="// TODO: add task\nlet x = 1;\n// todo: remove task")
    out = call("search_files", query="todo")
    assert "planner/script.js:1:" in out and "planner/script.js:3:" in out
    assert call("search_files", query="nothing-here") == "No matches for 'nothing-here'."


def test_git_status_commit_log():
    call("write_file", path="a.txt", content="x")
    assert "a.txt" in call("git_status")
    assert call("git_commit", message="first commit") == "Committed: first commit"
    assert "clean" in call("git_status")
    assert "first commit" in call("git_log", limit=5)
    assert "Nothing to commit" in fails("git_commit", message="again")


def test_git_rejects_bad_input():
    assert "empty" in fails("git_commit", message="  ")
    assert "between 1 and 50" in fails("git_log", limit=0)


def test_git_log_on_empty_repo_is_friendly():
    assert call("git_log") == "No commits yet."


def test_calls_are_written_to_audit_log():
    call("write_file", path="a.txt", content="x")
    call("read_file", path="a.txt")
    call("list_files", path=".")
    call("search_files", query="x")
    call("git_status")
    call("git_log")
    text = audit.LOG_FILE.read_text(encoding="utf-8")
    for tool in ("write_file", "read_file", "list_files", "search_files", "git_status", "git_log"):
        assert f"| {tool} |" in text