---
name: review-and-plan
description: Review Yesterday & Plan Today

---

# Review Yesterday & Plan Today

Review completed work from yesterday, mark tasks as done in `TODO.md`, and set up today's focus. Optionally mirror the status to GitHub issues.

## Steps

### 1. Read TODO.md

Read the `TODO.md` file from the project root.

### 2. Review Yesterday's Work

**AI Task:** Analyze `TODO.md` to identify work completed yesterday:

1. **Identify Completed Work:**
   - Look for tasks that appear to be done but may not be marked `[x]`
   - Check git history (`git log --oneline -20`) for recent commits
   - Cross-reference commits with TODO items

2. **Mark Completed Tasks:**
   - Update `[ ]` to `[x]` for any tasks that were completed
   - Only change checkboxes, do not modify task descriptions
   - Be conservative — only mark tasks that are definitively complete

### 3. Compute Section Status

**AI Task:** For each numbered section in `TODO.md` (e.g., "## 1. Feature Name"):

1. Count `[x]` (done) vs `[ ]` (pending) sub-tasks in the section
2. Derive the status:
   - **ALL done** → `Completed`
   - **SOME done** → `Active`
   - **NONE done** → `Not Started`
3. Record the status next to the section heading if the file uses status tags, otherwise just track it for the summary.

### 4. Sync GitHub Issues (Optional)

**AI Task:** If the project tracks work in GitHub issues, keep them in step with `TODO.md`:

1. List open issues: `gh issue list --json number,title,labels`
2. Match each `TODO.md` section to an issue by title/keyword
3. Close issues whose section is now `Completed` (`gh issue close <number>`)
4. Leave a brief progress comment on the section that is now `Active`

Skip this step entirely if the project has no GitHub issues — `TODO.md` is the source of truth.

### 5. Plan Today's Tasks

**AI Task:** Based on the current state of `TODO.md` after marking completions:

1. **Identify Next Priority:**
   - Find the first incomplete section (has `[ ]` sub-tasks)
   - This becomes the focus for today

2. **Add New Tasks (if needed):**
   - If new tasks are provided, insert them in the appropriate section
   - Follow the existing `TODO.md` format and numbering

### 6. Update TODO.md

Apply all changes to the `TODO.md` file:

- Mark completed tasks as `[x]`
- Do NOT remove or reorder existing content
- Maintain the existing structure and formatting

### 7. Output Summary

Return a brief summary:

```
## Review & Plan Complete

**Marked as Done:**
- <Task 1 that was marked complete>
- <Task 2 that was marked complete>

**Section Status:**
- <Section name>: <old status> → <new status>

**Today's Focus:**
- <Current priority task with progress indicator>

**Up Next:**
- <Next priority items>
```

Done.
