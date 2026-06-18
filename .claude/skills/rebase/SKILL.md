---
name: rebase
description: Rebase current branch onto target, auto-resolving all conflicts
---

# Rebase with Auto Conflict Resolution

Rebase the current branch onto a target branch, automatically resolving every conflict encountered and continuing until the rebase completes successfully.

## Input

- `$ARGUMENTS` - Target branch to rebase onto (e.g., `main`, `develop`). Defaults to `main` if blank.

## Steps

### 1. Pre-flight Checks

**AI Task:** Validate the repo is in a clean state ready for rebase:

```bash
git status
```

1. **Check for dirty working tree:**
   - If there are uncommitted changes, warn the user and STOP
   - Staged but uncommitted changes also block rebase — warn and STOP

2. **Check for in-progress operations:**
   - If a rebase/merge/cherry-pick is already in progress, ask the user whether to `--abort` or `--continue`

3. **Identify branches:**
   - Current branch: `git branch --show-current`
   - Target branch: `$ARGUMENTS` or `main` if not provided

4. **Fetch latest from remote:**

   ```bash
   git fetch origin
   ```

5. **Preview the rebase scope:**

   ```bash
   git log --oneline [target-branch]..HEAD
   ```

   - Show the user how many commits will be replayed
   - If zero commits, inform the user the branch is already up to date and STOP

### 2. Start the Rebase

**AI Task:** Begin the rebase operation:

```bash
git rebase origin/[target-branch]
```

- If the rebase completes with no conflicts, skip to **Step 6 (Final Report)**
- If conflicts occur, proceed to **Step 3**

### 3. Resolve Conflicts (Loop Entry)

**AI Task:** This step repeats for every commit that has conflicts. For each round:

#### 3a. Identify Conflicted Files

```bash
git status
```

- List all files marked as "both modified", "both added", "deleted by us/them", etc.
- Note the commit being applied:

```bash
git log --oneline -1 REBASE_HEAD
```

#### 3b. Understand Both Sides

For each conflicted file:

1. **Read the file** with conflict markers intact
2. **Review the commit being applied:**

   ```bash
   git show REBASE_HEAD --stat
   git log --oneline -1 REBASE_HEAD
   ```

3. **Review what's on the target side:**

   ```bash
   git log --oneline -3 HEAD
   ```

4. **Classify each conflict block** (`<<<<<<<` ... `=======` ... `>>>>>>>`) into:

   | Category | Strategy |
   |----------|----------|
   | **Additive** | Keep both additions in logical order |
   | **Superseding** | Keep the more complete/recent change |
   | **Divergent** | Synthesize a merged version honoring both intents |
   | **Formatting** | Use project style conventions |
   | **Import/Dependency** | Keep all unique imports, deduplicate |
   | **Structural** | Careful manual merge considering final structure |
   | **Deletion** | If one side deleted and the other modified, determine which intent wins |

#### 3c. Resolve Each File

For each conflicted file:

1. **Remove all conflict markers** and produce the correct merged content using the Edit tool
2. **Verify no markers remain:**

   ```bash
   grep -n "^<<<<<<<\|^=======\|^>>>>>>>" [file]
   ```

3. **For TypeScript/React files (`apps/web`), check for:**
   - Duplicate imports (deduplicate them)
   - Duplicate declarations
   - Inconsistent type references
   - Broken import paths

4. **For Python files (`apps/api`), check for:**
   - Duplicate or conflicting imports (deduplicate them)
   - Duplicate function/class definitions
   - Pydantic model fields that diverged between the two sides
   - Broken import paths

#### 3d. Validate Resolution

Run the gates for whichever app the resolved files belong to (run both if the conflict touched both):

```bash
# Frontend (apps/web)
pnpm --filter web run typecheck 2>&1 | head -80
pnpm --filter web run lint 2>&1 | head -80
```

```bash
# Backend (apps/api)
ruff check apps/api 2>&1 | head -80
```

- If errors exist, fix them and re-validate
- Repeat until they pass cleanly (or errors are clearly pre-existing / unrelated to the conflict)

#### 3e. Stage and Continue

```bash
git add [resolved-files]
git rebase --continue
```

- If `git rebase --continue` succeeds with no new conflicts, check:
  - **Rebase complete?** -> Go to **Step 6**
  - **Next commit also has conflicts?** -> Loop back to **Step 3a**
- If `git rebase --continue` fails due to remaining conflicts, loop back to **Step 3a**

### 4. Handle Edge Cases

**AI Task:** If any of these occur during the loop, handle them:

1. **Empty commit after resolution:**

   ```bash
   git rebase --skip
   ```

   - This happens when the conflict resolution results in no net change for that commit

2. **Binary file conflicts:**
   - Cannot auto-resolve — ask the user which version to keep (ours or theirs)

3. **File deleted on one side, modified on the other:**
   - Determine intent: if the target branch deleted the file and our commit modified it, usually accept the deletion unless our change is critical
   - If our branch deleted and theirs modified, usually accept the deletion
   - When in doubt, ask the user

4. **Repeated failures on the same commit:**
   - If the same commit fails resolution 3 times, ask the user whether to `--skip` or abort

### 5. Post-Rebase Validation

**AI Task:** After the rebase completes, run a final validation across both apps:

```bash
# Frontend (apps/web)
pnpm --filter web run typecheck 2>&1 | head -80
pnpm --filter web run lint 2>&1 | head -80
```

```bash
# Backend (apps/api)
ruff check apps/api 2>&1 | head -80
pytest apps/api 2>&1 | head -80
```

- Fix any issues introduced during rebase
- Ensure the codebase is in a clean, working state

### 6. Final Report

**AI Task:** Provide a summary of the rebase:

```markdown
## Rebase Complete

**Branch:** `[current-branch]` rebased onto `[target-branch]`
**Commits replayed:** [count]
**Conflicts resolved:** [count] across [count] commits

### Conflict Resolution Summary

| Commit | File | Conflicts | Strategy | Notes |
|--------|------|-----------|----------|-------|
| `[short-hash]` | `apps/web/.../file.tsx` | 2 | Additive | Merged both import blocks |
| `[short-hash]` | `apps/api/.../file.py` | 1 | Superseding | Kept target's implementation |

### Validation

- Frontend typecheck: PASS/FAIL
- Frontend lint: PASS/FAIL
- Backend ruff: PASS/FAIL
- Backend pytest: PASS/FAIL

### Next Steps

- Review the conflict resolutions above for correctness
- Run your tests to verify behavior
- Force push if this branch was previously pushed: `git push --force-with-lease`
```

Done.
