---
name: develop
description: Development implementation phase detailed rules; read when entering development implementation; includes execution flow, code specifications, consistency audit, solution package migration
---

# Development Implementation - Detailed Rules

**Goal:** Execute code changes per task list in solution package, synchronize knowledge base updates, migrate to history/

**Prerequisites:** Solution package exists in `plan/` directory awaiting execution

**Backup Protection:** Recommend creating Git backup branch or manually backing up code directory before execution

---

## Mandatory Pre-entry Check

<p3_entry_gate>
**Description:** Even if routing determines entering development implementation, this check still verifies legitimacy (double insurance)

**Sole Legal Conditions for Development Implementation (meet any):**

```yaml
Condition A - Confirmation after solution design complete:
  Verification method: Previous AI output in conversation history was solution design complete AND current user input is explicit confirmation

Condition B - Full authorization command:
  Verification method: MODE_FULL_AUTH status=true

Condition C - Execution command:
  Verification method: MODE_EXECUTION status=true
```

**Verification Failure Handling:**
```
IF doesn't meet any condition:
  Output: "❌ Routing Error: Entering development implementation requires meeting prerequisites. Current conditions not met, re-routed."
  Execute: Re-determine current user message per routing priority
  Terminate: Development implementation flow
```
</p3_entry_gate>

---

## Execution Steps

**Important:** All file operations follow G5 silent execution specification

### Step 1: Determine Solution Package to Execute

```yaml
Full authorization command (MODE_FULL_AUTH=true):
  - Read CREATED_PACKAGE variable (solution package path set during solution design phase)
  - Check if solution package exists and is complete
    - Exists and complete → Use this solution package, set CURRENT_PACKAGE = CREATED_PACKAGE
    - Doesn't exist or incomplete → Output error format per G6.2 and stop
  - Ignore other legacy solution packages in plan/

Interactive confirmation mode/Execution command (MODE_EXECUTION=true):
  - Scan all solution packages under plan/ directory
  - No solution package exists → Output error format per G6.2 and stop
  - Solution package incomplete → Output error format per G6.2 and stop
  - Single complete solution package → Set CURRENT_PACKAGE, continue execution
  - Multiple solution packages → List inventory, wait for user selection
    - User enters valid number (1-N) → Set CURRENT_PACKAGE, continue execution
    - User enters cancel/refuse → Output cancellation format per G6.2, flow terminates
    - Invalid input → Ask again

Exception output examples:
  Solution package doesn't exist:
    ```
    ❌【HelloAGENTS】- Execution Error

    Error: No executable solution package found
    - Cause: plan/ directory is empty or doesn't exist

    ────
    🔄 Next Steps: Please create solution using ~plan command first, or enter solution design phase
    ```

  Solution package incomplete:
    ```
    ❌【HelloAGENTS】- Execution Error

    Error: Solution package incomplete
    - Solution package: [solution package name]
    - Missing files: [why.md/how.md/task.md]

    ────
    🔄 Next Steps: Please supplement missing files or recreate solution package
    ```
```

### Step 2: Check Knowledge Base Status and Handle

Execution method:
- Determine per G10 quick decision tree
- If need to create/rebuild knowledge base → Read `kb` Skill to execute complete flow

### Step 3: Read Knowledge Base and Acquire Project Context

Execution method:
- Execute per G10 quick flow (check knowledge base first → scan codebase if insufficient)
- If need detailed rules → Read `kb` Skill

### Step 4: Read Current Solution Package

Read `plan/YYYYMMDDHHMM_<feature>/task.md` and `why.md`

### Step 5: Execute Code Changes Per Task List

```yaml
Execution rules:
  - Strictly execute item by item per task.md
  - If a task matches TDD applicability (new feature, bug fix, behavior change, core logic change, or test strategy design), read the `tdd` Skill first
  - Complete the matching RED task by default before changing production code
  - When constrained by legacy code, missing test frameworks, unstable reproduction environments, or user constraints, record the constraint, alternative verification method, and TDD-EXEMPT reason before continuing with the existing verification strategy

Task success handling:
  - After each task executes successfully, immediately update status from [ ] to [√]

Task skip handling (status update to [-]):
  - Prerequisite tasks this task depends on failed
  - Task conditions not met
  - Task already covered by other task implementations

Task failure handling (status update to [X]):
  - Record error information (for adding notes before migration)
  - Continue executing subsequent tasks
  - After all tasks complete, if failures exist:
    - Interactive confirmation mode/Execution command: List failure inventory, ask user decision
      - User chooses continue → Continue subsequent steps
      - User chooses terminate → Output "Terminated development implementation", flow terminates
    - Full authorization command: List failed tasks in summary, clear MODE_FULL_AUTH status

Code editing techniques:
  - Large file handling (≥2000 lines): Grep locate → Read(offset,limit) → Edit precise modification
  - Each Edit only modifies single function/class
```

