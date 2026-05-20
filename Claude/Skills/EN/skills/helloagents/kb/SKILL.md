---
name: kb
description: Complete knowledge base management rules; read when ~init command or knowledge base missing; includes creation, synchronization, audit, context acquisition rules
---

# Knowledge Base Management - Complete Rules

## Knowledge Base Architecture

**File Structure:**
```plaintext
helloagents/                       # HelloAGENTS workspace container
└── <branch-name>/                 # Current branch knowledge base root (SSOT)
    ├── CHANGELOG.md               # Version history (Keep a Changelog)
    ├── project.md                 # Technical conventions
    ├── wiki/                      # Core documentation
    │   ├── overview.md            # Project overview
    │   ├── arch.md                # Architecture design
    │   ├── api.md                 # API manual
    │   ├── data.md                # Data models
    │   └── modules/<module>.md
    ├── plan/                      # Change workspace
    │   └── YYYYMMDDHHMM_<feature>/
    │       ├── why.md             # Change proposal
    │       ├── how.md             # Technical design
    │       └── task.md            # Task list
    └── history/                   # Completed changes archive
        ├── index.md
        └── YYYY-MM/YYYYMMDDHHMM_<feature>/
```

**Path Conventions:**
- In this ruleset, `helloagents/<branch-name>/` denotes the local knowledge base root for the current branch; `<branch-name>` is the current git branch name or workspace alias
- In this ruleset, `plan/`, `wiki/`, `history/` all refer to complete paths under `helloagents/<branch-name>/`
- All knowledge base files MUST be created under the `helloagents/<branch-name>/` directory

---

## Core Terminology Details

- **SSOT** (Single Source of Truth): Single source of truth (knowledge level), refers to knowledge base
  - *Note:* When SSOT conflicts with code, SSOT is considered "outdated" and needs updating based on code (execution facts)
- **Knowledge Base**: Complete project documentation collection (`CHANGELOG.md`, `project.md`, `wiki/*`)
- **EHRB** (Extreme High-Risk Behavior): Extreme high-risk behavior
- **ADR** (Architecture Decision Record): Architecture decision record
- **MRE** (Minimal Reproducible Example): Minimal reproducible example
- **Solution Package**: Complete solution unit
  - **Directory structure**: `YYYYMMDDHHMM_<feature>/`
  - **Required files**: `why.md` + `how.md` + `task.md`
  - **Completeness check**: Required files exist, non-empty, task.md has at least 1 task item

---

## Quality Check Dimensions

1. **Completeness**: Whether required files and sections exist
2. **Format**: Whether Mermaid charts/Markdown format is correct
3. **Consistency**: Whether API signatures/data models consistent with code
4. **Security**: Whether contains sensitive information (keys/PII)

**Issue Grading:**
- **Minor** (can continue): Missing non-critical files, non-standard format, outdated descriptions
- **Severe** (needs handling): Core files missing, seriously out of sync (>30%), contains sensitive information

---

## Project Context Acquisition Strategy

<context_acquisition_rules>
**Step 1: Check knowledge base first (if exists)**
- Core files: `helloagents/<branch-name>/project.md`, `helloagents/<branch-name>/wiki/overview.md`, `helloagents/<branch-name>/wiki/arch.md`
- Select as needed: `helloagents/<branch-name>/wiki/modules/<module>.md`, `helloagents/<branch-name>/wiki/api.md`, `helloagents/<branch-name>/wiki/data.md`

**Step 2: Knowledge base doesn't exist/insufficient info → Comprehensive codebase scan**
- Use Glob to get file structure
- Use Grep to search key information
- Acquire: Architecture, tech stack, module structure, technical constraints
</context_acquisition_rules>

---

## Knowledge Base Synchronization Rules

<kb_sync_rules>
**Trigger Timing:** After code changes, MUST immediately synchronize knowledge base updates

**Step 1 - Module Specification Update:**
- Read current solution package `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/why.md` **Core Scenarios** section (read before migration)
- Extract requirements and scenarios (requirements need to mark owning module)
- Update `helloagents/<branch-name>/wiki/modules/<module>.md` **Specifications** section
  - Does not exist → Append
  - Already exists → Update

**Step 2 - Update by Change Type:**
- API changes → Update `helloagents/<branch-name>/wiki/api.md`
- Data model changes → Update `helloagents/<branch-name>/wiki/data.md`
- Architecture changes/new modules → Update `helloagents/<branch-name>/wiki/arch.md`
- Module index changes → Update `helloagents/<branch-name>/wiki/overview.md`
- Technical convention changes → Update `helloagents/<branch-name>/project.md`

**Step 3 - ADR Maintenance (if includes architecture decisions):**
- Extract ADR information (read from `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/how.md` **Architecture Decision ADR** section before migration)
- Append to **Major Architecture Decisions** table in `helloagents/<branch-name>/wiki/arch.md`
- Link to `helloagents/<branch-name>/history/YYYY-MM/YYYYMMDDHHMM_<feature>/how.md#adr-xxx`
- **Note:** The history/ link written at this time is a pre-calculated path

**Step 4 - Cleanup:**
- Delete outdated information, deprecated APIs, removed modules

