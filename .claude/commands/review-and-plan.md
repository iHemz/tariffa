# Review Yesterday & Plan Today

Review completed work from yesterday, mark tasks as done in TODO.md, and set today's focus.

## Steps

### 1. Read TODO.md

Read the `TODO.md` file from the project root.

### 2. Review Yesterday's Work

**AI Task:** Analyze the TODO.md to identify work completed yesterday:

1. **Identify Completed Work:**
   - Look for tasks that appear to be done but may not be marked `[x]`
   - Check git history (`git log --oneline -20`) for recent commits
   - Cross-reference commits with TODO items

2. **Mark Completed Tasks:**
   - Update `[ ]` to `[x]` for any tasks that were completed
   - Only change checkboxes, do not modify task descriptions
   - Be conservative - only mark tasks that are definitively complete

### 3. Reconcile Status

**AI Task:** Roll up section status from the checkbox state:

1. **For each numbered section in TODO.md (e.g., "## 1. Feature Name"):**
   - Count `[x]` (done) vs `[ ]` (pending) sub-tasks in the section
   - **ALL done** → section is `COMPLETED`
   - **SOME done** → section is `Active`
   - **NONE done** → section is `Not Started`

2. **Mark next priority Active:**
   - Find the first section that is NOT `COMPLETED`
   - If it is `Not Started`, treat it as `Active` for today

3. **Optional — GitHub issues:**
   - If a section maps to a GitHub issue, you can reflect status there with `gh issue close <n>` / `gh issue edit <n>` / a status comment. Only do this when the mapping is explicit; never guess.

### 4. Plan Today's Tasks

**AI Task:** Based on the current state of TODO.md after marking completions:

1. **Identify Next Priority:**
   - Find the first incomplete section (has `[ ]` sub-tasks)
   - This becomes the focus for today

2. **Add New Tasks (if needed):**
   - If the user provides new tasks to add, insert them in the appropriate section
   - Follow the existing TODO.md format and numbering

### 5. Update TODO.md

Apply all changes to the `TODO.md` file:

- Mark completed tasks as `[x]`
- Do NOT remove or reorder existing content
- Maintain the existing structure and formatting

### 6. Output Summary

Return a brief summary:

```
## Review & Plan Complete

**Marked as Done:**
- <Task 1 that was marked complete>
- <Task 2 that was marked complete>

**Status Updated:**
- <Section name>: <old status> → <new status>

**Today's Focus:**
- <Current priority task with progress indicator>

**Up Next:**
- <Next priority items>
```

Done.
