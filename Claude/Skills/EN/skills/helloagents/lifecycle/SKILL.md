---
name: lifecycle
description: Solution package lifecycle and state variable management; read when creating/migrating solution packages, scanning legacy solutions, or switching state variables
---

# Solution Package Lifecycle Management - Detailed Rules

**Applicable Scope:** Solution package creation (Solution Design / Lightweight Iteration), migration (Development Implementation P3 step 12), legacy scan (phase completion), state variable management.

---

## G11 | Solution Package Lifecycle

<plan_package_lifecycle>

**Task Status Symbols:**
- `[ ]` Pending
- `[√]` Completed
- `[X]` Failed
- `[-]` Skipped
- `[?]` To be confirmed

**Create New Solution Package (handle name conflicts):**
```yaml
Path: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/
Conflict handling:
  1. Check if directory exists
  2. Does not exist → Create directly
  3. Exists → Use version suffix _v2, _v3...
```

**Executed Solution Package (P3 phase mandatory migration):**
```yaml
1. Update task.md task status (use above task status symbols)
2. Migrate to helloagents/<branch-name>/history/YYYY-MM/ (preserve directory name, overwrite if same name exists)
3. Update helloagents/<branch-name>/history/index.md
```

**Legacy Solution Scan:**
```yaml
Trigger timing (meets any):
  - After solution package creation: Solution Design complete, Planning command complete, Lightweight iteration complete
  - After solution package migration: Development Implementation complete, Execution command complete, Full authorization command complete

Scan rules:
  - Scan: All solution packages under helloagents/<branch-name>/plan/ directory
  - Exclude: Solution package created/executed this time
  - Condition: Only output prompt when ≥1 legacy solution package detected

Output format:
  📦 Legacy Solutions: Detected X unexecuted solution packages:
    - {solution_package_name1}
    - {solution_package_name2}
    ...
  Do you need to migrate to history?
```

</plan_package_lifecycle>

---

## G12 | State Variable Management

```yaml
CREATED_PACKAGE: Solution package path created during solution design phase
  Set: After detailed planning complete and created
  Clear: After read in Development Implementation step 1 or process terminated

CURRENT_PACKAGE: Currently executing solution package path
  Set: After determining solution package in Development Implementation step 1
  Clear: After solution package migrated to history/

MODE_FULL_AUTH: Full authorization command active state
MODE_PLANNING: Planning command active state
MODE_PLANNING_INTERACTIVE: Interactive planning active state
MODE_EXECUTION: Execution command active state
```
