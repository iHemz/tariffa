---
name: commit
description: Generate a commit message from staged/unstaged changes and commit to the current branch. Use when the user says "commit", "commit changes", "save my work", or wants to commit without switching branches or creating a PR.
argument-hint: "optional commit message hint"
---

# Commit: Generate Message & Commit

Analyze current changes, craft a quality conventional commit message, and commit to the current branch. No branch creation, no push, no PR.

## Input

- `$ARGUMENTS` - Optional hint for the commit message (e.g., `fix login redirect`). If blank, AI will generate entirely from the diff.

## Steps

### 1. Analyze Current State

**AI Task:** Understand what's being committed:

```bash
git status
git diff --stat
git log --oneline -5
```

1. **Check for changes:**
   - If there are no staged or unstaged changes, notify user and stop
   - Note which files are modified, added, or deleted
   - Note which files are already staged vs unstaged

2. **Check for sensitive files:**
   - Warn if `.env`, credentials, secrets, or large binaries are in the changeset
   - Do NOT stage those files unless the user explicitly confirms

### 2. Stage Changes

**AI Task:** Stage the appropriate files:

1. **If files are already staged** and there are no unstaged changes:
   - Use the existing staging as-is

2. **If there are unstaged changes:**
   - Stage all modified and new files that are related to the work:
     ```bash
     git add -A
     ```
   - Review what was staged:
     ```bash
     git diff --cached --stat
     ```

3. **Verify staging:**
   - Confirm files look correct
   - If sensitive files were staged, unstage them and warn

### 3. Analyze the Diff

**AI Task:** Read the full diff to understand the changes:

```bash
git diff --cached
```

- Understand WHAT changed (files, functions, logic)
- Understand WHY it changed (feature, fix, refactor, etc.)
- Identify the scope (which module/area is affected)

### 4. Craft Commit Message

**AI Task:** Generate a conventional commit message:

1. **If `$ARGUMENTS` provided:**
   - Use it as a hint/guide for the message, but still analyze the diff for accuracy

2. **Follow conventions:**
   - **Format:** `type(scope): subject`
   - **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
   - **Scope:** Module or area affected (e.g., `extraction`, `compliance`, `web`, `api`)
   - **Subject:** Imperative mood, lowercase, no period, max 72 chars

3. **Message structure:**

   ```
   type(scope): brief description of what changed

   - Why this change was made
   - Additional context if multiple related changes
   ```

4. **Quality checklist:**
   - Does it explain WHY, not just WHAT?
   - Is it clear to someone unfamiliar with the context?
   - Would this help in a `git blame` 6 months from now?
   - Does it match the style of recent commits in the repo?

### 5. Commit

**AI Task:** Create the commit. Always proceed automatically - do not ask for confirmation.

```bash
git commit -m "$(cat <<'COMMIT'
type(scope): brief description

- Explanation of why
- Additional context if needed
COMMIT
)"
```

- Verify commit was created successfully
- If pre-commit hooks fail, fix the issues and retry with a NEW commit (never `--amend`)

### 6. Commit Report

**AI Task:** Provide a brief summary:

```markdown
## Committed

**Branch:** `[current-branch]`
**Commit:** `[short-hash]` - [commit subject]

### Files Changed

| File | Change |
|------|--------|
| `[file1]` | Modified |
| `[file2]` | Added |

### Next Steps

- Run `/ship` to push and create a PR when ready
```

## Commit Message Examples

**Good:**

```
feat(compliance): flag NAFDAC registration gaps in the review screen

- Surfaces regulator hits inline so agents catch issues before filing
- Grounds each flag in the retrieved regulatory text (RAG)
```

```
fix(extraction): handle missing line items in packing list parse

- Prevents crash when a packing list has no itemized rows
- Falls back to invoice line items when the packing list is sparse
```

```
refactor(api): extract S3 presign logic into a shared helper

- Deduplicates presigned-URL generation across upload routes
- Keeps file uploads going browser to S3 directly, not through the API
```

**Bad:**

```
updated stuff
```

```
fix bug
```

## Error Handling

| Error | Action |
|-------|--------|
| No changes to commit | Notify user and stop |
| Sensitive files detected | Warn user, exclude from staging |
| Pre-commit hook fails | Fix issues, create NEW commit |
| Staging area empty after filtering | Notify user, nothing to commit |
