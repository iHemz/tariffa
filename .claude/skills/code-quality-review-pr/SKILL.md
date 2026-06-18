---
name: code-quality-review-pr
description: Code Quality Review (Pull Request)

---

# Code Quality Review (Pull Request)

Review Pull Request changes against the base branch for quality principles and generate a structured report.

## Steps

### 0. Git Prerequisite (1 command)

Run this command to fetch the latest and compare your PR branch against main:

Run:

```bash
git fetch origin main && \
echo "----- PR INFO -----" && git log --oneline origin/main..HEAD && \
echo "----- PR SUMMARY -----" && git diff origin/main...HEAD --name-status && git diff origin/main...HEAD --numstat && git diff origin/main...HEAD --stat && \
echo "----- PR PATCH -----" && git diff origin/main...HEAD
```

### 1. Analyze Code Changes

**AI Task:** Review the git diff (PR changes vs base branch) and evaluate against quality principles:

1. **SOLID & DRY Assessment:**
   - **S**ingle Responsibility: Does each function/class do one thing well?
   - **O**pen/Closed: Is the code extensible without modification?
   - **L**iskov Substitution: Can derived types substitute base types?
   - **I**nterface Segregation: Are interfaces focused and minimal?
   - **D**ependency Inversion: Do high-level modules depend on abstractions?
   - **DRY**: Is there repeated logic that should be abstracted?
   - **Over-engineering check**: Is the abstraction level appropriate, or excessive?

2. **Conciseness & Readability:**
   - Are variable/function names self-documenting?
   - Is the code complexity warranted by the requirements?
   - Are there unnecessary comments explaining obvious code?
   - Could any logic be simplified without losing clarity?

3. **Performance Characteristics:**
   - **Time Complexity (Big-O)**: What's the worst-case runtime?
   - **Space Complexity**: What's the memory footprint?
   - **Potential Bottlenecks**: Database calls in loops? Unbounded iterations? Memory leaks?
   - **Scalability**: Will this perform well at 10x, 100x scale?

4. **Boy Scout Rule (Leave Code Better):**
   - Did the changes improve surrounding code quality (even small cleanups)?
   - Were obvious issues in touched files addressed (dead code, outdated comments, unclear naming)?
   - Is the code left in a better state than before the change?
   - Were any quick wins missed (inconsistent formatting, minor refactors)?

### 2. Generate Quality Report

**AI Task:** Produce a structured assessment:

```
## Code Quality Review

**Files Changed:** <count files, +additions/-deletions lines>

### ✅ Strengths
- <What's done well - be specific with examples>

### ⚠️ Concerns

| Severity | Issue | Location |
|----------|-------|----------|
| High/Medium/Low | <Description> | <file:line-range> |

### 📊 Performance Analysis
- **Time Complexity:** O(?)
- **Space Complexity:** O(?)
- **Bottlenecks:** <None found / List specific issues>

### 🏕️ Boy Scout Check
- **Improvements Made:** <List any cleanup/improvements beyond the core change>
- **Missed Opportunities:** <None / List quick wins that could have been addressed>

### 📋 Verdict
<PASS | PASS WITH NOTES | NEEDS REVISION>

<Brief explanation of verdict>

### 📌 Recommended Improvements
<If concerns exist, list specific actionable improvements - ordered by priority>
```

### 3. Output

Return the quality report directly.

Done.
