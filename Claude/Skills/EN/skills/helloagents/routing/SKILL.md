---
name: routing
description: Detailed routing mechanism rules; read for complex boundary routing decisions (score boundaries, ambiguous EHRB, mode upgrades, context interruptions, command paths)
---

# Routing Mechanism - Detailed Rules

**Applicable Scope:** Routing decisions in complex boundary scenarios; bootstrap retains only the minimal decision tree, this Skill provides full evaluation dimensions, decision principles, context response rules, and command path definitions.

---

## Routing Flow

For each user message, execute the following steps:

1. **Phase Lock Check**: Locked → Silently queue message, process sequentially after current phase completes
2. **Information Extraction**: Scan command words, context state, intent, EHRB signals
3. **Routing Decision**: Match per routing priority

---

## Routing Priority

**Mutually Exclusive Decision Tree (match in order, stop when hit):**
```yaml
1. Command Mode (~auto/~plan/~exec/~init)
2. Context Response (follow-up/selection/confirmation/feedback)
3. Systematic Debugging Mode (bug/test failure/build failure/runtime exception/performance regression/flaky)
4. Development Mode (fine-tuning → lightweight iteration → standard development → complete R&D)
5. Consultation Q&A (fallback)
```

---

## Evaluation Dimensions

```yaml
Primary dimensions:
  Intent type: Q&A type | Modification type | Command type
  Modification scope: None | Micro (≤2 files ≤30 lines) | Small (3-5 files) | Medium (multi-file) | Large (architecture-level) | Uncertain
  Requirement clarity: Clear | Ambiguous | Needs clarification
  Context state: None | In follow-up | In selection | In confirmation
  Command modifier: None | ~auto | ~plan | ~init | ~exec

Secondary dimensions:
  Debugging signal: Bug | Test failure | Build failure | Runtime exception | Performance regression | flaky | None
  EHRB risk signal: Yes | No
  TDD applicability: Required | Recommended | Exempt | Uncertain
  Keywords: prod|production|live|DROP|TRUNCATE|rm -rf|keys|payment|bug|error|exception|failure|regression|flaky|timeout|stack trace|pollution|polluter|passes alone|suite failure|boundary|chain
```

---

## Decision Principles

- Fine-tuning/Lightweight iteration/Standard development conditions are "all must meet" type, any not met then downgrade
- Complete R&D conditions are "meet any" type, serves as conservative fallback
- Default to Complete R&D when uncertain

---

## Routing Verification

<routing_verification>

⚠️ **CRITICAL - Mandatory Enforcement Rules:**

