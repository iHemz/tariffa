---
name: implement-prd
description: Implement PRD

---

# Implement PRD

Implement a feature based on an existing Product Requirements Document (PRD), then ship the changes.

## Input

- `{{prd_name}}` - The PRD filename or partial name (e.g., `form-m-export`, `hs-classification`). Leave blank to be prompted.

## Prerequisites

- Working in a local Git repository
- PRD document exists in `docs/prds/`
- On `main` branch with clean working directory (or feature branch for incremental work)

## Steps

### 1. Locate PRD Document

**AI Task:** Find the PRD file:

1. **If `{{prd_name}}` is empty or blank:**
   - List PRD files in `docs/prds/`
   - Ask: "Which PRD would you like to implement?"
   - Wait for response before proceeding

2. **Search for PRD:**
   - Look in `docs/prds/` for files matching `{{prd_name}}`
   - Try: exact match, partial match
   - Common patterns: `[feature-name].md`, `batch-[date]-[feature-name].md`

3. **If no PRD found:**
   - Inform user: "No PRD found matching '{{prd_name}}' in `docs/prds/`"
   - List available PRDs
   - STOP - do not proceed without a valid PRD

4. **If multiple matches:**
   - List matching files
   - Ask user to specify which one

5. **Read the ENTIRE PRD document** thoroughly before proceeding

### 2. Analyze PRD Structure

**AI Task:** Extract implementation details:

1. **Parse Core Sections:**
   - Executive Summary (understand the "why")
   - Problem Statement (current vs desired state)
   - Scope (In Scope vs Out of Scope)
   - Functional Requirements (P0/P1/P2 priorities)
   - Technical Approach (modules, patterns, constraints)
   - Implementation Phases (ordered tasks)
   - Acceptance Criteria (definition of done)

2. **Identify Key Implementation Details:**
   - Affected modules/files
   - Database schema changes (Postgres)
   - API endpoints (new/modified)
   - UI components (new/modified)
   - Pipeline stage contracts (Pydantic models) affected
   - Migration needs

3. **Confirm understanding with user:**

   ```
   I'll implement: [PRD Title]

   **Summary:** [1-2 sentences]

   **P0 Requirements (Must Have):**
   - [Requirement 1]
   - [Requirement 2]

   **Phases:**
   1. [Phase 1 summary]
   2. [Phase 2 summary]
   3. [Phase 3 summary]

   **Estimated Changes:** [X] files across [Y] modules

   Ready to proceed? (or specify a phase to start with)
   ```

4. **Wait for user confirmation** before making any changes

### 3. Pre-Implementation Checks

**AI Task:** Verify readiness:

1. **Check git state:**

   ```bash
   git status
   ```

   - Ensure working directory is clean (or warn about uncommitted changes)
   - Note current branch

2. **Review project conventions:**
   - Skim the relevant `/docs/` spec for the area being changed
   - Note the non-negotiables: thin frontend, typed Pydantic handoffs, RAG-grounded compliance, browser → S3 uploads, never submits to NICIS/Trade Window

3. **Verify referenced files exist:**
   - Check each file mentioned in PRD's Technical Approach
   - Read existing code that will be modified
   - Note any drift from PRD assumptions

4. **Check for conflicts:**
   - Has the codebase changed since PRD was written?
   - Are there new patterns to consider?
   - Flag any discrepancies to user

### 4. Implementation Phase Loop

**AI Task:** Execute each implementation phase from the PRD:

**For each phase (Phase 1, Phase 2, Phase 3...):**

#### 4a. Announce Phase Start

```
## Starting Phase [N]: [Phase Name]

**Goal:** [Phase goal from PRD]

**Deliverables:**
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
```

#### 4b. Implement Deliverables

**For each deliverable in the phase:**

1. **Read target files** before editing
2. **Make changes following project conventions:**
   - All business logic and AI orchestration live in `apps/api`; keep `apps/web` a thin client
   - Validate inputs and every pipeline handoff with Pydantic models (no raw dicts across a stage boundary)
   - Keep compliance logic RAG-grounded
   - Keep file uploads going browser → S3 via presigned URL
   - Never claim to submit to NICIS / Trade Window — output is a draft

