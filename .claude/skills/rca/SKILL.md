---
name: rca
description: Root Cause Analysis (RCA) from a GitHub issue or local TODO entry
---

# Root Cause Analysis (RCA)

Generate a Root Cause Analysis document for a bug/issue, sourced from a GitHub issue or a local `TODO.md` entry.

## Input

- `{{issue_ref}}` - A GitHub issue number (e.g. `#42`), a GitHub issue URL, or a short description / `TODO.md` line item. Leave blank to be prompted.

## Prerequisites

- Working in a local Git repository
- The bug/issue is described somewhere I can read it (a GitHub issue, a `TODO.md` line, or a pasted description)
- `gh` CLI available if pulling from a GitHub issue

## Steps

### 1. Validate the Issue Reference

**AI Task:** Check if an issue reference was provided:

1. **If `{{issue_ref}}` is empty or blank:**
   - Ask: "Which bug should I analyze? Give me a GitHub issue number (e.g. `#42`), an issue URL, a line from `TODO.md`, or just describe it."
   - Wait for the response before proceeding
   - Do NOT continue until something is provided

2. **If a reference is provided:**
   - Proceed to Step 2

### 2. Fetch the Issue Details

**AI Task:** Retrieve the full context for the bug:

1. **If it's a GitHub issue** (number or URL):
   - Run `gh issue view <number> --comments` to pull the title, body, labels, and comments
2. **If it's a `TODO.md` entry:**
   - Read `TODO.md` and locate the matching line / section
3. **If it's a pasted description:**
   - Use it directly

4. Extract all relevant fields:
   - Title / summary
   - Description
   - Labels / priority (if any)
   - Comments (for reproduction steps, additional context)

5. **Verify this is a bug/issue** (not a feature request). If unclear, ask me to confirm.

### 3. Analyze the Issue

**AI Task:** Understand the problem:

1. **Extract from the issue:**
   - What is the expected behavior?
   - What is the actual (broken) behavior?
   - Steps to reproduce (if provided)
   - Error messages or logs (if provided)
   - Affected users/roles
   - Severity/Impact

2. **Identify affected area:**
   - Which app — `apps/web` (Next.js frontend) or `apps/api` (FastAPI backend)?
   - Which module/agent/component is affected?
   - What user flows are impacted (upload, extraction, classification, compliance check, Form M prep sheet)?

### 4. Search Codebase for Root Cause

**AI Task:** Investigate the codebase:

1. **Search for related code:**
   - Use `Grep`/`Glob` to find the affected functionality
   - Search for any error messages mentioned in the issue
   - Find the specific component/agent/endpoint/service

2. **Trace the code path:**
   - Identify the entry point (FastAPI endpoint, React component, agent stage, background task)
   - Follow the execution flow, including any typed Pydantic handoff between pipeline stages
   - Find where the issue occurs

3. **Identify the root cause:**
   - What is the actual bug/defect?
   - Why does it behave incorrectly?
   - What conditions trigger the bug?

4. **Check for related issues:**
   - Are there similar patterns elsewhere with the same bug?
   - Is this a regression from a recent change?

### 5. Determine Fix Strategy

**AI Task:** Plan the fix:

1. **Identify the fix approach:**
   - What needs to change to fix the issue?
   - Are there multiple ways to fix it? What is the safest/cleanest approach?

2. **Identify files to modify:**
   - List all files that need changes
   - Note the specific functions/components/models to update

3. **Consider edge cases:**
   - What edge cases does the fix need to handle?
   - Are there related scenarios that might be affected?

4. **Assess risk:**
   - What could go wrong with the fix?
   - What are the testing requirements?

### 6. Generate RCA Document

**AI Task:** Create a comprehensive RCA document:

```markdown
# RCA: {{issue_ref}} - [Issue Title]

**Issue:** {{issue_ref}}
**Date:** [today's date]
**Severity:** [Critical/High/Medium/Low]
**Status:** Analysis Complete - Ready for Implementation

---

## Summary

[2-3 sentence summary of the issue and its impact]

## Issue Details

### Expected Behavior

[What should happen]

### Actual Behavior

[What actually happens - the bug]

### Reproduction Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Error Messages/Logs
```

