---
name: validate
description: Comprehensive validation pipeline - build, runtime, and integration testing
argument-hint: "[build|runtime|integration|all]"

---

# Validate: Runtime & Build Verification

Run comprehensive validation checks on the codebase, including build, runtime, and integration testing. Use this to verify code quality before commits or to diagnose issues.

**Input:** $ARGUMENTS (optional) — Validation scope: `build`, `runtime`, `integration`, or `all` (default)

---

## Step 1: Determine Validation Scope

Parse `$ARGUMENTS` to determine what to validate:

- **`build`** — Build & compile validation only
- **`runtime`** — Runtime error detection only
- **`integration`** — Integration testing only
- **`all`** or no arguments — Run all three (recommended)

---

## Step 2: Run Validations

Based on scope, run the appropriate checks. Run independent checks **in parallel** (one message, multiple Bash calls) for speed.

### Build Validation (if scope includes `build` or `all`)

Static checks across both apps:

```bash
# apps/web — types and lint
pnpm --filter web run typecheck
pnpm --filter web run lint

# apps/api — lint
uv run ruff check apps/api
```

Report all errors and warnings.

### Runtime Validation (if scope includes `runtime` or `all`)

Start each app's dev server, watch for startup/runtime errors, and confirm critical routes respond:

```bash
# apps/web dev server
pnpm --filter web run dev

# apps/api dev server
uv run fastapi dev apps/api
```

Hit the key pages/endpoints, capture any console errors, stack traces, or non-2xx responses, then stop the servers. Report all failures.

### Integration Testing (if scope includes `integration` or `all`)

Run the backend test suite and exercise the agent pipeline / API end-to-end:

```bash
uv run pytest apps/api
```

Verify the pipeline handoffs (extraction → classification → compliance → Form M prep) and any API routes the web client calls. Report all failures with full context.

---

## Step 3: Consolidate Results

After all checks complete, consolidate the results:

```markdown
# Validation Report

## Overall Status: ✅ PASS | ⚠️ WARNINGS | ❌ FAIL

---

## Build Validation
[typecheck / lint / ruff results]

---

## Runtime Validation
[dev server startup + critical route results]

---

## Integration Testing
[pytest + pipeline/API results]

---

## Summary

### Errors
- Build Errors: [count]
- Runtime Errors: [count]
- Integration Failures: [count]

### Warnings
- Build Warnings: [count]
- Runtime Warnings: [count]

### Recommendations
[If failures, list priority fixes]

---

## Next Steps

- ✅ All validations passed → Ready to commit
- ⚠️ Warnings only → Review warnings, consider fixing
- ❌ Failures detected → Fix errors before committing
```

---

## Usage Examples

### Validate Everything (Recommended)
```
/validate
```
or
```
/validate all
```

### Validate Build Only (Quick Check)
```
/validate build
```

### Validate Runtime Only (After Code Changes)
```
/validate runtime
```

### Validate Integration Only (After API Changes)
```
/validate integration
```

---

## When to Use

- **Before commits** — Catch errors before they enter git history
- **After refactoring** — Verify nothing broke
- **Before PR creation** — Ensure production readiness
- **Debugging runtime errors** — Systematically identify issues
- **After dependency updates** — Verify compatibility

---

## Critical Rules

- **PARALLEL EXECUTION** — Run independent checks in parallel when scope is `all`
- **REPORT ONLY** — Validation never modifies code; fixing is a separate step
- **COMPREHENSIVE** — Include full context for all failures
- **ACTIONABLE** — Provide clear next steps for fixing issues
