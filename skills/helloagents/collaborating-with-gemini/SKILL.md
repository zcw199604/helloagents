---
name: collaborating-with-gemini
description: Delegates coding tasks to Gemini CLI for prototyping, debugging, and code review. Use when needing algorithm implementation, bug analysis, or code quality feedback. Supports multi-turn sessions via SESSION_ID.
invocation: model
side_effects: external_process
requires: []
completion_criteria: 已按约束调用 Gemini CLI，保留 SESSION_ID，并返回结构化结果。
---

## Quick Start

Resolve `<skill-directory>` to the directory containing this `SKILL.md`. Never resolve the bridge relative to the user's project.

**PowerShell (recommended for long prompts):**

```powershell
$prompt = @'
Your task
'@

python "<skill-directory>/scripts/bridge.py" --cd "C:/path/to/project" --PROMPT $prompt --sandbox --timeout 600
```

**Bash / short prompt:**

```bash
python "<skill-directory>/scripts/bridge.py" --cd "/path/to/project" --PROMPT "Your task" --sandbox --timeout 600
```

**Output:** JSON with `success`, `SESSION_ID`, `agent_messages`, and optional `error`.

## Model And Timeout Policy

- Model requirement: pass `--model` when the task requires a specific Gemini model for reproducibility or policy compliance.
- Default model behavior: if `--model` is omitted, the bridge keeps Gemini CLI default model selection.
- Timeout policy: default to 600 seconds; use a smaller task-specific value when practical.
- Timeout escalation: use a larger value only when the caller explicitly requires it; never use an unbounded wait.
- Read-only enforcement: default `--sandbox` also passes Gemini `--approval-mode plan`; `--no-sandbox` is forbidden for review/acceptance and requires separate explicit write authorization.
- Timeout termination covers the CLI process tree; non-zero process exit or fatal stream events always produce `success=false`, even after partial assistant output.

## Parameters

```
usage: gemini_bridge.py [-h] --PROMPT PROMPT --cd CD [--sandbox] [--SESSION_ID SESSION_ID] [--return-all-messages] [--model MODEL]

Gemini Bridge

options:
  -h, --help            show this help message and exit
  --PROMPT PROMPT       Instruction for the task to send to gemini.
  --cd CD               Set the workspace root for gemini before executing the task.
  --sandbox, --no-sandbox
                        Run in sandbox mode. Defaults to `True`; disabling it requires explicit authorization.
  --SESSION_ID SESSION_ID
                        Resume the specified session of the gemini. Defaults to empty string, start a new session.
  --return-all-messages
                        Return all messages (e.g. reasoning, tool calls, etc.) from the gemini session. Set to `False` by default, only the agent's final reply message is
                        returned.
  --model MODEL         Optional model passthrough to Gemini CLI. No automatic model switching is applied.
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

**Prototyping (request diffs):**
```bash
python "<skill-directory>/scripts/bridge.py" --cd "/project" --PROMPT "Generate unified diff to add logging" --sandbox
```

**Debug with full trace:**
```bash
python "<skill-directory>/scripts/bridge.py" --cd "/project" --PROMPT "Debug this error" --return-all-messages --sandbox
```
