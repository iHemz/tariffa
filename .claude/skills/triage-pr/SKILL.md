---
name: triage-pr
description: Analyze GitHub PR review comments — categorize what needs fixing vs what to leave. Provide a PR URL or number as argument.
argument-hint: "GitHub PR URL or PR number (required)"
---

# Triage PR Review Comments

Fetch all review comments from a GitHub Pull Request, analyze each one against the codebase and project conventions, and produce a categorized report of what needs fixing and what can safely be left.

**This skill is analysis-only — it does NOT modify any files.**

## Input

- `$ARGUMENTS` — GitHub PR URL (e.g., `https://github.com/org/repo/pull/123`) or PR number (e.g., `123`). **Required.**

## Steps

### 1. Validate Input

**AI Task:** Determine the PR reference:

1. **If `$ARGUMENTS` is empty or blank:**
   - Ask the user: "Please provide a GitHub PR URL or PR number (e.g., `https://github.com/org/repo/pull/123` or `123`)"
   - Wait for response before proceeding

2. **If provided:**
   - Extract the PR number from the URL or use the number directly
   - Proceed to Step 2

### 2. Fetch PR Context

**AI Task:** Gather the full picture — PR metadata, diff, and all comments:

1. **Fetch PR details:**

   ```bash
   gh pr view <PR_NUMBER> --json title,body,state,baseRefName,headRefName,url,author,additions,deletions,changedFiles
   ```

2. **Fetch the diff to understand what changed:**

   ```bash
   gh pr diff <PR_NUMBER>
   ```

3. **Fetch inline code review comments:**

   ```bash
   gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments --paginate --jq '.[] | {id: .id, path: .path, line: .line, original_line: .original_line, body: .body, diff_hunk: .diff_hunk, user: .user.login, created_at: .created_at, in_reply_to_id: .in_reply_to_id}'
   ```

4. **Fetch PR-level review comments (top-level reviews with body text):**

   ```bash
   gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews --paginate --jq '.[] | select(.body != "") | {id: .id, body: .body, state: .state, user: .user.login}'
   ```

5. **Fetch issue-level comments (general conversation):**

   ```bash
   gh pr view <PR_NUMBER> --json comments --jq '.comments[] | {body: .body, author: .author.login}'
   ```

### 3. Read Affected Files

**AI Task:** For every file referenced in review comments:

1. Read the **current local version** of each file mentioned in comments
2. This allows you to determine:
   - Whether the comment is still relevant (code may have changed since the review)
   - Whether the surrounding code context affects the fix approach
   - Whether the comment applies to the project's actual conventions

### 4. Analyze & Categorize Each Comment

**AI Task:** Evaluate every comment against three dimensions:

#### a. Validity Check

For each comment, determine:
- **Is the reviewer correct?** — Does the feedback accurately identify a real issue?
- **Is it still relevant?** — Has the code changed since the comment was made?
- **Does it align with project conventions?** — Check against `CLAUDE.md`, `/docs/`, and existing patterns in the codebase

#### b. Categorize

Assign each comment to exactly one category:

| Category | Criteria | Action |
|----------|----------|--------|
| **Must Fix** | Bugs, security issues, logic errors, type safety violations, data integrity risks | Fix before merging |
| **Should Fix** | Valid code quality feedback, naming issues, missing error handling, pattern violations from `/docs/` | Fix — improves code quality |
| **Nitpick — Take It** | Minor but valid improvements: slightly better naming, small readability wins, trivial refactors | Quick wins worth doing |
| **Leave** | Subjective preference, stylistic opinion not backed by project conventions, over-engineering suggestion, or already-correct code the reviewer misread | Skip with justification |
| **Outdated** | Comment references code that has already been changed or removed since the review | Skip — no longer applies |

#### c. Provide Reasoning

For every comment — especially "Leave" and "Outdated" — write a clear 1-2 sentence justification. This is the most valuable part of the triage.

### 5. Generate Triage Report

**AI Task:** Produce a structured report:

```
## PR Review Triage — [PR Title]

**PR:** [URL]
**Author:** @[author] | **Reviewer(s):** @[reviewers]
**State:** [Open/Merged] | **Files Changed:** [count] (+[additions]/-[deletions])

---

### Must Fix ([count])

| # | File:Line | Reviewer | Issue | Why It Matters |
|---|-----------|----------|-------|----------------|
| 1 | `path/file.ts:42` | @reviewer | [Summary] | [Impact if not fixed] |

<For each item, include the full comment text and your recommended fix approach (2-3 sentences max)>

---

### Should Fix ([count])

| # | File:Line | Reviewer | Issue | Rationale |
|---|-----------|----------|-------|-----------|
| 2 | `path/file.ts:15` | @reviewer | [Summary] | [Why this improves quality] |

<For each item, include the comment and fix approach>

---

### Nitpick — Take It ([count])

| # | File:Line | Reviewer | Suggestion |
|---|-----------|----------|------------|
| 3 | `path/file.ts:88` | @reviewer | [Summary] |

---

### Leave ([count])

| # | File:Line | Reviewer | Comment | Why We're Leaving It |
|---|-----------|----------|---------|---------------------|
| 4 | `path/file.ts:22` | @reviewer | [Summary] | [Clear justification] |

---

### Outdated ([count])

| # | File:Line | Reviewer | Comment | Why It's Outdated |
|---|-----------|----------|---------|-------------------|
| 5 | `path/file.ts:50` | @reviewer | [Summary] | [What changed since] |

---

### Summary

- **Total comments:** [X]
- **Fix:** [Must Fix + Should Fix + Nitpick count] items
- **Leave:** [Leave + Outdated count] items
- **Estimated effort:** [Quick / Medium / Significant]

### Recommended Next Steps

1. [Prioritized action items]
2. Run `/fix-pr-reviews [PR_NUMBER]` to auto-fix the "Must Fix" and "Should Fix" items
```

### 6. Ask User How to Proceed

**AI Task:** After presenting the report, ask the user:

> Would you like me to run `/fix-pr-reviews` to fix the "Must Fix" and "Should Fix" items? Or would you like to adjust the categories first?

Done.
