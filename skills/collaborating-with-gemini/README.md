# collaborating-with-gemini

A Claude Code **Agent Skill** that bridges Claude with Google Gemini CLI for multi-model collaboration on coding tasks.

## Overview

This Skill enables Claude to delegate coding tasks to Gemini CLI, combining the strengths of multiple AI models. Gemini handles algorithm implementation, debugging, and code analysis while Claude orchestrates the workflow and refines the output.

## Features

- **Multi-turn sessions**: Maintain conversation context across multiple interactions via `SESSION_ID`
- **Sandboxed execution**: Optional sandbox mode for isolated execution
- **JSON output**: Structured responses for easy parsing and integration
- **Cross-platform**: Windows path escaping handled automatically

## Installation

1. Ensure [Gemini CLI](https://github.com/google-gemini/gemini-cli) is installed and available in your PATH
2. Copy this Skill to your Claude Code skills directory:
   - User-level: `~/.claude/skills/collaborating-with-gemini/`
   - Project-level: `.claude/skills/collaborating-with-gemini/`

## Usage

> For long prompts on Windows PowerShell, prefer variable passing instead of inline long quoted strings.

### Basic

**PowerShell (recommended for long prompts):**

```powershell
$prompt = @'
Analyze the authentication flow
'@

python scripts/gemini_bridge.py --cd "C:/path/to/project" --PROMPT $prompt
```

**Bash / short prompt:**

```bash
python scripts/gemini_bridge.py --cd "/path/to/project" --PROMPT "Analyze the authentication flow"
```

### Multi-turn Session

**PowerShell (recommended for long prompts):**

```powershell
# Start a session
$prompt1 = @'
Review login.py for security issues
'@
python scripts/gemini_bridge.py --cd "C:/project" --PROMPT $prompt1
# Response includes SESSION_ID

# Continue the session
$prompt2 = @'
Suggest fixes for the issues found
'@
python scripts/gemini_bridge.py --cd "C:/project" --SESSION_ID "uuid-from-response" --PROMPT $prompt2
```

**Bash / short prompt:**

```bash
# Start a session
python scripts/gemini_bridge.py --cd "/project" --PROMPT "Review login.py for security issues"
# Response includes SESSION_ID

# Continue the session
python scripts/gemini_bridge.py --cd "/project" --SESSION_ID "uuid-from-response" --PROMPT "Suggest fixes for the issues found"
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--PROMPT` | Yes | Task instruction |
| `--cd` | Yes | Workspace root directory |
| `--sandbox` | No | Run in sandbox mode (default: off) |
| `--SESSION_ID` | No | Resume a previous session |
| `--return-all-messages` | No | Include full reasoning trace in output |
| `--model` | No | Explicit model override (default `flash`; clear opus request in prompt auto-switches to `opus`) |

### Output Format

```json
{
  "success": true,
  "SESSION_ID": "uuid",
  "agent_messages": "Gemini response text",
  "all_messages": []
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.
