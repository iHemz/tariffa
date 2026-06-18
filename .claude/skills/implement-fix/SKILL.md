---
name: implement-fix
description: Implement Fix from RCA Document

---

# Implement Fix from RCA Document

Implement a fix based on an existing Root Cause Analysis (RCA) document.

## Input

- `{{issue_ref}}` - A reference for the issue: a GitHub issue number (e.g., `42`) or a short slug (e.g., `shipment-sync-race`). Leave blank to be prompted.

## Prerequisites

- Working in a local Git repository
- An RCA document exists at `docs/rca/{{issue_ref}}.md`

## Steps

### 1. Validate the Issue Reference

**AI Task:** Check if a reference was provided:

1. **If `{{issue_ref}}` is empty or blank:**
   - Ask the user: "Please provide the issue reference (a GitHub issue number like `42`, or a slug like `shipment-sync-race`)"
   - Wait for their response before proceeding
   - Do NOT continue until a valid reference is provided

2. **If a reference is provided:**
   - Proceed to Step 2

### 2. Verify RCA Document Exists

**AI Task:** Check for the RCA document:

1. Look for the RCA document at `docs/rca/{{issue_ref}}.md`
2. **If the RCA document does NOT exist:**
   - Inform the user: "No RCA document found at `docs/rca/{{issue_ref}}.md`. Please create an RCA first (e.g. via `/find-bug`)."
   - STOP — do not proceed without an RCA document

3. **If the RCA document exists:**
   - Read the ENTIRE RCA document thoroughly
   - Proceed to Step 3

### 3. Fetch Additional Context

**AI Task:** Gather any extra context for the fix:

1. If `{{issue_ref}}` is a GitHub issue number, fetch it:
   ```bash
   gh issue view {{issue_ref}}
   ```
   Extract: title, description, labels, and any comments with reproduction details.
2. If it's a local slug, rely on the RCA document and ask the user for anything missing.

### 4. Analyze the RCA Document

**AI Task:** Extract implementation details from the RCA:

1. **Understand the Root Cause:** what exactly is broken and why; which module/layer is affected.
2. **Review the Proposed Fix:** what changes are recommended; which files; what strategy.
3. **Note Testing Requirements:** what tests should be added/modified; what validation is needed.
4. **Check Affected Files:** list all files mentioned; verify they still exist and haven't been significantly modified.

### 5. Verify Current State

**AI Task:** Before making changes:

1. **Confirm the issue still exists:** review the code mentioned in the RCA, verify the problem is still present.
2. **Check current state of affected files:** read each file that will be modified; look for recent changes that affect the fix.
3. **Identify any conflicts:** has the code changed since the RCA was written? Are there new patterns or dependencies to consider?

### 6. Implement the Fix

**AI Task:** Following the "Proposed Fix" section of the RCA:

**For each file to modify:**

#### a. Read the existing file

- Understand current implementation
- Locate the specific code mentioned in the RCA

#### b. Make the fix

- Implement the change as described in the RCA
- Follow project conventions:
  - All business logic and AI orchestration live in `apps/api` — keep `apps/web` a thin client
  - Validate inputs and pipeline handoffs with Pydantic models (no raw dicts crossing a stage boundary)
  - Keep compliance logic RAG-grounded
  - Keep file uploads going browser → S3 via presigned URL
- Maintain code style and conventions
- Add comments if the fix is non-obvious

#### c. Handle related changes

- Update any related code affected by the fix
- Ensure consistency across the codebase
- Update imports if needed
- Respect the client/server boundary

### 7. Add/Update Tests

**AI Task:** Following the "Testing Requirements" from the RCA:

**Create test cases for:**

1. Verify the fix resolves the issue
2. Test edge cases related to the bug
3. Ensure no regression in related functionality
4. Test any new code paths introduced

**Test location:**

- Backend: `pytest` tests under `apps/api` (mirror the source location)
- Frontend: component/unit tests under `apps/web` if applicable
- Use descriptive test names

**Backend test example:**

```python
class TestIssue_{{issue_ref}}Fix:
    def test_resolves_reported_issue(self):
        # Arrange - set up the scenario that caused the bug
        # Act - execute the code that previously failed
        # Assert - verify it now works correctly
        ...

    def test_handles_edge_cases(self):
        # Test edge case scenarios
        ...
```

### 8. Run Validation

**AI Task:** Execute validation commands (only for the side(s) you touched):

```bash
# Backend (apps/api)
ruff check
pytest

# Frontend (apps/web)
pnpm --filter web run typecheck
pnpm --filter web run lint
```

**If validation fails:**

- Fix the issues
- Re-run validation
- Don't proceed until all pass

### 9. Verify the Fix

**AI Task:** Verify the fix works:

1. **Follow reproduction steps from the RCA:** execute the steps that previously caused the issue; confirm it no longer occurs.
2. **Test edge cases:** boundary conditions, error scenarios.
3. **Check for unintended side effects:** verify related functionality still works; ensure no new errors.

### 10. Update the RCA Document

**AI Task:** Add an "Implementation" section at the end of the RCA:

```markdown
## Implementation

**Date:** [today's date]
**Implementer:** AI Agent

### Changes Made

| File              | Change                  | Lines        |
| ----------------- | ----------------------- | ------------ |
| `path/to/file.py` | [Description of change] | [line range] |

### Tests Added

- `apps/api/tests/test_file.py` - [Description of tests]

### Validation

- ruff check passed
- pytest passed
- (frontend) typecheck / lint passed (if applicable)

### Verification

- Issue no longer reproducible
- Edge cases handled
- No regressions detected
```

### 11. Update the Issue (if applicable)

**AI Task:** If `{{issue_ref}}` is a GitHub issue, add an implementation summary comment:

```bash
gh issue comment {{issue_ref}} --body "..."
```

**Comment format:**

```markdown
## Fix Implemented

**Root Cause:** [One-line summary from RCA]

**Changes Made:**

- `path/to/file.py` - [change description]
- `path/to/other.py` - [change description]

**Tests Added:**

- [Test file and description]

**Validation:**

- ruff check / pytest pass
- (frontend) typecheck / lint pass (if applicable)
- Issue verified resolved

**Ready for review and merge.**
```

## Output Summary

Return a final summary:

```
## Fix Implementation Complete

**Issue:** {{issue_ref}} - [Title]
**RCA Document:** `docs/rca/{{issue_ref}}.md`

**Root Cause:**
[One-line summary from RCA]

### Changes Made

| File | Change |
|------|--------|
| `path/to/file.py` | [Description] |
| `path/to/file.py` | [Description] |

**Total:** X files modified, Y lines added, Z lines removed

### Tests Added

| Test File | Tests |
|-----------|-------|
| `apps/api/tests/test_x.py` | [Test names] |

### Validation Results

- ruff check - passed
- pytest - passed
- (frontend) typecheck / lint - passed (if applicable)

### Verification

- Issue no longer reproducible
- Edge cases handled
- No regressions detected

### Ready for Commit

**Suggested commit message:**

fix([module]): resolve {{issue_ref}} - [brief description]

[Summary of what was fixed and how]

**Next Steps:**
1. Review changes in the modified files
2. Run `/commit` to commit the changes
3. Create a PR for review
```

Done.
