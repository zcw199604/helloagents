---
name: collaborating-with-codex
description: Delegates coding tasks to Codex CLI for prototyping, debugging, and code review. Use when needing algorithm implementation, bug analysis, or code quality feedback. Supports multi-turn sessions via SESSION_ID.
invocation: model
side_effects: external_process
requires: []
completion_criteria: 已按约束调用 Codex CLI，保留 SESSION_ID，并返回结构化结果。
---

## Quick Start

Resolve `<skill-directory>` to the directory containing this `SKILL.md`. Never resolve the bridge relative to the user's project.

**PowerShell (recommended for long prompts):**

```powershell
$prompt = @'
Your task
'@

python "<skill-directory>/scripts/bridge.py" --cd "C:/path/to/project" --PROMPT $prompt --sandbox read-only --timeout 600
```

**Bash / short prompt:**

```bash
python "<skill-directory>/scripts/bridge.py" --cd "/path/to/project" --PROMPT "Your task" --sandbox read-only --timeout 600
```

**Output:** JSON with `success`, `SESSION_ID`, `agent_messages`, and optional `error`.

## Model And Timeout Policy

- Model requirement: pass `--model` when the task requires a specific Codex model for reproducibility or policy compliance.
- Default model behavior: if `--model` is omitted, the bridge keeps Codex CLI default model selection.
- Timeout policy: default to 600 seconds; use a smaller task-specific value when practical.
- Timeout escalation: use a larger value only when the caller explicitly requires it; never use an unbounded wait.
- Read-only enforcement: review/acceptance keeps `--sandbox read-only`; `--yolo` maps to Codex's explicit dangerous bypass flag and is forbidden for read-only review.
- Timeout termination covers the CLI process tree; non-zero process exit or fatal stream events always produce `success=false`, even after partial assistant output.

## Parameters

```
usage: codex_bridge.py [-h] --PROMPT PROMPT --cd CD [--sandbox {read-only,workspace-write,danger-full-access}] [--SESSION_ID SESSION_ID] [--skip-git-repo-check]
                       [--return-all-messages] [--image IMAGE] [--model MODEL] [--yolo] [--profile PROFILE]

Codex Bridge

options:
  -h, --help            show this help message and exit
  --PROMPT PROMPT       Instruction for the task to send to codex.
  --cd CD               Set the workspace root for codex before executing the task.
  --sandbox {read-only,workspace-write,danger-full-access}
                        Sandbox policy for model-generated commands. Defaults to `read-only`.
  --SESSION_ID SESSION_ID
                        Resume the specified session of the codex. Defaults to `None`, start a new session.
  --skip-git-repo-check
                        Allow codex running outside a Git repository (useful for one-off directories).
  --return-all-messages
                        Return all messages (e.g. reasoning, tool calls, etc.) from the codex session. Set to `False` by default, only the agent's final reply message is
                        returned.
  --image IMAGE         Attach one or more image files to the initial prompt. Repeat the flag for multiple paths.
  --model MODEL         Optional model passthrough to Codex CLI. No additional model restriction is applied by the bridge.
  --yolo                Run every command without approvals or sandboxing. Only use when `sandbox` couldn't be applied.
  --profile PROFILE     Optional profile passthrough to Codex CLI.
  --timeout TIMEOUT     Maximum runtime in seconds. Defaults to 600.
```

## Multi-turn Sessions

**Always capture `SESSION_ID`** from the first response for follow-up:

```powershell
# Initial task
$prompt1 = @'
Analyze auth in login.py
'@
python "<skill-directory>/scripts/bridge.py" --cd "C:/project" --PROMPT $prompt1

# Continue with SESSION_ID
$prompt2 = @'
Write unit tests for that
'@
python "<skill-directory>/scripts/bridge.py" --cd "C:/project" --SESSION_ID "uuid-from-response" --PROMPT $prompt2
```

```bash
# Initial task
python "<skill-directory>/scripts/bridge.py" --cd "/project" --PROMPT "Analyze auth in login.py"

# Continue with SESSION_ID
python "<skill-directory>/scripts/bridge.py" --cd "/project" --SESSION_ID "uuid-from-response" --PROMPT "Write unit tests for that"
```

## Common Patterns

**Prototyping (read-only, request diffs):**
```bash
python "<skill-directory>/scripts/bridge.py" --cd "/project" --PROMPT "Generate unified diff to add logging"
```

**Debug with full trace:**
```bash
python "<skill-directory>/scripts/bridge.py" --cd "/project" --PROMPT "Debug this error" --return-all-messages
```
