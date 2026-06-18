---
name: fix-pr-reviews
description: Fix AI Code Review Comments from GitHub PR
disable-model-invocation: true
---

# Fix AI Code Review Comments from GitHub PR

Fetch code review comments from a GitHub Pull Request, analyze each comment, and fix the issues in the local codebase.

## Input

- `$ARGUMENTS` - GitHub PR URL (e.g., `https://github.com/org/repo/pull/123`) or PR number (e.g., `123`). If blank, user will be prompted.

## Steps

### 1. Validate Input

**AI Task:** Determine the PR reference:

1. **If `$ARGUMENTS` is empty or blank:**
   - Ask the user: "Please provide a GitHub PR URL or PR number (e.g., `https://github.com/org/repo/pull/123` or `123`)"
   - Wait for response before proceeding

2. **If provided:**
   - Extract the PR number from the URL or use the number directly
   - Proceed to Step 2

### 2. Fetch PR Review Comments

**AI Task:** Gather all review comments from the PR:

1. **Fetch PR details and diff:**

   ```bash
   gh pr view <PR_NUMBER> --json title,body,state,baseRefName,headRefName,url
   ```

2. **Fetch all review comments (these are inline code review comments):**

   ```bash
   gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments --paginate --jq '.[] | {id: .id, path: .path, line: .line, original_line: .original_line, side: .side, body: .body, diff_hunk: .diff_hunk, user: .user.login, created_at: .created_at, in_reply_to_id: .in_reply_to_id}'
   ```

3. **Fetch PR-level review comments (top-level reviews with body text):**

   ```bash
   gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews --paginate --jq '.[] | select(.body != "") | {id: .id, body: .body, state: .state, user: .user.login}'
   ```

4. **Fetch issue-level comments (general conversation):**

   ```bash
   gh pr view <PR_NUMBER> --json comments --jq '.comments[] | {body: .body, author: .author.login}'
   ```

### 3. Categorize & Prioritize Comments

**AI Task:** Analyze and organize the fetched comments:

1. **Filter out noise:**
   - Skip bot auto-generated comments that are NOT code review feedback (e.g., deployment status, CI results)
   - Skip resolved/outdated comment threads if identifiable
   - Keep ALL comments that contain actionable code review feedback, suggestions, or improvement requests — regardless of whether they come from a human or an AI reviewer

2. **Categorize each comment:**
   - **Must Fix** — Bugs, security issues, logic errors, type errors
   - **Should Fix** — Code quality, readability, naming, patterns, best practices
   - **Consider** — Suggestions, preferences, optional improvements
   - **Won't Fix** — Questions already answered, non-actionable praise, out-of-scope

3. **Present the categorized list to the user:**

   ```
   ## PR Review Comments — [PR Title]

   **PR:** [URL]
   **Total Comments:** X actionable (Y filtered out)

   ### Must Fix (X)
   | # | File | Line | Comment | Author |
   |---|------|------|---------|--------|
   | 1 | `path/to/file.ts` | L42 | [Summary of issue] | @reviewer |

   ### Should Fix (X)
   | # | File | Line | Comment | Author |
   |---|------|------|---------|--------|
   | 2 | `path/to/file.ts` | L15 | [Summary of issue] | @reviewer |

   ### Consider (X)
   | # | File | Line | Comment | Author |
   |---|------|------|---------|--------|
   | 3 | `path/to/file.ts` | L88 | [Summary of suggestion] | @reviewer |

   ### Won't Fix (X)
   | # | Reason | Comment |
   |---|--------|---------|
   | 4 | [Why skipped] | [Comment summary] |
   ```

4. **Ask the user which categories to fix:**
   - Default: Fix all "Must Fix" and "Should Fix" items
   - Let user confirm or adjust (e.g., "Fix all", "Skip #3", "Also fix #5 from Consider")

### 4. Read Affected Files

**AI Task:** Before making any changes:

1. **Identify all unique files** mentioned in the comments to fix
2. **Read each file completely** to understand current state
3. **Cross-reference** comment line numbers with current file contents
   - Comments may reference old line numbers if commits have been pushed since the review
   - Use the `diff_hunk` context from each comment to locate the correct code section
4. **Check for conflicting comments** — two reviewers suggesting different fixes for the same code

### 5. Fix Each Comment

**AI Task:** Address each approved comment, working file-by-file:

**For each file with comments:**

#### a. Plan the changes

- Group all comments for the same file
- Determine if fixes interact with each other (overlapping line ranges)
- Order fixes from bottom-to-top of file to preserve line numbers during edits

#### b. Apply fixes

- Make the code change that addresses the reviewer's feedback
- Follow project conventions:
  - All business logic and AI orchestration live in `apps/api` — keep `apps/web` a thin client
  - Validate inputs and pipeline handoffs with Pydantic models (no raw dicts crossing a stage boundary)
  - Keep compliance logic RAG-grounded
  - Keep file uploads going browser → S3 via presigned URL (don't proxy through the API)
- If a comment suggests a specific code change, use that suggestion
- If a comment identifies a problem but doesn't suggest a fix, use your best judgment to implement an appropriate solution

#### c. Verify each fix

- Ensure the fix actually addresses the reviewer's concern
- Ensure no surrounding code is broken by the change
- If a fix requires changes in other files (e.g., updating imports, shared types), make those too

### 6. Run Validation

**AI Task:** Ensure all fixes are clean:

```bash
# Frontend (apps/web)
pnpm --filter web run typecheck
pnpm --filter web run lint

# Backend (apps/api)
ruff check
pytest
```

(Run only the side(s) the PR actually touches.)

**If validation fails:**

- Fix the issues
- Re-run validation
- Don't proceed until all checks pass

### 7. Generate Fix Report

**AI Task:** Produce a summary of all changes made:

```
## PR Review Fixes Complete

**PR:** [URL]
**Branch:** [current branch]

### Comments Addressed

| # | File | Comment Summary | Fix Applied | Status |
|---|------|-----------------|-------------|--------|
| 1 | `path/to/file:42` | [Issue] | [What was changed] | Fixed |
| 2 | `path/to/file:15` | [Issue] | [What was changed] | Fixed |
| 3 | `path/to/file:88` | [Suggestion] | Skipped (user choice) | Skipped |

### Files Modified

| File | Changes |
|------|---------|
| `path/to/file` | [Summary of all changes in file] |

### Validation Results

- Frontend (typecheck / lint): PASS/FAIL/N-A
- Backend (ruff / pytest): PASS/FAIL/N-A

### Next Steps

1. Review the changes in your editor
2. Run `/ship` or commit and push to update the PR
3. Re-request review from the original reviewers
```

Done.
