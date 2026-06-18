---
name: enterprise-readiness-review
description: Enterprise Readiness Review

---

# Enterprise Readiness Review

Evaluate PR changes for enterprise-grade scalability - is this code ready for a 100-engineer team to maintain, extend, and onboard onto?

## Input

- `{{base_branch}}` - Base branch to compare against (default: `main`)

## Steps

### 0. Git Prerequisite (1 command)

Fetch and analyze the full PR diff:

```bash
BASE_BRANCH="${base_branch:-main}"
git fetch origin "$BASE_BRANCH" && \
echo "----- PR COMMITS -----" && git log --oneline "origin/$BASE_BRANCH..HEAD" && \
echo "----- FILES CHANGED -----" && git diff "origin/$BASE_BRANCH...HEAD" --name-status && \
echo "----- CHANGE STATS -----" && git diff "origin/$BASE_BRANCH...HEAD" --stat && \
echo "----- FULL DIFF -----" && git diff "origin/$BASE_BRANCH...HEAD"
```

### 1. Enterprise Scalability Assessment

**AI Task:** Review the PR through the lens of a 100-engineer organization:

#### 1.1 Module Boundaries & Ownership

- **Clear ownership:** Can a single team own this code without stepping on others?
- **Boundary violations:** Does the code reach into other modules inappropriately?
- **Coupling:** Would changes here force changes in unrelated modules?
- **Import direction:** Are imports flowing correctly (no circular dependencies)?

#### 1.2 Onboarding & Discoverability

- **Self-documenting:** Can a new engineer understand intent without asking someone?
- **Naming clarity:** Do names communicate purpose, not implementation?
- **Consistent patterns:** Does the code follow established patterns in the codebase?
- **Docstring/JSDoc coverage:** Are public APIs and complex functions documented (Python docstrings in `apps/api`, JSDoc/types in `apps/web`)?

#### 1.3 Contract Stability

- **API contracts:** Are inputs/outputs well-typed with clear schemas?
- **Breaking change risk:** Could internal changes accidentally break consumers?
- **Versioning consideration:** Is the code structured to allow non-breaking evolution?
- **Interface abstraction:** Are implementations hidden behind stable interfaces?

#### 1.4 Testing & Confidence

- **Test coverage:** Are critical paths tested?
- **Test isolation:** Can tests run independently without shared state?
- **Mock boundaries:** Are external dependencies properly abstracted for testing?
- **Failure scenarios:** Are error cases and edge conditions covered?

#### 1.5 Operational Readiness

- **Observability:** Can issues be debugged from logs/metrics alone?
- **Error handling:** Are errors actionable with context?
- **Graceful degradation:** Does the code handle partial failures?
- **Configuration:** Are magic values externalized appropriately?

#### 1.6 Team Collaboration Patterns

- **PR reviewability:** Can this be reviewed in <30 minutes by someone unfamiliar?
- **Atomic commits:** Are changes logically grouped?
- **Blast radius:** If this breaks, what's the impact scope?
- **Feature flags:** Should this be behind a flag for safe rollout?

### 2. Generate Enterprise Readiness Report

**AI Task:** Produce a structured assessment:

```markdown
## Enterprise Readiness Review

**PR:** <branch name> → {{base_branch}}
**Files Changed:** <count files, +additions/-deletions lines>
**Modules Affected:** <list affected modules>

### 🏢 Scalability Scorecard

| Dimension                    | Score  | Notes                 |
| ---------------------------- | ------ | --------------------- |
| Module Boundaries            | 🟢🟡🔴 | <one-line assessment> |
| Onboarding & Discoverability | 🟢🟡🔴 | <one-line assessment> |
| Contract Stability           | 🟢🟡🔴 | <one-line assessment> |
| Testing & Confidence         | 🟢🟡🔴 | <one-line assessment> |
| Operational Readiness        | 🟢🟡🔴 | <one-line assessment> |
| Team Collaboration           | 🟢🟡🔴 | <one-line assessment> |

**Overall:** 🟢 Enterprise Ready | 🟡 Needs Hardening | 🔴 Significant Gaps

### 🎯 Critical Issues

<Issues that MUST be addressed before merge - list with specific locations>

### ⚠️ Recommendations

| Priority | Issue         | Location    | Suggested Fix           |
| -------- | ------------- | ----------- | ----------------------- |
| P1/P2/P3 | <description> | `file:line` | <actionable suggestion> |

### 📋 Team Scale Considerations

**If 10 engineers touched this module simultaneously:**

- <What would break? What would cause merge conflicts?>

**If a new engineer started tomorrow:**

- <What would confuse them? What would they need explained?>

**If this code had a bug at 3 AM:**

- <Could on-call debug it from logs? What context is missing?>

### ✅ What's Done Well

- <Specific examples of enterprise-ready patterns>

### 📌 Suggested Improvements (Priority Order)

1. **[P1]** <Most critical improvement>
2. **[P2]** <Second priority>
3. **[P3]** <Nice to have>

### 🚀 Verdict

<READY TO MERGE | MERGE WITH FOLLOW-UPS | NEEDS CHANGES>

<Brief explanation of verdict and any required follow-up tasks>
```

### 3. Output

Return the enterprise readiness report directly.

Done.
