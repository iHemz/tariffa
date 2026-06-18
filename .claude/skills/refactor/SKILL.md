---
name: refactor
description: Refactor Code
---

Perform structured refactoring while maintaining functionality and improving quality.

## Input

- `{{target}}` - File path, function name, or component to refactor. Leave blank to be prompted.
- `{{refactor_type}}` - Type of refactoring (optional): `extract`, `rename`, `restructure`, `dry`, `pattern`, `move`, `simplify`, or blank for analysis.

## Prerequisites

- Working in the tariffa repository (`apps/web` Next.js frontend or `apps/api` FastAPI backend)
- Code to refactor exists and is functional
- Git working tree is clean (recommended)

## Steps

### 1. Validate Inputs

**AI Task:** Check inputs are provided:

1. **If `{{target}}` is empty:**
   - Ask: "What would you like to refactor? Please provide a file path, function name, or component name."
   - Wait for response before proceeding

2. **If `{{refactor_type}}` is empty:**
   - Proceed with analysis mode (Step 2) to suggest refactoring opportunities
   - Otherwise, proceed to Step 3 with the specified type

### 2. Analyze Code for Refactoring Opportunities

**AI Task:** Read and analyze the target code:

1. **Locate the code:**
   - Use `Glob` to find files matching the target
   - Use `Grep` to find functions/components by name
   - Use the Explore agent if the target is conceptual (e.g., "the compliance classification logic")

2. **Read the code:**
   - Read the full file(s) containing the target
   - Understand the current implementation
   - Note dependencies and consumers

3. **Identify refactoring opportunities:**

   | Type            | Indicators                                                        |
   | --------------- | ----------------------------------------------------------------- |
   | **Extract**     | Long functions (>50 lines), repeated code blocks, mixed concerns  |
   | **Rename**      | Unclear names, misleading names, inconsistent naming conventions  |
   | **Restructure** | Deep nesting, complex conditionals, unclear data flow             |
   | **DRY**         | Duplicated logic across files, copy-pasted patterns               |
   | **Pattern**     | Missing abstractions, opportunities for design patterns           |
   | **Move**        | Code in wrong module/layer, tight coupling, circular dependencies |
   | **Simplify**    | Over-engineered solutions, unnecessary complexity, dead code      |

4. **Generate analysis report:**

```markdown
## Refactoring Analysis: [target]

### Current State

- **Location:** `path/to/file.ts`
- **Lines:** X-Y (Z lines total)
- **Dependencies:** [list imports/consumers]
- **Complexity:** [low/medium/high]

### Identified Opportunities

| Priority | Type   | Description   | Impact   |
| -------- | ------ | ------------- | -------- |
| 1        | [type] | [description] | [impact] |

### Recommended Approach

[Description of suggested refactoring strategy]

Proceed with refactoring? (specify type or number from table)
```

### 3. Plan the Refactoring

**AI Task:** Based on `{{refactor_type}}`, create a detailed plan:

#### For `extract`:

- Identify code blocks to extract
- Determine extraction target (function, hook, component, service method)
- Plan parameter passing and return values
- Identify shared state/dependencies

#### For `rename`:

- List all instances of the name across the codebase
- Determine new name following conventions:
  - Frontend (`apps/web`): TSX components PascalCase, functions/variables camelCase
  - Backend (`apps/api`): modules/functions/variables snake_case, Pydantic models / classes PascalCase
  - DB fields: snake_case
- Plan for updating imports and references

#### For `restructure`:

- Map current code flow
- Design improved structure
- Plan intermediate refactoring steps
- Identify breaking points

#### For `dry`:

- Identify all duplicated code locations
- Design shared abstraction
- Determine appropriate location (utils, shared, module-specific)
- Plan migration strategy

#### For `pattern`:

- Identify applicable design pattern
- Map current code to pattern structure
- Plan implementation following the conventions already in the codebase and the relevant spec in `/docs/`
- Ensure alignment with existing patterns (e.g. how other Pydantic AI agents, services, or React components in the repo are structured)

#### For `move`:

- Identify target location
- Check for circular dependency risks
- Respect the service boundary: business logic, DB, storage, and LLM calls live in `apps/api`; `apps/web` stays a thin client
- Update all import paths

#### For `simplify`:

- Identify unnecessary complexity
- Plan removal/simplification steps
- Verify no functionality loss
- Check for hidden side effects

### 4. Pre-Refactoring Checklist

**AI Task:** Verify safety before making changes:

1. **Check git status:**

   ```bash
   git status --porcelain
   ```

   - Warn if uncommitted changes exist
   - Recommend committing or stashing first

2. **Identify all affected files:**
   - Use `Grep` to find all usages of code being refactored
   - List files that will need updates

