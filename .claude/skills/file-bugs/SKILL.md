---
name: file-bugs
description: "File and organize bug reports for a feature or page. You describe the bugs (with optional screenshots), Claude formats them into structured reports organized by date and feature under docs/bug-reports/. Use when you say 'file bugs', 'log bugs', 'report bugs', 'file a bug for [feature]', 'document these bugs', or want to record bugs you've found during development — even if you just paste a screenshot and say 'this is broken'."
argument-hint: "[feature-or-page-name]"
---

# File Bugs

Organize and file bug reports that developers have found during their work. You describe the bugs, provide screenshots if you have them, and this skill formats everything into clean, structured reports filed under `docs/bug-reports/`.

This is a **documentation** skill, not a detection skill — you bring the bugs, Claude organizes them.

## Input

- `$ARGUMENTS` — The feature or page area the bugs relate to (e.g., `upload`, `review screen`, `form-m-export`).

## Step 1: Set Up

### 1.1 Get the Feature Area

If `$ARGUMENTS` is empty, ask:
> "Which feature or page are these bugs for? (e.g., `upload`, `review screen`, `compliance flags`)"

### 1.2 Create Report Directory

```
docs/bug-reports/YYYY-MM-DD/{feature-slug}/
```

- Date: today's date, `YYYY-MM-DD` format
- Feature slug: lowercase, hyphens for spaces (e.g., `partner-settings`)
- If the folder already exists for today, append a counter: `upload-2/`

```bash
mkdir -p docs/bug-reports/YYYY-MM-DD/{feature-slug}
```

### 1.3 Get Current Branch

```bash
git branch --show-current
```

Store for the report header.

## Step 2: Collect Bugs

**AI Task:** Gather bug details from the user. This is an interactive loop — keep collecting until the user says they're done.

Ask:
> "Describe the first bug. You can:
> - Type a description (e.g., 'the shipment list shows wrong date format')
> - Paste a screenshot
> - Do both
>
> I'll keep collecting bugs until you say 'done'."

### For Each Bug

1. **Assign an ID:** `BUG-001`, `BUG-002`, etc. (global counter for the report)

2. **Extract from the user's input:**
   - **Title:** Short summary (generate from description if user doesn't provide one)
   - **Description:** What's wrong
   - **Expected behavior:** What should happen (ask if not obvious from description)
   - **Screenshot:** If the user pastes/provides one

3. **Determine metadata (infer, don't interrogate):**
   - **Severity:** Infer from description. Use this guide:
     - **Critical:** Page crashes, data loss, security issue, completely broken
     - **High:** Feature doesn't work, blocks user flow, significant visual breakage
     - **Medium:** Cosmetic issues visible to most users, minor functional issues
     - **Low:** Minor cosmetic, edge-case, dev-only
   - **Category:** Infer the type:
     - `layout` — alignment, spacing, overflow, grid issues
     - `typography` — text truncation, wrong fonts, overlapping text
     - `component` — broken UI components, missing states, wrong behavior
     - `data` — wrong data displayed, missing data, stale data
     - `interaction` — broken clicks, forms not submitting, navigation issues
     - `network` — failed API calls, timeouts, wrong responses
     - `console-error` — JS errors, unhandled exceptions
     - `dark-mode` — theme/contrast issues
     - `responsive` — mobile/tablet layout issues
   - **Page/URL:** Infer from context or ask if unclear

4. **Save screenshots:** If the user provides a screenshot, save it to the report directory:
   ```
   docs/bug-reports/YYYY-MM-DD/{feature-slug}/bug-001.png
   ```
   Name screenshots by bug ID for clear association.

5. **Confirm and continue:**
   > "Got it — filed as BUG-001: {title} ({severity}). Next bug? (or say 'done')"

Keep the loop tight — don't ask 5 questions per bug. Infer what you can, only ask when something is genuinely ambiguous.

## Step 3: Generate Report

**AI Task:** Write the report to `docs/bug-reports/YYYY-MM-DD/{feature-slug}/REPORT.md`.

**Template:**

````markdown
# Bug Report: {Feature Name}

**Date:** YYYY-MM-DD
**Branch:** {branch}
**Filed by:** {user} via Claude

---

## Summary

| Severity | Count |
|---|---|
| Critical | X |
| High | X |
| Medium | X |
| Low | X |
| **Total** | **X** |

---

## Bugs

### BUG-001: {Title}

| Field | Value |
|---|---|
| **Severity** | {critical / high / medium / low} |
| **Category** | {category} |
| **Page** | {page or URL path} |

**Description:**
{What's wrong — from the user's description}

**Expected:**
{What should happen}

**Screenshot:**
![BUG-001](./bug-001.png)

---

### BUG-002: {Title}

...

---

*Filed on YYYY-MM-DD via /file-bugs*
````

**Formatting rules:**
- Each bug gets its own `###` section with the table + description format above
- Screenshots use relative paths (`./bug-001.png`) so they render in GitHub
- If no screenshot was provided for a bug, omit the Screenshot line entirely
- Keep descriptions concise but complete — capture the user's words, don't over-edit them
- Sort bugs by severity (critical first, low last)

## Step 4: Present and Offer Next Steps

After writing the report, show the user:

1. A quick summary: "{N} bugs filed for {feature} at `docs/bug-reports/YYYY-MM-DD/{feature-slug}/REPORT.md`"
2. List the bugs briefly (ID + title + severity)
3. Ask:
   > "Would you like me to:
   > - File more bugs for another feature?
   > - Create a PR with these bug reports?
   > - Investigate any of these bugs (using `/find-bug`)?"

If the user says "create a PR" or the conversation naturally leads there, use the `/ship` skill to branch, commit, push, and create a PR with the bug report files.

---

## Notes

- **Multiple features in one session:** If the user wants to file bugs across multiple features, create separate subfolders and reports per feature. After all features are done, create a top-level summary at `docs/bug-reports/YYYY-MM-DD/SUMMARY.md`:

  ```markdown
  # Bug Report Summary — YYYY-MM-DD

  | Feature | Bugs | Critical | High | Medium | Low | Report |
  |---|---|---|---|---|---|---|
  | Upload | 3 | 0 | 1 | 2 | 0 | [View](./upload/REPORT.md) |
  | Review screen | 1 | 0 | 0 | 1 | 0 | [View](./review-screen/REPORT.md) |
  ```

- **Screenshots are optional** — not every bug needs one. Text descriptions are fine on their own.

- **Don't over-interrogate** — the user is busy. Infer severity, category, and expected behavior where possible. Only ask when genuinely ambiguous. One question per bug maximum.

- **Incremental filing** — if the user comes back later the same day to file more bugs for the same feature, check if a folder exists and append a counter (`upload-2/`) rather than overwriting.