### Step 6: Code Security Check

Check content:
- Unsafe patterns (eval, exec, SQL concatenation, etc.)
- Hardcoded sensitive information
- EHRB risk avoidance

### Step 7: Quality Check and Testing

```yaml
Test execution: Run test tasks defined in task.md, or project's existing test suite

TDD gate (strictly enforce when applicable):
  - RED: The test must fail first, and the failure reason must match the target behavior
  - GREEN: Write only the minimum implementation needed for related tests to pass
  - REFACTOR: Refactor only after tests pass, then rerun related tests
  - Anti-pattern check: Do not test mock behavior, do not add test-only production interfaces, and prefer fakes/real components/integration tests when mocks become complex

Test failure handling rules (strictly enforce):
  ⛔ Blocking tests (core functionality):
    - Failure MUST immediately stop execution
    - Output critical error format
    - Wait for user explicit decision (fix/skip/terminate)
    - Prohibit auto-skip

  ⚠️ Warning tests (important functionality):
    - Mark in summary when failed
    - Continue executing subsequent steps

  ℹ️ Informational tests (secondary functionality):
    - Record in summary when failed
    - Continue executing subsequent steps
```

**⛔Blocking Test Failure Output Format:**
```
❌【HelloAGENTS】- Blocking Test Failure

⛔ Core functionality test failed, must handle before continuing:
- Failed test: [test name]
- Error message: [error summary]

[1] Fix and retry - Attempt to fix issue then retest
[2] Skip and continue - At your own risk, ignore this error and continue execution
[3] Terminate execution - Stop development implementation

────
🔄 Next Steps: Please enter number to choose
```

### Step 8: Synchronize Update Knowledge Base

**Important:** MUST complete solution package content reading before step 12 migrates solution package

Execution method: Read `kb` Skill to execute complete knowledge base synchronization rules

### Step 9: Update CHANGELOG.md

Determine version number per G7 version management rules

### Step 10: Consistency Audit

<consistency_audit>
**Audit Timing:** Execute immediately after P3 phase completes knowledge base operations

**Audit Content:**
1. **Completeness**: Documentation covers all modules, essential files and charts complete
2. **Consistency**: APIs/data models consistent with code, no omissions, duplicates, dead links

**Reality Priority (conflict resolution mechanism):**
```
1. Code is sole source of execution reality (Ground Truth)
   → Runtime behavior, API signatures, data structures based on code

2. Default correction direction: Correct knowledge base to conform to code
   → When inconsistency discovered, MUST update documentation to reflect code's objective facts

3. Exceptions (correct code):
   - Knowledge base is recent P2/P3 solution package (just designed solution)
   - Code has obvious errors (Bug)
   - Error information points to code issue

4. When in doubt: Bidirectional verification, prioritize trusting most recent code changes
```
</consistency_audit>

### Step 11: Code Quality Check (Optional)

```yaml
Execution content: Analyze code files, identify quality issues

If issues found:
  Interactive confirmation mode:
    - Output optimization suggestion inquiry format
    - User confirms → Execute optimization, update documentation, retest
    - User refuses → Skip optimization, continue subsequent steps
  Full authorization command/Execution command:
    - List suggestions in summary (don't execute)

Commit association: Execute per project specifications if commit needed
```

**Code Quality Optimization Suggestion Inquiry Format:**
```
❓【HelloAGENTS】- Code Quality

Found following optimizable items:
1. [Optimization suggestion 1] - [Impact scope/files]
2. [Optimization suggestion 2] - [Impact scope/files]

[1] Execute optimization - Apply above optimization suggestions
[2] Skip - Keep current state, continue subsequent steps

────
🔄 Next Steps: Please enter number to choose
```

### Step 12: Migrate Executed Solution Package to history/

<plan_migration>

⚠️ **CRITICAL - Mandatory Enforcement Rules:**

**Cannot skip:** This step is atomic operation at end of this phase

**Execution Rules:**

1. Update task.md task status and notes:
   - All tasks update to actual execution results ([√]/[X]/[-]/[?])
   - Add notes below non-[√] status tasks (format: `> Note: [reason]`)
   - If multiple failed/skipped tasks, can add execution summary section at end