[Any relevant error messages or logs]

````

### Affected Users

- [User type/role affected]
- [Scope of impact]

## Root Cause Analysis

### Investigation Summary

[Description of how the root cause was identified]

### Root Cause

**Location:** `path/to/file.py` (lines X-Y)

**The Problem:**
[Clear explanation of what is wrong in the code]

**Why It Happens:**
[Explanation of the conditions that trigger the bug]

### Code Analysis

```python
# Current code (problematic)
[Show the problematic code snippet]
````

**Issue:** [Explain what's wrong with this code]

## Proposed Fix

### Fix Strategy

[High-level description of how to fix the issue]

### Files to Modify

| File                | Change Required         |
| ------------------- | ----------------------- |
| `path/to/file.py`   | [Description of change] |
| `path/to/other.tsx` | [Description of change] |

### Proposed Code Changes

**File:** `path/to/file.py`

```python
# Before (current code)
[problematic code]

# After (fixed code)
[corrected code]
```

### Edge Cases to Handle

- [ ] [Edge case 1]
- [ ] [Edge case 2]

## Testing Requirements

### Unit Tests

- [ ] Test that [specific scenario] works correctly
- [ ] Test edge case: [description]
- [ ] Test error handling: [description]

### Integration Tests

- [ ] Verify [end-to-end flow] works
- [ ] Test [related functionality] not regressed

### Manual Verification

1. [Step to manually verify the fix]
2. [Step to verify edge cases]

## Validation Commands

```bash
# Backend (apps/api)
ruff check apps/api
pytest apps/api

# Frontend (apps/web)
pnpm --filter web run typecheck
pnpm --filter web run lint
```

## Risk Assessment

| Risk               | Likelihood   | Impact       | Mitigation        |
| ------------------ | ------------ | ------------ | ----------------- |
| [Potential risk 1] | Low/Med/High | Low/Med/High | [How to mitigate] |

## Timeline

- **RCA Created:** [today's date]
- **Ready for Implementation:** Yes

## References

- Issue: {{issue_ref}}
- Related issues: [if any]
- Related docs: [if any, e.g. `/docs/03-agent-pipeline.md`]

---

**Next Step:** Implement this fix, then re-run the validation commands above.

````

### 7. Create RCA File

**AI Task:** Save the RCA document:

1. Ensure the `docs/rca/` directory exists (create if needed)
2. Create the file at `docs/rca/<slug>.md` — use the GitHub issue number if there is one (e.g. `docs/rca/42.md`), otherwise a short kebab-case slug of the title

### 8. Record the RCA Against the Issue

**AI Task:** Link the RCA back to where the bug is tracked:

1. **If it's a GitHub issue:** add a comment with `gh issue comment <number> --body "..."` summarizing the root cause and linking to the RCA file.
2. **If it's a `TODO.md` entry:** update that line to reference the RCA file (e.g. append `→ docs/rca/<slug>.md`).

**Comment / note format:**

```markdown
## Root Cause Analysis Complete

**Root Cause:** [One-line summary]

**Location:** `path/to/affected/file.py`

**Proposed Fix:** [Brief description of fix strategy]

**RCA Document:** `docs/rca/<slug>.md`

**Files to Modify:**
- `path/to/file.py`
- `path/to/other.tsx`
````

## Output Summary

Return a final summary:

```
## RCA Complete

**Issue:** {{issue_ref}} - [Title]
**RCA Document:** `docs/rca/<slug>.md`

### Root Cause Summary

**The Problem:** [One-line description]
**Location:** `path/to/file.py`
**Severity:** [Critical/High/Medium/Low]

### Proposed Fix

[Brief description of fix strategy]

**Files to Modify:**
- `path/to/file.py` - [change description]
- `path/to/other.tsx` - [change description]

### Testing Required

- [X] unit tests
- [X] integration tests (if applicable)

### Tracking Updated

- RCA recorded against the issue / TODO entry

### Next Steps

1. Review the RCA document at `docs/rca/<slug>.md`
2. Implement the fix and run the validation commands
```

Done.
