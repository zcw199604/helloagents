---
name: collaborating-with-claude
description: Delegates coding tasks to Claude CLI for prototyping, debugging, and code review. Use when needing algorithm implementation, bug analysis, or code quality feedback. Supports multi-turn sessions via SESSION_ID.
---

## Quick Start

```bash
python scripts/claude_bridge.py --cd "/path/to/project" --PROMPT "Your task"
```

**Output:** JSON with `success`, `SESSION_ID`, `agent_messages`, and optional `error`.

## Parameters

```
usage: claude_bridge.py [-h] --PROMPT PROMPT --cd CD [--sandbox [{read-only,workspace-write,danger-full-access}]] [--SESSION_ID SESSION_ID]
                        [--skip-git-repo-check] [--return-all-messages] [--image IMAGE] [--model MODEL] [--yolo] [--profile PROFILE]

Claude Bridge

options:
  -h, --help            show this help message and exit
  --PROMPT PROMPT       Instruction for the task to send to claude.
  --cd CD               Set the workspace root for claude before executing the task.
  --sandbox [{read-only,workspace-write,danger-full-access}]
                        Sandbox compatibility option. Defaults to `read-only`.
  --SESSION_ID SESSION_ID
                        Resume the specified session of the claude. Defaults to empty string, start a new session.
  --skip-git-repo-check
                        Compatibility option with codex bridge; ignored in claude bridge.
  --return-all-messages
                        Return all messages (e.g. reasoning, tool calls, etc.) from the claude session. Set to `False` by default, only the
                        agent's final reply message is returned.
  --image IMAGE         Compatibility option with codex bridge. Currently ignored in claude bridge.
  --model MODEL         Explicit model override. Defaults to `sonnet`; if prompt clearly requests opus, auto-switches to `opus`.
  --yolo                Run every command without approvals or sandboxing. Use with caution.
  --profile PROFILE     Compatibility option with codex bridge. Currently ignored in claude bridge.
```

## Multi-turn Sessions

**Always capture `SESSION_ID`** from the first response for follow-up:

```bash
# Initial task
python scripts/claude_bridge.py --cd "/project" --PROMPT "Analyze auth in login.py"

# Continue with SESSION_ID
python scripts/claude_bridge.py --cd "/project" --SESSION_ID "uuid-from-response" --PROMPT "Write unit tests for that"
```

## Common Patterns

**Prototyping (read-only, request diffs):**
```bash
python scripts/claude_bridge.py --cd "/project" --PROMPT "Generate unified diff to add logging" --sandbox read-only
```

**Debug with full trace:**
```bash
python scripts/claude_bridge.py --cd "/project" --PROMPT "Debug this error" --return-all-messages
```
