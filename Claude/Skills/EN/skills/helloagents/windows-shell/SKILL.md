---
name: windows-shell
description: Windows PowerShell encoding rules and syntax constraints; read when Platform=win32 and shell commands are needed
---

# Windows PowerShell Environment Rules

**Applicable Scope:** When Platform=win32 and AI built-in tools cannot fulfill the need, requiring shell commands; the PowerShell section in bootstrap G1 has been migrated to this Skill.

---

## Core Principles

- Prioritize AI built-in tools for file operations, use shell commands only when necessary
- When using shell commands, MUST follow the "Encoding Rules" and "Syntax Constraints" below
- Cross-platform compatibility: Use only PowerShell native cmdlets and syntax
- Pre-execution verification: Verify syntax integrity in internal thinking (escape closure, bracket matching, parameter format), query documentation when uncertain

---

## Encoding Rules

```yaml
Read: Auto-detect and use original file encoding or specify -Encoding UTF8
Write: MUST add -Encoding UTF8 by default, unless special encoding requirements exist
Transfer: Auto-detect and use original file encoding
```

---

## Syntax Constraints

```yaml
File Operations: Add -Force by default to avoid target conflicts
Environment Variables: Use $env:VAR format, $VAR is prohibited
Command-line Parameters: -NoProfile is prohibited (user Profile must load to ensure UTF-8 encoding)
Redirection: << and <() are prohibited, use Here-String @'...'@ for multi-line text input
Here-String: Closing marker '@ or "@ MUST be on its own line and at the beginning of the line
Cmdlet Parameters: Compound parameters (e.g., -Context) MUST explicitly specify -Path, pure pipeline input is prohibited
Variable Reference: $ must be followed by valid variable name, use ${var} form to avoid ambiguity
Path Parameters: Filenames and paths MUST be wrapped in double quotes, e.g., "file.txt", "$filePath", to avoid null errors and space issues
Escape Sequences: Use backtick for literal $, e.g., "Price: `$100"
Quote Nesting: Double quotes inside double quotes must be escaped "", or use single quotes
Escape Characters: `n (newline) `t (tab) `$ (literal $)
Parameter Combination: Verify compatibility before combining multiple parameters, adjust per error message when encountering mutual exclusion errors
Command Chaining: && and || are prohibited in PS5.1, use semicolon or if ($?) for conditional execution
Comparison Operators: > < are prohibited for comparison (parsed as redirection), MUST use -gt -lt -eq -ne
Null Comparison: $null MUST be placed on the left side of comparison, e.g., $null -eq $var
```
