---
name: output-format
description: Phase output / exception / consultation / interactive / command completion format templates; read when any phase produces final output, exception, consultation Q&A, interactive inquiry, or command completion
---

# Output Format - Detailed Rules

**Applicable Scope:** All HelloAGENTS phase final outputs, exception states, consultation Q&A, interactive inquiries, and special command completion outputs.

**Relationship with bootstrap:** This Skill centrally maintains the G6.1-G6.4 and "Command Completion Output Format" sections originally in bootstrap; bootstrap only retains a minimal pointer to this Skill.

---

## G6.1 | Unified Output Format

<output_format>

⚠️ **CRITICAL - Mandatory Enforcement Rules:**

**1. MUST use standard format** - After any code/documentation changes complete, ALWAYS use one of the following formats:
   - Fine-tuning mode complete
   - Lightweight iteration complete
   - Development implementation complete
   - Command complete (~auto/~plan/~exec/~init)

**2. NO free text** - NEVER use unformatted free text to describe task completion

**3. Verification steps** - MUST self-check before output:
   ```
   [ ] Confirm current mode
   [ ] Confirm using correct format template
   [ ] Confirm includes 【HelloAGENTS】 identifier
   [ ] Confirm includes status symbol (✅/❓/⚠️/🚫/❌)
   [ ] Confirm file list uses vertical list
   ```

**4. Verification requirements** - After any write operation MUST restate:
   - What was changed
   - Where it was changed (file list)
   - Verification results

---

⚠️ **CRITICAL - List Display Specification (MUST follow):**

**All lists MUST use vertical list format:**

```
File List:
📁 Changes:
  - {file_path1}
  - {file_path2}
  ...
(When no changes: 📁 Changes: None)

Legacy Solution List:
📦 Legacy Solutions: Detected X unexecuted solution packages:
  - {solution_package_name1}
  - {solution_package_name2}
  ...
Do you need to migrate to history?

Other Lists (already compliant):
- Follow-up questions: 1. {question}...
- User options: [1] {option}...
- Failed tasks: - [X] {task}...
```

---

**Template Method Pattern:** The sole output structure when any phase completes.

**Rendering Structure:**
```
{status_symbol}【HelloAGENTS】- {phase_name}

[Phase output: ≤5 structured key points]

────
📁 Changes:
  - {file_path1}
  - {file_path2}
  ...

🔄 Next Steps: [≤2 sentences recommendation]

[📦 Legacy Solutions: (display per lifecycle Skill rules, if applicable)]
```

**Status Symbol Mapping:**
- ✅ : Phase successfully completed
- ❓ : Waiting for user input/selection
- ⚠️ : Warning/partial failure/needs user decision
- 🚫 : Operation cancelled
- ❌ : Serious error/routing failure
- 💡 : Consultation Q&A (technical consultation, concept explanation)

**Phase Names:**
- Requirements Analysis, Solution Ideation, Solution Design, Development Implementation
- Fine-tuning mode complete, Lightweight iteration complete
- Full authorization command complete, Planning command complete, Execution command complete, Knowledge base command complete
- Consultation Q&A

**Legacy Solution Reminder:**
  Trigger scenarios: Solution Design/Lightweight Iteration/Development Implementation/Planning Command/Execution Command/Full Authorization Command completion
  Execution rules: Scan and display per lifecycle Skill
  Display position: Optional slot at end of output format

**Applicable Scope:** Final summary output when phase completes (not applicable to follow-up questions, intermediate progress)

**Language Rules:** Follow G1, all natural language text generated in {OUTPUT_LANGUAGE}
</output_format>

---

## G6.2 | Exception Status Output Format

<exception_output_format>
**Applicable Scope:** Non-normal completion phase output (cancellation, errors, warnings, interruptions, etc.)

**EHRB Safety Warning:**
```
⚠️【HelloAGENTS】- Safety Warning

Detected high-risk operation: [risk type]
- Impact scope: [description]
- Risk level: [EHRB level]

────
⏸️ Waiting for confirmation: Continue execution? (Confirm risk/Cancel)
```

**Risk Escalation (upgrading from simplified mode):**
```
⚠️【HelloAGENTS】- Risk Escalation

Detected EHRB signal, upgraded from [fine-tuning mode/lightweight iteration] to [standard development/complete R&D].
- Risk type: [specific risk]

────
🔄 Next Steps: Will continue processing per [target mode] flow
```

**User Cancellation:**
```
🚫【HelloAGENTS】- Cancelled

Cancelled: [operation name]
────
🔄 Next Steps: [follow-up recommendations, if any]
```

**Process Termination (user-initiated termination):**
```
🚫【HelloAGENTS】- Terminated

Terminated: [phase name]
- Progress: [brief description of completed/incomplete work]

────
🔄 Next Steps: Can restart or perform other operations
```

**Routing/Validation Errors:**
```
❌【HelloAGENTS】- Execution Error

Error: [error description]
- Cause: [specific reason]

────
🔄 Next Steps: [fix recommendations]
```

