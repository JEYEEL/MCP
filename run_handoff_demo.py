import asyncio
import json
import os
from pathlib import Path

# Ensure git credentials exist for commits
os.environ["GIT_AUTHOR_NAME"] = "Agent Session"
os.environ["GIT_COMMITTER_NAME"] = "Agent Session"
os.environ["GIT_AUTHOR_EMAIL"] = "agent@session.local"
os.environ["GIT_COMMITTER_EMAIL"] = "agent@session.local"

from server import mcp

def call(name: str, **args):
    """Executes a tool via the MCP server dispatcher and returns text."""
    result = asyncio.run(mcp.call_tool(name, args))
    content = result[0] if isinstance(result, tuple) else result
    return "\n".join(block.text for block in content)

def main():
    transcript = []
    print("[*] Initializing 2-Session Multi-Agent Handoff Demo...")

    # ==========================================
    # SESSION 1: Architect / Scaffolder
    # ==========================================
    print("\n>>> STARTING AGENT SESSION 1 (Architect / Scaffolder)...")
    
    # 1. Read existing state
    print(" -> [Session 1] Tool Call: read_file('PROJECT_STATE.md')")
    res1 = call("read_file", path="PROJECT_STATE.md")
    transcript.append({"session": 1, "tool": "read_file", "args": {"path": "PROJECT_STATE.md"}, "result": res1})

    # 2. Append implementation plan
    print(" -> [Session 1] Tool Call: write_file('PLAN_LOG.md')")
    plan_entry = "\n### Session 1 Execution\n- [x] Scaffold study planner CLI script\n- [ ] Session 2 handoff: Priority sorting\n"
    res2 = call("write_file", path="PLAN_LOG.md", content=plan_entry)
    transcript.append({"session": 1, "tool": "write_file", "args": {"path": "PLAN_LOG.md"}, "result": res2})

    # 3. Scaffold target application file
    print(" -> [Session 1] Tool Call: write_file('study_planner.py')")
    code = (
        "def list_tasks():\n"
        "    print('Task: Study Math - Priority: Normal')\n\n"
        "if __name__ == '__main__':\n"
        "    list_tasks()\n"
    )
    res3 = call("write_file", path="study_planner.py", content=code)
    transcript.append({"session": 1, "tool": "write_file", "args": {"path": "study_planner.py"}, "result": res3})

    # 4. Git commit
    print(" -> [Session 1] Tool Call: git_commit('Scaffold study planner CLI')")
    res4 = call("git_commit", message="Scaffold study planner CLI")
    transcript.append({"session": 1, "tool": "git_commit", "args": {"message": "Scaffold study planner CLI"}, "result": res4})

    # 5. Write Checkpoint
    print(" -> [Session 1] Tool Call: write_file('CHECKPOINTS.md')")
    chk = (
        "## Checkpoint - Session 1 Completed\n"
        "- Status: Scaffolding complete and committed.\n"
        "- Next Action for Session 2: Use str_replace on study_planner.py to implement priority sorting.\n"
    )
    res5 = call("write_file", path="CHECKPOINTS.md", content=chk)
    transcript.append({"session": 1, "tool": "write_file", "args": {"path": "CHECKPOINTS.md"}, "result": res5})
    print("[+] Session 1 Completed Successfully.")

    print("\n-----------------------------------------------------")
    print("[*] Context reset: Disconnecting Session 1. Starting Session 2...")
    print("-----------------------------------------------------\n")

    # ==========================================
    # SESSION 2: Implementer / Completion
    # ==========================================
    print(">>> STARTING AGENT SESSION 2 (Implementer / Completion)...")

    # 1. Read checkpoint only (agent efficiency requirement)
    print(" -> [Session 2] Tool Call: read_file('CHECKPOINTS.md')")
    res6 = call("read_file", path="CHECKPOINTS.md")
    transcript.append({"session": 2, "tool": "read_file", "args": {"path": "CHECKPOINTS.md"}, "result": res6})

    # 2. Targeted replacement using str_replace
    print(" -> [Session 2] Tool Call: str_replace('study_planner.py')")
    old_code = "    print('Task: Study Math - Priority: Normal')"
    new_code = (
        "    tasks = [('Study Math', 1), ('Review MCP Specs', 2)]\n"
        "    for task, priority in sorted(tasks, key=lambda x: x[1]):\n"
        "        print(f'Task: {task} (Priority {priority})')"
    )
    res7 = call("str_replace", path="study_planner.py", old_str=old_code, new_str=new_code)
    transcript.append({"session": 2, "tool": "str_replace", "args": {"path": "study_planner.py"}, "result": res7})

    # 3. Verify git status and commit
    print(" -> [Session 2] Tool Call: git_status()")
    res8 = call("git_status")
    transcript.append({"session": 2, "tool": "git_status", "args": {}, "result": res8})

    print(" -> [Session 2] Tool Call: git_commit('Implement priority sorting')")
    res9 = call("git_commit", message="Implement priority sorting")
    transcript.append({"session": 2, "tool": "git_commit", "args": {"message": "Implement priority sorting"}, "result": res9})

    # 4. Final state mark
    print(" -> [Session 2] Tool Call: write_file('PROJECT_STATE.md')")
    state_text = (
        "## Project State\n"
        "- Current Status: COMPLETE\n"
        "- Verified: Scaffolded, refactored with priority sorting, and committed across 2 agent sessions.\n"
    )
    res10 = call("write_file", path="PROJECT_STATE.md", content=state_text)
    transcript.append({"session": 2, "tool": "write_file", "args": {"path": "PROJECT_STATE.md"}, "result": res10})
    print("[+] Session 2 Completed Successfully.")

    # Save deliverables
    out_path = Path("transcript.json")
    out_path.write_text(json.dumps(transcript, indent=2), encoding="utf-8")
    print(f"\n[SUCCESS] '{out_path.name}' generated successfully with {len(transcript)} tool calls recorded!")

if __name__ == "__main__":
    main()