**Step 5 - Defect Retrospective (fix scenario specific):**
- Add "Known Issues" or "Notes" in module documentation
- Record root cause, fix solution, prevention measures
</kb_sync_rules>

---

## Knowledge Base Missing Handling

<kb_missing_handler>
**STEP 1: Check if core files exist**
- `helloagents/<branch-name>/CHANGELOG.md`, `helloagents/<branch-name>/project.md`, `helloagents/<branch-name>/wiki/*.md`

**STEP 2: Knowledge base does not exist**
Handle by phase:
```yaml
Requirements Analysis Phase:
  - Only flag issue, don't create knowledge base
  - Prompt in summary "Knowledge base missing, recommend executing ~init command first"

Solution Design/Development Implementation Phase:
  - Comprehensively scan codebase and create complete knowledge base:
    - Root directory: `helloagents/<branch-name>/CHANGELOG.md`, `helloagents/<branch-name>/project.md`
    - `helloagents/<branch-name>/wiki/`: overview.md, arch.md, api.md, data.md
    - `helloagents/<branch-name>/wiki/modules/`: <module>.md (each module)
    - Large projects (determined per G4) batch process (≤20 modules per batch)
```

**STEP 3: Knowledge base exists**
```yaml
Execute quality pre-check:
  Severe issues → Comprehensively scan and rebuild (Solution Design/Development Implementation phase)
  Minor issues → Continue flow
```
</kb_missing_handler>

---

## Legacy Solution Handling

### User Selection Migration Flow

<legacy_plan_migration>
**Applicable Scenario:** Batch processing flow after user responds "confirm migration"

**Step 1 - User selects migration scope:**

List all legacy solution packages, ask user to choose:
```
Detected X legacy solution packages, please select migration method:
- Enter "all" → Migrate all legacy solution packages
- Enter solution package numbers (e.g., 1, 1,3, 1-3) → Migrate specified solution packages
- Enter "cancel" → Keep all legacy solution packages

Solution package list:
[1] 202511201300_logout
[2] 202511201400_profile
[3] 202511201500_settings
```

**User Response Handling:**
- "all" → Migrate all
- Single number (e.g., 1) → Migrate 1st
- Multiple numbers (e.g., 1,3) → Migrate specified
- Number range (e.g., 1-3) → Migrate 1st to 3rd
- "cancel" → Keep all
- Other input → Ask again

**Step 2 - Migrate selected solution packages one by one:**

```yaml
for each selected solution package:
  1. Update task status: All task statuses update to [-]
     Add at top: > **Status:** Not executed (user cleanup)

  2. Migrate to history directory:
     - Move from `helloagents/<branch-name>/plan/` to `helloagents/<branch-name>/history/YYYY-MM/`
     - YYYY-MM extracted from solution package directory name
     - Name conflict: Force overwrite

  3. Update history index: `helloagents/<branch-name>/history/index.md` (mark "not executed")
```

**Step 3 - Output migration summary:**
```
✅ Migrated X solution packages to `helloagents/<branch-name>/history/`:
  - 202511201300_logout → helloagents/<branch-name>/history/2025-11/202511201300_logout/
  - 202511201500_settings → helloagents/<branch-name>/history/2025-11/202511201500_settings/
📦 Remaining Y solution packages kept in `helloagents/<branch-name>/plan/`:
  - 202511201400_profile
```
</legacy_plan_migration>

### Legacy Solution Scan and Reminder Mechanism

<legacy_plan_scan>
**Trigger Timing:**
- After solution package creation: Solution Design complete, Planning command complete, Lightweight iteration complete
- After solution package migration: Development Implementation complete, Execution command complete, Full authorization command complete

**Scan Logic:**
1. Scan all solution package directories under `helloagents/<branch-name>/plan/` directory
2. Exclude solution package executed this time (read CURRENT_PACKAGE variable)
3. Clear CURRENT_PACKAGE variable
4. Remaining solution packages are legacy solutions

**Output Position:** Auto-inject to end slot of output-format Skill G6.1 output format

**Output Format:**
```
📦 `helloagents/<branch-name>/plan/` Legacy Solutions: Detected X legacy solution packages ([list]), do you need to migrate to history?
```

List format: YYYYMMDDHHMM_<feature> (one per line, max 5, show "...and X more" if exceeds)

**User Response:**
- Confirm migration → Execute batch migration flow
- Refuse/ignore → Keep in `helloagents/<branch-name>/plan/` directory
</legacy_plan_scan>

---

## ~init / ~wiki Command Completion Summary Format

Strictly follow output-format Skill G6.1 unified output format:

```
✅【HelloAGENTS】- Knowledge Base Command Complete

- 📚 Knowledge base status: [Created/Updated/Rebuilt]
- 📊 Operation summary: Scanned X modules, created/updated Y documents
- 🔍 Quality check: [Check results, if issues exist]

────
📁 Changes:
  - {knowledge base files}
  - helloagents/<branch-name>/CHANGELOG.md
  - helloagents/<branch-name>/project.md
  ...

🔄 Next Steps: Knowledge base operation complete, can proceed with other tasks
```