**Partial Task Failure Inquiry:**
```
⚠️【HelloAGENTS】- Partial Failure

Partial tasks failed during execution:
- [X] [task1]: [failure reason]
- [X] [task2]: [failure reason]

[1] Continue - Skip failed tasks, complete subsequent steps
[2] Terminate - Stop execution, preserve current progress

────
🔄 Next Steps: Please enter number to choose
```

**Invalid Input Re-inquiry:**
```
❓【HelloAGENTS】- [current phase]

Invalid input, please choose again.
[Original option list]

────
🔄 Next Steps: Please enter valid option
```

**Insufficient Scoring Follow-up (breaking silence in push mode):**
```
❓【HelloAGENTS】- Requirements Analysis

[Push mode] Requirement completeness score X/10 points, need to supplement information to continue.

1. [question1]
2. [question2]
...

Please supplement and reply, or enter "cancel" to terminate current command.
```
</exception_output_format>

---

## G6.3 | Consultation Q&A Output Format

<qa_output_format>

**Applicable Scope:** All direct answer scenarios (technical consultation, greetings, confirmations, etc., non-development flow interactions)

**Core Constraints:**
- MUST use `💡【HelloAGENTS】- Consultation Q&A` format
- Length constraints: Simple ≤2 sentences | Typical ≤5 key points | Complex = overview + ≤5 key points

**Output Structure:**
```
💡【HelloAGENTS】- Consultation Q&A

[Answer content - follow length constraints]
```

**Example:**
```
💡【HelloAGENTS】- Consultation Q&A

Client errors are handled in the connectToServer function at src/services/process.ts:712. After connection failure, it retries 3 times, marking as failed status if all attempts fail.
```

</qa_output_format>

---

## G6.4 | Interactive Inquiry Output Format

<interactive_output_format>

**Applicable Scope:** Interactive scenarios requiring user selection/confirmation (not phase completion, not exception status)

**General Template:**
```
❓【HelloAGENTS】- {scenario name}

[Situation explanation - ≤3 sentences]

[1] {option1} - {explanation}
[2] {option2} - {explanation}

────
🔄 Next Steps: {guidance text}
```

**Core Constraints:** ❓ status symbol | 2-4 options | explanation ≤1 sentence

**Special Scenario Supplements:**

1. **Requirement Change Prompt** (Feedback-Delta rules triggered):
   ```
   ⚠️【HelloAGENTS】- Requirement Change

   Detected major requirement change: {change type}
   ────
   🔄 Next Steps: Will re-execute requirements analysis
   ```

2. **Context Confirmation/Command Confirmation** - See format in routing Skill

3. **Other Interactive Scenarios** - See format in corresponding Skill files (solution ideation selection, test failures, code quality inquiries, etc.)

</interactive_output_format>

---

## Special Command Completion Output Format

**Description:** All command completion outputs strictly follow G6.1 unified output format, below defines each command's phase content filling rules.

**Full Authorization Command Complete:**
```
✅【HelloAGENTS】- Full Authorization Command Complete

- ✅ Execution path: Requirements Analysis → Solution Design → Development Implementation
- 📊 Execution result: Requirement score X/10, tasks Y/Z completed
- 💡 Key decisions: [decision summary, if any]

────
📁 Changes:
  - {code files}
  - {knowledge base files}
  - {solution package files}
  - helloagents/<branch-name>/CHANGELOG.md
  - helloagents/<branch-name>/history/...
  ...

🔄 Next Steps: Full authorization command ended, ready to receive new instructions anytime
📦 Legacy Solutions: [Scan and display per lifecycle Skill]
```

**Planning Command Complete:**
```
✅【HelloAGENTS】- Planning Command Complete

- ✅ Execution path: Requirements Analysis → Solution Design
- 📋 Requirements analysis: Score X/10, [key objectives]
- 📝 Solution planning: [solution type], X tasks

────
📁 Changes:
  - helloagents/<branch-name>/plan/{solution_package_dir}/why.md
  - helloagents/<branch-name>/plan/{solution_package_dir}/how.md
  - helloagents/<branch-name>/plan/{solution_package_dir}/task.md

🔄 Next Steps: Solution package generated, enter ~exec to execute if needed
📦 Legacy Solutions: [Scan and display per lifecycle Skill, if any]
```

**Execution Command Complete:**
```
✅【HelloAGENTS】- Execution Command Complete

- ✅ Executed solution: [solution package name]
- 📊 Execution result: Tasks Y/Z completed
- 🔍 Quality verification: [test result summary]

────
📁 Changes:
  - {code files}
  - {knowledge base files}
  - helloagents/<branch-name>/CHANGELOG.md
  - helloagents/<branch-name>/history/...
  ...

🔄 Next Steps: Execution command ended, ready to receive new instructions anytime
📦 Legacy Solutions: [Scan and display per lifecycle Skill]
```

**Knowledge Base Command Complete:** See format in kb Skill
