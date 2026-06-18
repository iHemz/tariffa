---
name: checkout-main
description: Switch from the current branch to main and fetch the latest changes. Use when the user says "checkout main", "switch to main", "go to main", "pull latest", or wants to leave their current branch and get up to date with main.
---

# Checkout Main

Switch to the `main` branch and pull the latest changes, handling in-progress rebases/merges automatically.

## Workflow

### Step 1: Check for in-progress rebase or merge

Run `git status` to detect the current state.

- **Rebase in progress** → Run `git rebase --abort`
- **Merge in progress** → Run `git merge --abort`
- **Cherry-pick in progress** → Run `git cherry-pick --abort`
- **Clean state** → Continue to Step 2

### Step 2: Check for uncommitted changes

Run `git status` again after any abort.

- **Uncommitted changes exist** → **Stop and warn the user.** List the changed files and ask whether to:
  - `git stash` the changes and proceed
  - Commit them first
  - Discard them with `git checkout -- .`
- **Working tree clean** → Continue to Step 3

### Step 3: Switch to main

```bash
git checkout main
```

If `main` doesn't exist, try `master` instead.

### Step 4: Pull latest

```bash
git pull origin main
```

Report the result: how many commits pulled, or "already up to date".

## Error Handling

| Error | Action |
|-------|--------|
| Rebase/merge in progress | Abort it automatically (Step 1) |
| Uncommitted changes | Warn user, ask how to proceed (Step 2) |
| `main` branch not found | Try `master`, then report error |
| Pull conflicts | Report the conflict and stop |
| Network error on pull | Report the error, note the branch switch succeeded |

## Success Output

After completing, confirm:
1. Which branch was left (and if a rebase/merge was aborted)
2. Now on `main`
3. Pull result (commits fetched or already up to date)