3. **Handle dependencies:**
   - Schema/migration changes before service changes
   - Service/agent changes before API changes
   - API changes before UI changes

4. **Document non-obvious decisions** with inline comments

#### 4c. Phase Checkpoint

After completing each phase:

```bash
# Backend (apps/api)
ruff check
pytest

# Frontend (apps/web)
pnpm --filter web run typecheck
pnpm --filter web run lint
```

(Run only the side(s) the phase touched.)

**If errors occur:**

- Fix issues immediately
- Re-run validation
- Don't proceed to next phase until current phase passes

#### 4d. Phase Completion

```
## Phase [N] Complete ✅

**Deliverables Completed:**
- ✅ [Deliverable 1]
- ✅ [Deliverable 2]

**Files Modified:**
- `path/to/file1.ts`
- `path/to/file2.ts`

**Validation:** ruff/pytest ✅ | typecheck/lint ✅

Proceeding to Phase [N+1]...
```

### 5. Final Validation

**AI Task:** Comprehensive quality check:

1. **Run all validation commands:**

   ```bash
   # Backend
   ruff check && pytest
   # Frontend
   pnpm --filter web run typecheck && pnpm --filter web run lint
   ```

2. **Verify acceptance criteria from PRD:**
   - Check each functional criterion
   - Check each quality criterion
   - Check each UX criterion (if applicable)

3. **Create validation summary:**

   ```
   ## Acceptance Criteria Verification

   **Functional:**
   - ✅ [Criterion 1]
   - ✅ [Criterion 2]

   **Quality:**
   - ✅ Backend: ruff + pytest pass
   - ✅ Frontend: typecheck + lint pass
   - ✅ Pipeline handoffs are validated Pydantic models

   **UX:**
   - ✅ [UX criterion if applicable]
   ```

### 6. Update PRD with Implementation Status

**AI Task:** Mark PRD as implemented:

Add an "Implementation Status" section at the end of the PRD file:

```markdown
---

## Implementation Status

**Status:** ✅ Implemented
**Date:** [today's date]
**Implementer:** AI Agent

### Changes Made

| Phase   | Files Modified | Summary         |
| ------- | -------------- | --------------- |
| Phase 1 | [count] files  | [brief summary] |
| Phase 2 | [count] files  | [brief summary] |
| Phase 3 | [count] files  | [brief summary] |

### Validation Results

- ✅ Backend: ruff + pytest passed
- ✅ Frontend: typecheck + lint passed
- ✅ All acceptance criteria met

### Notes

[Any implementation decisions, deviations from PRD, or follow-up items]
```

### 7. Implementation Summary

**AI Task:** Provide comprehensive summary before shipping:

```
## PRD Implementation Complete ✅

**PRD:** [PRD filename]
**Feature:** [Feature Name]

### Summary of Changes

| Area | Files | Changes |
|--------|-------|---------|
| `apps/api/[module]` | [count] | [summary] |
| `apps/api/[route]` | [count] | [summary] |
| `apps/web/[component]` | [count] | [summary] |

**Total:** [X] files modified, [Y] lines added, [Z] lines removed

### Phases Completed

1. ✅ Phase 1: [summary]
2. ✅ Phase 2: [summary]
3. ✅ Phase 3: [summary]

### Validation Results

- ✅ Backend: `ruff check` + `pytest` - passed
- ✅ Frontend: typecheck + lint - passed

### Acceptance Criteria

- ✅ [P0 requirement 1]
- ✅ [P0 requirement 2]
- ✅ [All criteria met]

### Ready to Ship

Proceeding to create branch, commit, and open PR...
```

### 8. Ship Changes

**AI Task:** Execute the /ship workflow:

**This step executes the full `/ship` command workflow:**

1. **Analyze changes:**

   ```bash
   git status && git diff --stat && git diff --name-only
   ```