3. **Check for tests:**
   - Find existing tests for the code
   - Note test coverage gaps

4. **Verify understanding:**
   - Summarize what the code currently does
   - Confirm with user if complex or unclear

### 5. Execute Refactoring

**AI Task:** Implement changes systematically:

#### 5.1 Create New Abstractions (if applicable)

- Create new files/functions/components
- Follow project conventions:
  - Keep business logic, DB access, storage, and LLM/agent calls in `apps/api`
  - Use Pydantic models as the typed contract — every agent-to-agent handoff is a validated Pydantic model, never a raw dict
  - Keep the compliance agent grounded in retrieved regulatory text (RAG), never the model's unverified knowledge
  - Mirror the structure of existing modules; check the relevant spec in `/docs/` if unsure

#### 5.2 Migrate Code

- Move code to new locations
- Update signatures and interfaces
- Maintain functionality at each step

#### 5.3 Update Consumers

- Update all import statements
- Update function calls/component usage
- Ensure type safety throughout

#### 5.4 Clean Up

- Remove old/dead code
- Remove unused imports
- Update any barrel/`__init__.py` exports affected by the move
- Maintain the `apps/web` (thin client) ↔ `apps/api` (all logic) boundary

### 6. Validate Changes

**AI Task:** Run the quality gates for whichever app you touched (run both if the refactor spans both):

```bash
# Frontend (apps/web)
pnpm --filter web run typecheck
pnpm --filter web run lint

# Backend (apps/api)
ruff check apps/api
pytest apps/api
```

**If validation fails:**

- Identify the issue
- Fix without compromising the refactoring goals
- Re-run validation
- Do NOT proceed until all pass

### 7. Verify Functionality

**AI Task:** Ensure refactoring didn't break anything:

1. **Structural verification:**
   - All imports resolve correctly
   - No circular dependencies introduced
   - `apps/web` ↔ `apps/api` boundary maintained (frontend never talks to DB/S3/LLM directly)

2. **Behavioral verification:**
   - Logic is functionally equivalent
   - No unintended side effects
   - Edge cases still handled

3. **Pattern compliance:**
   - Matches the conventions of surrounding code and the relevant `/docs/` spec
   - Pipeline handoffs are still validated Pydantic models, not raw dicts
   - Auth checks still gate the endpoints/pages they should

### 8. Update Documentation

**AI Task:** Update related documentation:

1. **If new patterns introduced:**
   - Update the relevant spec in `/docs/`
   - Add docstrings / JSDoc comments to new abstractions

2. **If module structure changed:**
   - Update the module's exports (`index.ts` on the frontend, `__init__.py` on the backend)

### 9. Generate Refactoring Report

**AI Task:** Produce summary:

```markdown
## Refactoring Complete ✅

**Target:** {{target}}
**Type:** {{refactor_type}}

### Changes Summary

| File              | Change        | Lines |
| ----------------- | ------------- | ----- |
| `path/to/file.ts` | [description] | +X/-Y |

**Total:** X files modified, Y lines added, Z lines removed

### Before/After Comparison

**Before:**

- [Description of original state]
- [Key metrics: lines, complexity, duplication]

**After:**

- [Description of new state]
- [Improved metrics]

### Quality Improvements

- ✅ [Specific improvement 1]
- ✅ [Specific improvement 2]
- ✅ [Specific improvement 3]

### Validation Results

- ✅ `pnpm --filter web run typecheck` - passed
- ✅ `pnpm --filter web run lint` - passed
- ✅ `ruff check apps/api` - passed
- ✅ `pytest apps/api` - passed

### Suggested Commit Message
```

refactor([module]): [brief description]

[Detailed explanation of what was refactored and why]

- [Change 1]
- [Change 2]

```

### Next Steps

1. Review the changes
2. Run `/code-review` to verify quality
3. Test affected functionality manually
4. Commit changes
```

## Refactoring Type Reference

| Type          | Use When                                | Example                                                        |
| ------------- | --------------------------------------- | ------------------------------------------------------------- |
| `extract`     | Code is doing too much, repeated blocks | Extract `validate_hs_code()` from a 200-line agent function   |
| `rename`      | Names don't reflect purpose             | Rename `data` to `extracted_invoice`                          |
| `restructure` | Hard to follow logic flow               | Flatten nested conditionals in the compliance checker         |
| `dry`         | Same logic in multiple places           | Create a shared `format_hs_code()` helper                     |
| `pattern`     | Missing abstraction opportunities       | Give each pipeline stage a consistent typed input/output shape|
| `move`        | Code in wrong location                  | Move LLM call out of a route handler into an agent module     |
| `simplify`    | Over-engineered or complex              | Remove unused abstraction layers                              |

## Output

Return the refactoring report and ask if user wants to commit the changes.

Done.
