---
name: hello-subagent
description: Defines HelloAGENTS parallel subagent orchestration rules. Use during development implementation or multi-model collaboration when work can be split into multiple independent, clearly bounded, verifiable subtasks, guiding dispatch, context minimization, file boundary control, result aggregation, failure fallback, and final acceptance.
---

# Parallel Subagent Orchestration Rules

This Skill only extends the existing HelloAGENTS flow. It does not add phases, commands, or user-facing output formats.

---

## 1. Role Boundaries

```yaml
Main Agent Responsibilities:
  - Control Requirements Analysis → Solution Design → Development Implementation phases
  - Perform EHRB risk identification and user confirmation
  - Maintain proposal package task.md/why.md/how.md and history lifecycle
  - Split subtasks, assign file boundaries, track subagent status
  - Aggregate subagent results and perform final integration
  - Run verification, synchronize knowledge base, update CHANGELOG.md
  - Generate the only HelloAGENTS user-facing final output

Subagent Responsibilities:
  - Handle only the assigned single local task
  - Read only necessary context
  - Modify only explicitly authorized file scope
  - Return structured results, verification information, and risks
```

Subagents must not advance HelloAGENTS phases, migrate proposal packages, update final knowledge-base state, or output user-facing phase completion summaries.

---

## 2. Trigger Conditions

Enable subagents only when all conditions are met:

```yaml
Required Conditions:
  - Subtask count >= 2
  - No ordering dependency between subtasks
  - Each subtask can be understood and verified independently
  - File write scopes do not overlap
  - Shared interfaces, data structures, and state boundaries are clear
  - Requirements analysis or solution design has provided enough constraints
  - No unconfirmed EHRB risk exists
```

Recommended scenarios:
- Parallel implementation across independent modules
- Parallel investigation of independent test files or fault domains
- Clearly separated frontend, backend, test, and documentation task slices
- Multiple independent task groups exist in `task.md`
- Multi-model review needs parallel checks across different risk domains

Forbidden scenarios:
- Fine-tuning mode or small single-file changes
- Requirements remain ambiguous or architecture decisions are unfinished
- Multiple subtasks need frequent edits to the same file
- Multiple failures likely share the same root cause
- Subtasks have clear prerequisite ordering
- Production, permission, payment, destructive, or other EHRB risks are unconfirmed

---

## 3. Pre-Dispatch Checklist

Before dispatching, the main agent must complete:

```yaml
Checklist:
  - Read relevant constraints from current task.md/why.md/how.md
  - Identify allowed write files or directories for each subtask
  - Confirm write scopes are mutually exclusive across subagents
  - Confirm verification commands or acceptance criteria
  - Confirm subtasks do not require full main conversation context
  - Confirm the user has not requested stopping or waiting for confirmation
```

If any check fails, downgrade to sequential execution by the main agent.

---

## 4. Task Packet Format

Each dispatched subagent task must include:

```yaml
task_packet:
  id: Subtask ID
  goal: Single clear goal
  context:
    - Necessary requirement summary
    - Relevant proposal package excerpts
    - Relevant file paths
  allowed_scope:
    read:
      - Files/directories allowed for reading
    write:
      - Files/directories allowed for modification
  forbidden_scope:
    - Files/directories forbidden to modify
    - Interfaces/behaviors forbidden to change
  verification:
    - Verification command or manual acceptance standard
  output_contract:
    - status: DONE | BLOCKED | FAILED
    - summary: Summary of completed work
    - changed_files: Changed file list
    - verification: Verification result
    - risks: Risks or remaining issues
```

Keep context minimal. Do not send the full main conversation, unrelated proposals, or irrelevant history to subagents.

---

## 5. Write and Conflict Control

```yaml
Parallel Write Rules:
  - Each file can belong to only one subagent at a time
  - The same core interface, shared state, common type, or migration script is a conflict domain
  - Tasks inside a conflict domain must execute sequentially
  - Subagents must not modify files outside allowed_scope.write
  - Subagents must not revert user changes or other subagent changes
```

