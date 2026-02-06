# collaborating-with-claude

A Claude Code **Agent Skill** that bridges Claude with Claude CLI for multi-model collaboration on coding tasks.

## Overview

This Skill enables an orchestrating agent to delegate coding tasks to Claude CLI, combining strengths across tools. Claude handles implementation, debugging, and code analysis while the orchestrator coordinates workflow and refines output.

## Features

- **Multi-turn sessions**: Maintain conversation context across multiple interactions via `SESSION_ID`
- **Sandbox compatibility**: Supports `read-only`, `workspace-write`, and `danger-full-access` modes
- **JSON output**: Structured responses for easy parsing and integration
- **Cross-platform**: Windows path escaping handled automatically

## Installation

1. Ensure [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) is installed and available in your PATH
2. Copy this Skill to your CLI skills directory:
   - User-level: `~/.codex/skills/collaborating-with-claude/` or `~/.claude/skills/collaborating-with-claude/`
   - Project-level: `./.codex/skills/collaborating-with-claude/` or `./.claude/skills/collaborating-with-claude/`

## Usage

### Basic

```bash
python scripts/claude_bridge.py --cd "/path/to/project" --PROMPT "Analyze the authentication flow"
```

### Multi-turn Session

```bash
# Start a session
python scripts/claude_bridge.py --cd "/project" --PROMPT "Review login.py for security issues"
# Response includes SESSION_ID

# Continue the session
python scripts/claude_bridge.py --cd "/project" --SESSION_ID "uuid-from-response" --PROMPT "Suggest fixes for the issues found"
```

### Output Format

```json
{
  "success": true,
  "SESSION_ID": "uuid",
  "agent_messages": "Claude response text",
  "all_messages": []
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.
