from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "logs" / "tool_calls.log"


def log_call(tool: str, detail: str) -> None:
    """Append one line per tool call so every action can be reviewed later."""
    LOG_FILE.parent.mkdir(exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{stamp} | {tool} | {detail}\n")