2. **Determine branch name:**
   - Extract from PRD: `feat/[prd-feature-name]`
   - Or derive from the feature: `feat/[brief-description]`

3. **Create feature branch:**

   ```bash
   git checkout -b [branch-name]
   ```

4. **Stage all changes:**

   ```bash
   git add -A
   ```

5. **Craft commit message:**
   - Type: `feat` (new feature) or `fix` (bug fix) based on PRD type
   - Scope: Primary module affected
   - Subject: Brief description from PRD title
   - Body: Summary of key changes with PRD reference

   ```
   feat([module]): implement [PRD title]

   - [Key change 1]
   - [Key change 2]
   - [Key change 3]

   PRD: docs/prds/[prd-filename].md
   ```

6. **Commit changes:**

   ```bash
   git commit -m "$(cat <<'COMMIT'
   feat([module]): implement [PRD title]

   - [Key change 1]
   - [Key change 2]
   - [Key change 3]

   PRD: docs/prds/[prd-filename].md
   COMMIT
   )"
   ```

7. **Push to remote:**

   ```bash
   git push -u origin HEAD
   ```

8. **Create Pull Request:**
   - Use `gh pr create` (see ship skill for full workflow)
   - Title: `feat([module]): [PRD title]`
   - Body:

     ```markdown
     ## Summary

     Implements [PRD title] as specified in `docs/prds/[filename].md`.

     - [Key deliverable 1]
     - [Key deliverable 2]
     - [Key deliverable 3]

     ## Changes

     | Area                  | Changes   |
     | --------------------- | --------- |
     | `apps/api/[module]`   | [summary] |
     | `apps/web/[component]`| [summary] |

     ## PRD Reference

     - **PRD:** `docs/prds/[filename].md`
     - **Issue:** [GitHub issue # if present]

     ## Test Plan

     - [ ] Backend: ruff + pytest pass
     - [ ] Frontend: typecheck + lint pass
     - [ ] [Manual test 1 from PRD acceptance criteria]
     - [ ] [Manual test 2 from PRD acceptance criteria]

     ## Acceptance Criteria

     From PRD:

     - [x] [P0 criterion 1]
     - [x] [P0 criterion 2]
     ```

### 9. Final Report

**AI Task:** Provide final summary:

```
## Implementation & Ship Complete ✅

**PRD:** `docs/prds/[filename].md`
**Feature:** [Feature Name]

### Git

- **Branch:** `[branch-name]`
- **Commit:** `[short-hash]` - [commit subject]

### Pull Request

- **URL:** [PR URL]
- **Title:** [PR title]

### Summary

| Metric | Value |
|--------|-------|
| Files Modified | [count] |
| Lines Added | [count] |
| Lines Removed | [count] |
| Phases Completed | [count] |

### Validation

- ✅ Backend: ruff + pytest passed
- ✅ Frontend: typecheck + lint passed
- ✅ Acceptance Criteria: all met

### Next Steps

1. [ ] Wait for CI checks to pass
2. [ ] Review changes in the PR
3. [ ] Request review if needed
4. [ ] Merge when approved
5. [ ] Close the linked GitHub issue (if applicable)
```

---

## Error Handling

**PRD Not Found:**

- List available PRDs in `docs/prds/`
- Suggest running `/prd` to create one first

**Validation Failures:**

- Fix issues before proceeding
- Re-run validation
- Document any fixes as implementation notes

**Git Conflicts:**

- Notify user of conflict
- Suggest resolution approach
- Wait for user to resolve before continuing

**PR Creation Fails:**

- Ensure GitHub CLI (`gh`) is installed and authenticated
- Check authentication: `gh auth status`
- Provide manual commands as fallback

## Conventions

**Branch Naming:**

- `feat/[prd-slug]` for new features
- `fix/[prd-slug]` for bug fixes
- `refactor/[prd-slug]` for refactoring PRDs

**Commit Message:**

- Follow conventional commits
- Reference PRD in commit body
- Include the GitHub issue number if present

Done.
