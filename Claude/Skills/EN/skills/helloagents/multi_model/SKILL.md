---
name: multi_model
description: Defines trigger conditions, execution rules, and constraints for multi-model collaboration across ANALYZE/DESIGN/DEVELOP phases. Read this Skill when multi-model review is triggered.
---

# Multi-Model Collaboration Analysis and Review Rules

This module defines the unified behavior of multi-model collaboration in ANALYZE / DESIGN / DEVELOP phases and command paths (~plan/~exec).

---

## Rule Overview

```yaml
Rule Name: Multi-Model Collaboration Analysis and Review Rules
Scope:
  - ANALYZE: Cross-validation of project context and technical risks
  - DESIGN: Cross-review of proposals and implementation plan gate
  - DEVELOP: Consistency review and risk classification after completion
  - Command Paths: Multi-model review steps for ~plan / ~exec
Core Goals:
  - Reduce single-model bias risk
  - Complete cross-validation before key decisions
  - Ensure traceable consistency between proposal documents and code implementation
```

---

## Collaboration Strategy Switches

```yaml
Read Configuration:
  - MULTI_MODEL_POLICY (BALANCED / STRICT)
  - SIMPLE_TASK_NO_COLLAB_CONFIRM (0 / 1)
  - PHASE2_HARD_STOP_CONFIRM (0 / 1)
  - FORCE_MM_LIGHTWEIGHT_MIN_FILES (integer, default 2)

BALANCED:
  - Trigger multi-model collaboration based on risk
  - Simple tasks can skip collaboration by default

STRICT:
  - Enable multi-model collaboration by default
  - If simple tasks skip collaboration, determine if confirmation is required per SIMPLE_TASK_NO_COLLAB_CONFIRM

Force Escalation Linkage:
  - When user has confirmed enabling multi-model collaboration AND estimated changed files >= FORCE_MM_LIGHTWEIGHT_MIN_FILES:
    - R1 fast process must be upgraded to R2 simplified process
    - Enter ANALYZE → DESIGN to ensure proposal package is generated/reviewed

PHASE2_HARD_STOP_CONFIRM = 1:
  - After DESIGN phase outputs final implementation plan, must ask:
    "Shall I proceed with this plan? (Y/N)"
  - Must not proceed to DEVELOP execution without an explicit Y
```

---

## Boundary With hello-subagent

```yaml
Relationship:
  - multi_model handles multi-model analysis/review/acceptance
  - hello-subagent handles parallel subtask orchestration, context trimming, file boundaries, and return contracts

Trigger Linkage:
  - When multi-model review can be split into independent risk domains:
    - Read the `hello-subagent` Skill
    - Generate review-type subtask packets per its rules
    - Review subagents remain read-only and must not modify local files directly

Boundary Constraints:
  - multi_model no-write principle has priority over hello-subagent execution-subagent rules
  - Multi-model outputs are only recommendations, risk reports, or unified diffs
  - Final adoption, code modification, and knowledge-base synchronization remain main-agent responsibilities
```

---

## Phase-Specific Collaboration Rules

### ANALYZE Phase

```yaml
Trigger Conditions:
  - TASK_COMPLEXITY = complex
  - Or user explicitly requests multi-model cross-validation

Execution:
  - Request external model for risk cross-check based on analysis results
  - Output consensus items and divergence items; divergences deferred to DESIGN phase for arbitration
```

### DESIGN Phase (Phase2)

```yaml
Goal:
  - Cross-evaluate candidate proposals and converge into an implementation plan

Execution:
  - Primary combination: claude + gemini
  - Conflict arbitration: codex (added as needed)
  - Output step-by-step implementation plan and key risks

Hard Stop (optional):
  - Force Y/N gate when PHASE2_HARD_STOP_CONFIRM = 1
```

### DEVELOP Phase (Phase3/Phase4)

```yaml
Goal:
  - Perform consistency and risk review before and after coding implementation

Execution:
  - Prototype suggestions are for reference only, not directly applied
  - Execute consistency review after local changes:
    Compare proposal/tasks against code implementation

Risk Classification:
  - P0 / Must Fix: Security vulnerabilities, critical logic errors (blocking)
  - P1 / Should Fix: Quality and stability risks (warning)
  - P2 / Note: Optimization suggestions (informational)
```

---

## Execution Constraints (CRITICAL)

```yaml
No-Write Principle:
  - External models are for analysis/review only, not direct local file modification
  - Prompt must append:
    "OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications."

Session Continuity:
  - Save SESSION_ID on first call
  - Prefer reusing SESSION_ID within the same review chain

Output Requirements:
  - Collaboration mode (enabled/not enabled)
  - Call summary (model, success, SESSION_ID)
  - Consensus conclusions / conflict conclusions
  - Final recommendations and next steps
```

---

## Failure Fallback

```yaml
Single Model Failure:
  - Record failure reason
  - Continue with remaining models
  - Output "partial collaboration failure"

All Models Failed:
  - Fall back to local single-model analysis/review
  - Output warning and prompt to check bridge tool availability
```
