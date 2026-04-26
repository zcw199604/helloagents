---
name: tdd
description: Test-driven development quality rules; use when a task involves new features, bug fixes, observable behavior changes, core logic changes, public API/method additions, or test strategy design; defines TDD applicability, RED-GREEN-REFACTOR, exemptions, testing anti-patterns, and completion gates.
---

# Test-Driven Development Quality Rules

## Goal

Embed test-driven development as a cross-cutting quality rule across analysis, design, and implementation without changing the HelloAGENTS three-stage workflow.

## Applicability

```yaml
Required:
  - New feature or observable behavior change
  - Bug fix with reproducible conditions
  - Core business logic change
  - Public API/public method addition or semantic change
  - Regression test for a historical defect

Recommended:
  - Refactoring protected by existing tests
  - Boundary condition, error handling, or compatibility logic changes
  - The user did not request tests, but an automated verification path exists

Exempt:
  - Documentation, knowledge base, comments, formatting
  - Rename-only or mechanical migration with no behavior change
  - Exploratory spike or one-off diagnosis
  - No test framework exists and introducing one is out of scope
  - User explicitly requests read-only analysis or non-production-code-only work

Uncertain:
  - Treat as “Recommended” by default; add test tasks or record an exemption reason in the solution package
```

## Three-Stage Integration

### Analysis
- Mark `TDD Applicability: Required | Recommended | Exempt | Uncertain`.
- Extract observable behaviors, reproduction conditions, boundary scenarios, and verification commands.
- Treat missing testable success criteria as a requirement-completeness deduction or clarification point.

### Design
- Generate `RED → GREEN → REFACTOR → VERIFY` task sequences for each testable behavior.
- Exempt tasks must include `TDD-EXEMPT` and a reason.
- Test tasks must appear before production implementation tasks.

### Implementation
- Before changing production code, complete the matching RED task and confirm the failure reason matches the target behavior.
- GREEN only writes the minimum implementation needed to pass tests; do not refactor or widen scope.
- REFACTOR only runs after related tests pass; rerun tests after refactoring.
- RED/GREEN/REFACTOR evidence may be recorded silently in task notes or final summaries without breaking silent execution modes.

## RED-GREEN-REFACTOR Rules

```yaml
RED:
  - Write the test before production code
  - The test must fail
  - The failure reason must match the target behavior, not syntax, environment, or assertion mistakes

GREEN:
  - Write the minimum production implementation to pass
  - Do not perform unrelated refactoring
  - Do not expand task scope

REFACTOR:
  - Clean up only after tests pass
  - Preserve behavior
  - Rerun related tests after refactoring

VERIFY:
  - Prefer the smallest relevant test set first
  - Run broader existing suites when practical
  - Handle failures per the develop Skill blocking/warning/informational rules
```

## Test Design and Coverage Strategy

### Coverage Layers
- Prefer unit tests for new observable behavior; add integration tests for cross-module collaboration, persistence, network boundaries, or critical flows.
- Use end-to-end tests only for core user journeys and high-risk regressions; do not use E2E tests as a substitute for lower-level tests.
- Bug fixes must start with a failing test that reproduces the defect, then implement the fix.
- For scenarios that cannot be automated, record manual verification steps or a TDD-EXEMPT reason.

### Case Selection
- Cover happy paths, error paths, boundary values, null/missing values, invalid input, permission/state differences, and historical regressions.
- When time, randomness, concurrency, retries, timeouts, or external services are involved, control nondeterminism and verify failure modes.
- Test names should describe business behavior and expected outcomes, not only implementation details.

### Writing Rules
- Use Arrange-Act-Assert by default, keeping each test intent clear.
- Tests should be independent and must not depend on execution order, shared mutable state, or leftover external environment state.
- Test data should be minimal, explicit, and business-meaningful; avoid fixtures that obscure the assertion target.
- Assertions should verify observable results, state changes, outputs, errors, or side effects rather than internal implementation steps.

### Mock Boundaries
- Mock external uncontrollable dependencies when appropriate (network, payment, time, randomness, third-party APIs), but do not mock the code under test.
- Mocks must isolate uncontrollable boundaries, not hide design problems or skip real business collaboration.
- If mock setup becomes more complex than the behavior being tested, prefer fakes, lightweight real components, or integration tests.
## Testing Anti-Patterns

- Do not test mock behavior; test observable business results.
- Do not add `test-only` methods, switches, or internal-state leaks to production classes.
- Understand real dependency shape, side effects, failure modes, and call contracts before mocking.
- Keep mock object shape close to real objects to avoid false positives.
- If mocks become too complex, prefer fakes, lightweight real components, or integration tests.
- Do not add integration tests as an afterthought; plan them during design.
- Avoid verifying only call counts without verifying business outcomes.

## Completion Gate

```yaml
Check:
  - Every new observable behavior has a test, or an explicit TDD-EXEMPT reason
  - RED evidence is recorded: test name/test command, failure summary, target behavior, and failure-reason match
  - GREEN evidence is recorded: test command, pass summary, and minimum implementation note
  - Related tests still passed after REFACTOR
  - VERIFY evidence is recorded: test command, result summary, remaining risks, or uncovered reasons
  - No unnecessary mocks or test-only production interfaces were added
  - Happy paths, error paths, and key boundary cases are covered, or uncovered reasons are recorded
  - Tests remain independent, clearly named, and assert observable results
  - No new blocking test failures remain

Wording correction:
  - Prefer “new observable behavior must have tests” over “every new function/method must have tests”
  - Private helpers may be protected through tests of their external behavior
```


