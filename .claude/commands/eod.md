# End of Day Summary

Generate a *tight* End of Day summary covering the substantive things you worked on today. Respect the reader's time — lead with what matters most, keep each point sharp, and don't pad. Include every thread worth knowing about, but cut chores and polish.

## Steps

### 1. Get today's commits

```
git log --since="20 hours ago" --pretty=format:"%h|%ad|%an|%D|%s" --date=format:"%m-%d %H:%M" --all
```

Then narrow to **your** work and **today's** session — but do it with judgment, not a brittle filter:

- **Author** — `git config user.name` is NOT enough. Squash-merged PRs are re-attributed to a different display name (your local config name vs. the squash-merge display name GitHub records can differ). Match commits whose author name OR email belongs to you. Check both identities:
  ```
  git config user.name
  git config user.email
  ```
  When in doubt, include the commit — a near-miss is better than silently dropping a shipped PR.
- **Day boundary** — `--since="midnight"` silently drops everything when you worked late and the date has rolled past midnight (commits timestamped yesterday evening are still "today's work" for an EOD run the next morning). The 20-hour window above is deliberately generous; from it, pick the contiguous block that is this working session. If the window is empty or clearly spans two distinct days, widen it (`--since="36 hours ago"`) and use judgment.

Also capture branch context (needed for outcome mapping of unmerged work):

```
git branch --show-current
```

### 2. Map commits to outcomes

Each commit belongs to an outcome (e.g. `O139`, `O139b`). Resolve the outcome in this order:

1. **Branch name** — `sprint/O###-S#-...` or `feat/...-O###-...` embeds the outcome ID
2. **PR merge commits** — `Merge pull request #X from <owner>/sprint/O###-S#-...`
3. **Commit scope** — e.g. `feat(api):` is ambiguous; fall back to branch/PR context

Look up the outcome title from `docs/OUTCOMES.md` (grep `^## O###`). Strip the `O###` prefix — the reader only cares about the human title. If the outcome isn't in OUTCOMES.md, derive a short human title from the branch/PR context.

### 3. Pick the things that matter

From everything today, select the points you'd regret not knowing tomorrow morning. Order them like this:

1. **Shipped / merged** user-facing or substantive work
2. **Substantial unmerged work** in progress
3. **Risk / gotcha / heads-up** — unmerged work, production behavior change, something that would surprise you when you pick this back up — always **last**

Heads-ups go at the bottom so you end on what needs attention next. Everything else — chores, renames, polish — is **dropped entirely**. Do not mention it. Include every substantive thread, but never pad with filler.

### 4. Output format (Slack-friendly)

The summary is copy-pasted straight into Slack. Use Slack `mrkdwn`, **not** GitHub markdown:

- `*bold*` — single asterisks
- `• ` bullets (not `- `)
- No `#`/`##` headings
- Plain text links only

Each bullet: keep it sharp (aim for ≤12 words), lead with an active verb (Shipped, Merged, Fixed, Added). Prefix outcome context only if it disambiguates. State the change, not the motivation. Group bullets under bold outcome labels when that aids scanning.

Wrap in a ` ```text ... ``` ` code fence so the user can triple-click to copy.

Template:

```text
*End of Day*
• <most important shipped/merged thing>
• <other substantive work>
• <heads-ups / risks — always last>
```

### 5. Self-review before output

Before emitting, verify all of these — re-edit until every answer is yes:

1. Would you regret missing each bullet tomorrow? (If any bullet is "ok and?", cut it.)
2. Is every bullet sharp with no filler ("now", "in order to", "so users can")?
3. Are chores and polish dropped entirely?
4. No AI agents / orchestrators / internal tooling mentioned?
5. Are heads-ups / risks last, after all shipped and in-progress work?
6. **Sanity check the count** — if the summary has ≤2 substantive bullets, suspect a filter dropped work. Re-run Step 1 with a wider window and both author identities (name + email, including squash-merge attribution) before emitting. A thin EOD is almost always a query bug, not a quiet day.

Only emit once all of these are yes.

Done.
