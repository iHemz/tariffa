# Start of Day Briefing

Quick forward-looking briefing: what needs attention, what's the plan for today, and where to start.

## Steps

### 1. Read OUTCOMES.md

Read the outcomes backlog at `docs/OUTCOMES.md`. Each outcome block has a heading (`## O### — title`), a `**Status:**` field (`SHIPPED`, `NOT STARTED`, `IN PROGRESS`, `RESCOPED`, `BLOCKED`, etc.), and a `**Priority:**` field (P0/P1).

Identify the **active, incomplete** outcomes — anything whose status is NOT `SHIPPED` and NOT a no-build rescope (e.g. `RESCOPED — no engineering build`). These form today's plan.

### 2. Check Open PRs

Run: `gh pr list --author="@me" --state=open --json number,title,reviewDecision,statusCheckRollup --limit 10`

Also check PRs requesting your review:
Run: `gh pr list --search "review-requested:@me" --state=open --json number,title,author --limit 10`

### 3. Check Current Branch State

Run: `git status --short`
Run: `git stash list`

### 4. Generate Morning Briefing

**AI Task:** Synthesize the above into a concise, forward-looking briefing:

1. **PRs Needing Attention:** Your open PRs awaiting review or with requested changes, plus PRs where your review is requested
2. **Uncommitted Work:** Flag any uncommitted changes or stashes that might be forgotten WIP
3. **Today's Plan:** List the active, incomplete outcomes from OUTCOMES.md in priority order (P0 before P1), each with its outcome ID, title, and current status
4. **Start Here:** The specific first outcome to work on right now — the highest-priority `NOT STARTED` or `IN PROGRESS` outcome, with a one-line note on the immediate next action (e.g. "run /architect", "resume sprint", "open PR")

### 5. Output Format

Return the briefing in this exact format:

```
## Start of Day

**PRs:**
- #<number> <title> — <status: awaiting review / changes requested / checks failing>
- Review requested: #<number> <title> by <author>

**Uncommitted Work:**
- <branch: description of changes> (or "Clean working tree")

**Today's Plan:**
1. <O### — outcome title> (P0, <status>)
2. <O### — outcome title> (P1, <status>)
3. <O### — outcome title> (P1, not started)

**Start Here:**
→ <O### — outcome title> — <immediate next action>
```

If any section has no items, omit it entirely to keep the briefing short.

Done.