If overlapping file boundaries appear during execution, stop further parallel dispatch immediately; the main agent must split again or switch to sequential execution.

---

## 6. Relationship With Multi-Model Collaboration

`multi_model` focuses on review. `hello-subagent` focuses on task orchestration.

```yaml
Review Subagents:
  - Read-only by default
  - May analyze, review, output risks, and provide unified diff suggestions
  - Must not directly modify local files
  - Fit ANALYZE / DESIGN / DEVELOP cross-validation

Execution Subagents:
  - Used only in DEVELOP phase
  - Must have explicit allowed_scope.write
  - Are accepted and integrated by the main agent after completion
```

When using `collaborating-with-claude`, `collaborating-with-codex`, or `collaborating-with-gemini`, save `SESSION_ID`; follow-ups for the same subtask should reuse the original session.

---

## 7. Subagent Return Requirements

Subagents must return a structured summary:

```yaml
status: DONE | BLOCKED | FAILED
summary:
  - What was completed
changed_files:
  - path
verification:
  - command: Verification command run
    result: passed | failed | not_run
    note: Explanation
risks:
  - Risks or remaining issues; use none if empty
next:
  - Suggested next step for the main agent; use none if empty
```

`BLOCKED` must state the blocking reason, such as insufficient context, unfinished dependency, file conflict, unavailable environment, or unclear requirement.

---

## 8. Main Agent Acceptance

After receiving subagent results, the main agent must:

```yaml
Acceptance Steps:
  - Check whether status is DONE/BLOCKED/FAILED
  - Check whether changed_files exceeded scope
  - Check file or interface conflicts between subagents
  - Update task completion status against task.md
  - Run required verification commands or alternative verification
  - Aggregate risks and decide whether to continue, redispatch, execute sequentially, or ask the user
  - Finally synchronize knowledge base, `helloagents/<branch-name>/CHANGELOG.md`, and `helloagents/<branch-name>/history/index.md` by the main agent
```

Subagent results are intermediate material only. Final conclusions must be based on main-agent local verification.

---

## 9. Failure Fallback

```yaml
BLOCKED Handling Order:
  1. Determine whether context is insufficient
  2. Determine whether task splitting is invalid
  3. Determine whether hidden dependency or file conflict exists
  4. Determine whether verification environment is unavailable
  5. Redispatch once after adding context if reasonable
  6. If it still fails, downgrade to main-agent sequential execution or ask the user

FAILED Handling:
  - Record failure reason
  - Mark corresponding task.md task as [X] or [?]
  - Determine whether later tasks are affected
  - Continue per develop Skill failure handling rules
```

Do not mechanically redispatch the same failed task repeatedly.

---

## 10. Output Constraints

Subagent output does not use HelloAGENTS phase completion templates.

User-facing output is generated only by the main agent and must continue to follow `AGENTS.md` G6.1/G6.2/G6.3 format rules.

---

## 11. Path Mapping

This rule must not introduce new systems such as `.helloagents/`, `requirements.md`, `plan.md`, or `tasks.md`.

Use current HelloAGENTS paths:

```yaml
Requirement basis: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/why.md
Implementation plan: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/how.md
Task list: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/task.md
Execution archive: helloagents/<branch-name>/history/YYYY-MM/YYYYMMDDHHMM_<feature>/
Knowledge base: helloagents/<branch-name>/CHANGELOG.md, helloagents/<branch-name>/project.md, helloagents/<branch-name>/wiki/*
```

---

## 12. Priority

```yaml
Rule Priority:
  1. HelloAGENTS main flow and routing rules
  2. EHRB safety and user confirmation
  3. Proposal package lifecycle
  4. Knowledge base synchronization rules
  5. TDD and quality verification rules
  6. multi_model review rules
  7. hello-subagent parallel orchestration rules
```
