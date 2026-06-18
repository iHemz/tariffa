---
name: product-updates
description: Collect recent work into a product update email draft. Use when the user wants to summarize shipped features for a public-facing product update or changelog email.
argument-hint: time range, e.g. "last 2 weeks" or "since 2026-02-01"
---

# Product Updates: Email Content Generator

Collect recent shipped work from git history and merged PRs, filter for publicly relevant changes, and transform them into polished product update email content.

## Input

- `$ARGUMENTS` - Time range to cover (e.g., "last 2 weeks", "since 2026-02-01", "January"). Defaults to the last 2 weeks if blank.

## Steps

### 1. Determine Time Range

**AI Task:** Parse the time range from `$ARGUMENTS`:

- If a date or range is given, use it directly
- If a relative phrase like "last 2 weeks", calculate the date
- If blank, default to 14 days ago

Store as `$SINCE_DATE` in `YYYY-MM-DD` format.

### 2. Gather Merged PRs

**AI Task:** Pull the list of merged PRs in the time range:

```bash
gh pr list --state merged --search "merged:>=$SINCE_DATE" --json number,title,body,mergedAt,labels --limit 100
```

### 3. Gather Commit History

**AI Task:** Pull commits on `main` in the time range as a supplement:

```bash
git log main --since="$SINCE_DATE" --pretty=format:"%h|%s|%an|%ad" --date=short --reverse
```

### 4. Classify Changes

**AI Task:** Review every PR title, body, and commit subject. Classify each into one of these categories:

| Category | Include in Email? | Examples |
|----------|-------------------|---------|
| **New Feature** | Yes | New UI, new capability, new integration |
| **Improvement** | Yes | UX enhancement, performance boost users notice, workflow upgrade |
| **Bug Fix (user-facing)** | Yes | Fixes to visible behavior, broken flows, data issues |
| **Bug Fix (internal)** | No | Test fixes, dev tooling, CI fixes |
| **Refactor / Tech Debt** | No | Code cleanup, dependency updates, internal restructuring |
| **Infrastructure** | No | Deployment changes, monitoring, internal tooling |
| **Documentation** | No | README updates, internal docs |

**Discard** anything in the "No" categories. Keep only changes a customer or user would care about.

### 5. Group and Summarize

**AI Task:** Group the included changes into logical themes. Don't just list PRs — synthesize related changes into cohesive update items.

**Guidelines:**
- Combine related PRs into a single update point (e.g., 3 PRs about the compliance checks become one "Compliance Pre-Check" update)
- Write from the user's perspective — what can they do now that they couldn't before?
- Use active, benefit-oriented language
- Avoid internal jargon, code terms, or implementation details
- Keep each item to 1-2 sentences max

**Tone:**
- Professional but approachable
- Focus on value and outcomes, not technical details
- Present tense ("You can now..." not "We added...")

### 6. Generate Email Content

**AI Task:** Produce the final product update content in this format:

```markdown
## Product Update — [Month Day, Year]

### What's New

**[Theme/Feature Name]**
[1-2 sentence description of what users can now do and why it matters.]

**[Theme/Feature Name]**
[1-2 sentence description.]

...

### Improvements

- [Short improvement description]
- [Short improvement description]

### Fixes

- [Short fix description — only user-facing bugs]
- [Short fix description]
```

**Rules:**
- "What's New" section: Major new features and capabilities (the headline items)
- "Improvements" section: Enhancements to existing features
- "Fixes" section: Only include if there are notable user-facing bug fixes. Omit this section entirely if there are none worth mentioning publicly
- If a section would be empty, omit it
- Order items within each section by impact (most impactful first)

### 7. Source Reference

**AI Task:** Below the email content, provide a collapsed reference linking each update item back to the PRs it came from. This is for internal use only, not for the email.

```markdown
<details>
<summary>Source PRs</summary>

| Update Item | PRs |
|-------------|-----|
| [Theme/Feature Name] | #123, #125, #130 |
| [Improvement] | #127 |
| ... | ... |

</details>
```

### 8. Present to User

**AI Task:** Present the email content and ask:

1. **Should any items be reworded, removed, or reordered?**
2. **Are there any shipped features missing that should be included?**
3. **Is the tone right for your audience?**

Wait for feedback and iterate before finalizing.

## Output

The final product update email content in markdown, ready to be copied into an email tool or newsletter platform.

Done.