**Pre-routing verification (complete in <thinking>):**
1. **Intent type**: [Q&A type/Modification type/Command type] - Basis: [quote user's original words]
2. **Modification scope**: [None/Micro/Small/Medium/Large/Uncertain] - Basis: [file count/line count estimate]
3. **Debugging signal**: [Bug/Test failure/Build failure/Runtime exception/Performance regression/flaky/None] - Basis: [error/log/keywords]
4. **EHRB signal**: [Yes/No] - Basis: [keyword scan result]
5. **Final routing**: [Consultation Q&A/Systematic Debugging/Fine-tuning/Lightweight iteration/Standard development/Complete R&D]

**Post-routing restatement (in output):**
- If routed to development mode (not consultation Q&A): "Determined as [mode name], reason: [1-2 sentence explanation]"
- If routed to systematic debugging mode: "Determined as Systematic Debugging Mode, reason: detected [debugging signal], will reproduce and locate root cause before modifying"
- If uncertain: "Requirement complexity uncertain, defaulting to complete R&D flow to ensure quality"

**Uncertainty handling:**
- Boundary cases (e.g., exactly 2 files) → Refer to G3 uncertainty handling principles
- Critical information missing → Conservative routing (choose more complete path)

</routing_verification>

---

## Processing Paths

<complexity_paths>

**Consultation Q&A**
- Condition: Does not meet any above conditions (fallback)
- Action: Answer directly per G6.3 format in output-format Skill

**Systematic Debugging Mode**
- Condition (meets any): User reports a bug, test failure, build failure, runtime exception, performance regression, flaky/timeout behavior, error logs, stack trace, or regression issue
- Action:
  1. First enter the systematic debugging gate in development implementation (see `develop` Skill)
  2. Before fixing, MUST complete: read full error, reproduce stably, inspect recent changes, locate failure layer, trace the source of bad data/bad state
  3. Multi-component chains must collect boundary evidence; test pollution must locate the polluter; bad-data issues must add necessary defenses after root cause is confirmed
  4. Verify only one hypothesis at a time; prohibit stacking unverified patches
  5. After 3 consecutive failed fixes or inability to locate root cause → stop expanding changes, re-enter requirements analysis/solution design or request confirmation per G3
  6. After root cause is clear, enter fine-tuning/lightweight iteration/standard development/complete R&D based on impact scope; if EHRB involved, use complete R&D
- Output:
  - When reproduction information is missing: use requirements analysis follow-up format
  - When fix is complete: output using the final actual development mode (fine-tuning/lightweight iteration/development implementation/command complete)

**Fine-tuning Mode**
- Condition (all must meet): Intent=modification type, instruction clearly contains file path, files≤2, lines≤30, no architecture impact, command modifier=none, EHRB=no
- Action: Directly modify code
- Knowledge base handling:
  - Knowledge base does not exist: Don't create, prompt "Recommend executing ~init" in output
  - Knowledge base exists:
    - Quick check core file existence (CHANGELOG.md, project.md, wiki/*.md)
    - Core files missing → Skip knowledge base update, prompt "Recommend executing ~init to fix" in output
    - Core files complete → Only update affected module's `wiki/modules/<module>.md` (if corresponding module documentation exists)
- EHRB threshold: Detect EHRB signal → Output risk escalation prompt, execute per target mode
- Output format:
  ```
  ✅【HelloAGENTS】- Fine-tuning Mode Complete

  - ✅ Changes: [brief description of modifications]
  - 📁 Affected files: [file names]
  - 📚 Knowledge base: [Updated/⚠️ Recommend executing ~init]

  ────
  📁 Changes:
    - {file_path1}
    - {file_path2}
    ...

  🔄 Next Steps: Please verify changes
  ```

**Lightweight Iteration**
- Condition (all must meet): Intent=modification type, instruction clear, files 3-5, no architecture decisions, command modifier=none, EHRB=no
- Action flow:
  1. Check knowledge base status and handle (per G10 quick decision tree)
  2. Acquire project context (per G10 quick flow)
  3. Create simplified solution package (task.md only, omit why.md/how.md)
  4. Execute code changes
  5. Synchronize update knowledge base (per `kb` Skill sync rules)
  6. Migrate solution package to helloagents/<branch-name>/history/
  7. Scan legacy solutions
- Simplified solution package rules:
  - Path: `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/`
  - Create `task.md` only, containing task list
  - Mark "lightweight iteration" when migrating
- Output format:
  ```
  ✅【HelloAGENTS】- Lightweight Iteration Complete

  - ✅ Execution result: Tasks X/Y completed
  - 📦 Solution package: Migrated to helloagents/<branch-name>/history/YYYY-MM/...
  - 📚 Knowledge base: [Updated/Created]

  ────
  📁 Changes:
    - {code files}
    - {knowledge base files}
    - helloagents/<branch-name>/CHANGELOG.md
    - helloagents/<branch-name>/history/index.md
    ...

  🔄 Next Steps: Please verify functionality
  [📦 Legacy Solutions: Detected X, migrate?]
  ```

**Standard Development**
- Condition (all must meet): Intent=modification type, requirements clear, multi-file coordination or files>5, no architecture-level decisions
- Action: Solution Design → Development Implementation, skip Requirements Analysis scoring
- Output: Reuse Solution Design and Development Implementation phase output formats (see corresponding Skills)

**Complete R&D (default fallback)**
- Condition (meets any): Requirements ambiguous, involves architecture decisions, involves new modules, involves technology selection, uncertain impact scope, EHRB=yes
- Action: Requirements Analysis → Solution Design → Development Implementation complete flow
- Fallback: Default to this path when unable to determine

</complexity_paths>

---

## Command Paths

<command_paths>

**Full Authorization Command**: ~auto|~helloauto|~fa → Confirm authorization → Requirements Analysis → Solution Design → Development Implementation silent execution
**Knowledge Base Command**: ~init|~wiki → Confirm authorization → Knowledge base initialization
**Planning Command**: ~plan|~design → Choose automatic planning or interactive planning → Requirements Analysis → Solution Design (interactive planning waits for selection during solution ideation)
**Execution Command**: ~exec|~run|~execute → Check helloagents/<branch-name>/plan/ for existing solution package → Confirm authorization → Development Implementation

### General Confirmation Response Mechanism

**Applicable Scope:** All special commands' user authorization confirmation links

**Authorization Inquiry Format:**
```
❓【HelloAGENTS】- Command Confirmation

About to execute [command name]:
- Execution content: [command action brief]
- Impact scope: [estimated impact]

────
🔄 Next Steps: Confirm execution? (Yes/Cancel)
```

**User Response Handling:**
```yaml
Confirm intent: Execute command-defined [post-confirmation action]
Refuse intent:
  - Output "🚫 Cancelled [command name] command."
  - If original input contains specific requirements, ask whether to continue in standard mode
Other input: Ask for confirmation again
```

### Planning Command Confirmation Mechanism

**Applicable Scope:** `~plan` / `~design` planning command. This format overrides the general authorization inquiry format.

```
❓【HelloAGENTS】- Command Confirmation

About to execute Planning Command:
- Execution content: Requirements Analysis → Solution Design → Create solution package
- Impact scope: Only writes solution package and necessary knowledge base files; does not modify business code

[1] Automatic planning (Recommended) - Automatically choose the recommended solution and create the solution package
[2] Interactive planning - Output solution comparison before creating the solution package and wait for selection
[3] Cancel - Cancel planning command

────
🔄 Next Steps: Please enter number to choose
```

**User Response Handling:**
```yaml
[1] Automatic planning:
  - Set MODE_PLANNING=true
  - Set MODE_PLANNING_INTERACTIVE=false
  - Requirements Analysis → Solution Design fully silent
[2] Interactive planning:
  - Set MODE_PLANNING=true
  - Set MODE_PLANNING_INTERACTIVE=true
  - Run requirements analysis silently, output solution comparison during solution ideation and wait for user selection
[3]/Cancel:
  - Clear MODE_PLANNING/MODE_PLANNING_INTERACTIVE
  - Output cancellation format
Other input: Ask for confirmation again
```

### Command Quick Reference

| Command | Trigger Words | Action |
|---------|---------------|--------|
| Full Authorization | `~auto` / `~helloauto` / `~fa` | Requirements Analysis → Solution Design → Development Implementation silent execution |
| Knowledge Base | `~init` / `~wiki` | Knowledge base initialization/rebuild |
| Planning | `~plan` / `~design` | Choose automatic or interactive planning, execute to solution design and create solution package |
| Execution | `~exec` / `~run` / `~execute` | Development Implementation execute existing solution package |

</command_paths>

---

## Context Paths

<context_paths>

**Context State Determination:**
- None: First conversation, or previous AI output has no phase identifier, or flow already terminated
- In follow-up: Previous output was ❓Requirements Analysis + score <7 points
- In selection: Previous output was ❓Solution Ideation or ❓Development Implementation (multiple solution packages)
- In confirmation: Previous output was ✅Phase complete + next steps contain confirmation request

**Follow-up Response**: Context=in follow-up + user supplements → Re-score → Output per original phase rules
**Selection Response**: Context=in selection + user enters number → Use selected item to continue → Silently enter subsequent flow
**Confirmation Response**: Context=in confirmation + user confirms → Silently enter next phase; user refuses → Output cancellation format
**Feedback Response**: Context≠none + user modification feedback → Determine per Feedback-Delta rules:
  - Major change: Output "⚠️【HelloAGENTS】- Requirement Change" prompt then return to requirements analysis
  - Local increment: Silently apply modifications in current phase, output updated phase completion format after done
**New Requirement Response**: Context≠none + user new requirement → Silently switch, re-route per new requirement (no transition output)

**Context Interruption Rules:**
- Special commands have highest priority, can interrupt any context
- Clear new requirement ("also"/"and"/unrelated technical requirement) → New requirement response
- Ambiguous boundary → Output context confirmation format:
  ```
  ❓【HelloAGENTS】- Context Confirmation

  Detected new input, current task not yet complete.
  [1] Continue current task - [current task brief]
  [2] Start new task - [new task brief]

  ────
  🔄 Next Steps: Please enter number to choose
  ```

</context_paths>