2. Migrate to history directory:
   - Move solution package directory from plan/ to under history/YYYY-MM/
   - YYYY-MM extracted from solution package directory name (e.g., 202511201200_xxx → 2025-11)
   - Complete path after migration: history/YYYY-MM/YYYYMMDDHHMM_<feature>/
   - Migration operation automatically deletes source directory under plan/
   - Name conflict handling: Force overwrite old solution package in history/

3. Update history index: `history/index.md`

**Warning:** This operation will invalidate source file paths under plan/, ensure step 8 has completed content reading
**Cannot skip:** This step is atomic operation at end of this phase
</plan_migration>

### Step 13: Multi-Model Acceptance Prompt (Optional)

```yaml
Trigger timing: After solution package migration completes, before outputting final summary
Applicable modes: Interactive confirmation mode / Execution command

Full authorization command handling:
  - Skip prompt, output completion summary directly
  - Append to end of final summary: "💡 Multi-model acceptance: To verify consistency between code implementation and solution package, trigger separately after completion"

Prompt format:
  ❓【HelloAGENTS】- Multi-Model Acceptance

  Development implementation complete. You may perform multi-model acceptance testing to verify
  whether actual code implementation matches the solution package.

  [1] Start Multi-Model Acceptance - Read `multi_model` Skill, execute consistency review and risk classification per DEVELOP phase rules
  [2] Skip - Output completion summary directly

  ────
  🔄 Next Steps: Enter option number to select

User selection handling:
  [1] Start multi-model acceptance:
    - Read `multi_model` Skill, execute per DEVELOP phase collaboration rules:
      - External model reviews actual code changes against migrated task.md in history/
      - No-write principle: Append to prompt "OUTPUT: Unified Diff Patch ONLY."
      - Output risk classification report (P0 Must Fix / P1 Should Fix / P2 Note)
    - Output phase completion summary after acceptance completes
  [2] Output phase completion summary directly
```

---

## Code Specification Requirements

<code_standards>
**Applicable Scope:** All code changes in P3 phase

**Specification Requirements:**
- **File top comments:** Before import statements, project's existing comment style, 1-3 sentences explaining module purpose
- **All code comments:** MUST be generated in {OUTPUT_LANGUAGE}
- **Code style:** Follow project's existing naming conventions and format specifications
</code_standards>

---

## Development Implementation Output Format

⚠️ **CRITICAL - Mandatory Requirements:**
- ALWAYS use G6.1 unified output format
- NEVER use free text to replace standard format
- MUST verify format completeness before output

### When Waiting for User to Select Solution Package (step 1 multiple solution packages)

```
❓【HelloAGENTS】- Development Implementation

Detected multiple solution packages, please select execution target:

[1] YYYYMMDDHHMM_<feature1> - [Overview description]
[2] YYYYMMDDHHMM_<feature2> - [Overview description]
[3] YYYYMMDDHHMM_<feature3> - [Overview description]

────
🔄 Next Steps: Please enter solution package number (1/2/3)
```

### When Phase Complete

Strictly call G6.1 unified output format, fill following data:

1. **Phase Name:** `Development Implementation`
2. **Phase Specific Content (≤5 key points):**
   - 📚 Knowledge base status
   - ✅ Execution result: Task count and status statistics
   - 🔍 Quality verification: Consistency audit, test results
   - 💡 Code quality optimization suggestions (if any)
   - 📦 Migration info: Migrated to `history/YYYY-MM/YYYYMMDDHHMM_<feature>/`
3. **File Change List:**
   ```
   📁 Changes:
     - {code files}
     - {knowledge base files}
     - helloagents/CHANGELOG.md
     - helloagents/history/index.md
     ...
   ```
4. **Next Step Suggestions:**
   - Interactive confirmation mode / Execution command: Output multi-model acceptance prompt (see step 13 "Prompt format")
   - Full authorization command: Append multi-model acceptance hint to summary
5. **Legacy Solution Reminder:** Scan plan/ directory per G11, display if legacy solution packages exist

---

## Phase Transition Rules

```yaml
After completing all actions (step 12 migration complete):
  Interactive confirmation mode / Execution command:
    - Execute step 13 multi-model acceptance prompt
    - User selects [1] → Read multi_model Skill, execute acceptance → Output acceptance report → Output completion summary
    - User selects [2] → Output completion summary directly → Development implementation ends
  Full authorization command:
    - Skip step 13 prompt → Output overall summary (with multi-model acceptance hint at end) → Flow ends
  Variable cleanup: CURRENT_PACKAGE will automatically clean during legacy solution scan (per G11 rules)

Exceptional situations (test failures/user raises issues):
  Interactive confirmation mode: Mark in output, wait for user decision
  Full authorization command/Execution command: Mark test failure in summary, flow ends normally
  Subsequent user messages handled per routing priority
```

