import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from sandbox import resolve_path, SandboxError, WORKSPACE_ROOT


def test_normal_file_ok():
    assert resolve_path("notes.txt") == WORKSPACE_ROOT / "notes.txt"


def test_subfolder_ok():
    assert resolve_path("src/app.py") == WORKSPACE_ROOT / "src" / "app.py"


def test_parent_escape_blocked():
    with pytest.raises(SandboxError):
        resolve_path("../secret.txt")


def test_deep_escape_blocked():
    with pytest.raises(SandboxError):
        resolve_path("a/../../secret.txt")


def test_absolute_path_blocked():
    with pytest.raises(SandboxError):
        resolve_path("C:\\Windows\\win.ini")


def test_empty_blocked():
    with pytest.raises(SandboxError):
        resolve_path("")    