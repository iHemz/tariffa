# Documentation Style Guide

Style guide for writing and maintaining documentation in the tariffa codebase.

## Table of Contents

- [General Principles](#general-principles)
- [File Structure](#file-structure)
- [Writing Style](#writing-style)
- [Code Examples](#code-examples)
- [Formatting Standards](#formatting-standards)
- [Cross-References](#cross-references)
- [AI Discoverability](#ai-discoverability)

---

## General Principles

### 1. Clarity First
- Write for developers who are new to the codebase
- Use clear, concise language
- Avoid jargon unless necessary (and define it when used)

### 2. Completeness
- Document all public APIs
- Include examples for common use cases
- Explain "why" not just "what"

### 3. Accuracy
- Keep documentation in sync with code
- Update docs when code changes
- Remove outdated information

### 4. Consistency
- Follow established patterns
- Use consistent terminology
- Maintain uniform structure

---

## File Structure

### Standard Sections

Every documentation file should follow this structure:

```markdown
# [Title]

[One-line description]

## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)

---

## [Section 1]

[Content]

## [Section 2]

[Content]

---

## See Also

- [Related Doc 1](./related-doc-1.md)
- [Related Doc 2](./related-doc-2.md)
```

### Required Sections

1. **Title** - Clear, descriptive heading
2. **Description** - One-line summary (optional but recommended)
3. **Table of Contents** - For documents longer than 3 sections
4. **Content Sections** - Organized by topic
5. **See Also** - Links to related documentation

---

## Writing Style

### Tone

- **Professional but approachable** - Write like you're explaining to a colleague
- **Direct and concise** - Get to the point quickly
- **Action-oriented** - Use imperative mood for instructions

### Voice

- ✅ **DO:** "Use the `current_user` dependency to protect API routes"
- ❌ **DON'T:** "The `current_user` dependency can be used to protect API routes"

### Terminology

- **Consistent naming** - Use exact names from code
- **Define acronyms** - Spell out on first use (e.g., "HS code (Harmonized System code)")
- **Use project terms** - Follow established vocabulary (e.g., "extraction agent", "compliance stage", "Form M prep sheet")

### Examples

- ✅ **DO:** "Import the Pydantic models from `app.ai.schemas`"
- ❌ **DON'T:** "You might want to import from the schemas module"

---

## Code Examples

### Format

Always use code blocks with language tags. Backend examples are Python (`apps/api`); frontend examples are TypeScript (`apps/web`).

```python
# ✅ Good - Python backend example
from app.services.classification import ClassificationService
```

```bash
# ✅ Good - Shell command (backend uses uv)
uv run ruff check
```

### Best Practices

1. **Show both correct and incorrect:**
   ```python
   # ❌ Wrong - passes a raw dict across a pipeline boundary
   result = await classify(extraction.model_dump())

   # ✅ Correct - passes the validated Pydantic model
   result = await classify(extraction)
   ```

2. **Include context:**
   ```python
   # ✅ Good - Shows where this goes
   # app/api/routes/shipments.py
   @router.get("/shipments")
   async def list_shipments(user_id: str = Depends(current_user)):
       return await shipment_service.list(user_id=user_id)
   ```

3. **Use realistic examples:**
   ```python
   # ✅ Good - Realistic use case
   classification = await classification_agent.run(line_item)

   # ❌ Bad - Too abstract
   result = await agent.run(thing)
   ```

4. **Explain complex examples:**
   ```python
   # Create a shipment and kick off the agent pipeline.
   # Extraction → classification → compliance runs as a background task.
   shipment = await shipment_service.create(payload, user_id=user_id)
   background_tasks.add_task(run_pipeline, shipment.id)
   ```

---

## Formatting Standards

### Headings

- **H1 (#)** - Document title only
- **H2 (##)** - Major sections
- **H3 (###)** - Subsections
- **H4 (####)** - Sub-subsections (use sparingly)

### Lists

- Use bullet points for unordered lists
- Use numbered lists for step-by-step instructions
- Use checkboxes for checklists

### Emphasis

- **Bold** - For important terms, file names, or key concepts
- *Italic* - For emphasis or variable names
- `Code` - For code, file paths, or technical terms

### Code References

When referencing existing code, use the code reference format:

```12:14:apps/api/app/services/classification.py
class ClassificationService:
    ...
```

### File Paths

- Use backticks for file paths: `` `apps/api/app/services/classification.py` ``
- Use forward slashes: `` `apps/api/app/api/routes/shipments.py` ``
- Include file extension: `` `apps/api/app/core/logging.py` ``

---

## Cross-References

### Internal Links

Always link to related documentation:

```markdown
## See Also

- [Agent Pipeline](../docs/03-agent-pipeline.md)
- [Logging Patterns](../patterns/logging.md)
- [Validation Patterns](../patterns/validation.md)
```

### Link Format

- Use relative paths: `../patterns/logging.md`
- Use descriptive anchor text: `[Logging Patterns](../patterns/logging.md)`
- Link to specific sections when relevant: `[Validation Patterns](../patterns/validation.md#pydantic-model-patterns)`

### When to Link

- Link to related concepts
- Link to prerequisite knowledge
- Link to deeper dives
- Link to examples

---

## AI Discoverability

### Frontmatter (Optional)

For AI discoverability, add frontmatter:

```markdown
---
title: "Agent Pipeline"
description: "The four agents and their typed handoffs"
tags: ["architecture", "agents", "pipeline"]
---
```

### Keywords

Include relevant keywords naturally in content:
- Pipeline stage names (extraction, classification, compliance, Form M)
- Function and model names
- Pattern names
- Technology names (FastAPI, Pydantic AI, Claude, pgvector)

### Structure

- Use clear headings
- Include table of contents for long docs
- Use consistent terminology
- Add "See Also" sections

---

## Documentation Types

### Component READMEs

A README for a backend service or frontend feature should cover:

- Structure section
- Usage examples
- API / interface documentation
- Related components
- Architecture notes

### Guides

Step-by-step instructions:

1. **Introduction** - What you'll learn
2. **Prerequisites** - What you need
3. **Steps** - Numbered instructions
4. **Examples** - Code examples
5. **Troubleshooting** - Common issues
6. **See Also** - Related docs

### Architecture Docs

Conceptual documentation:

1. **Overview** - High-level explanation
2. **Concepts** - Key ideas
3. **Patterns** - Common patterns
4. **Examples** - Real-world examples
5. **Best Practices** - Do's and don'ts

### API Documentation

Reference documentation:

1. **Overview** - What the API does
2. **Methods** - All available methods
3. **Parameters** - Input parameters
4. **Returns** - Return values
5. **Examples** - Usage examples

---

## Common Patterns

### Pattern 1: Feature Documentation

```markdown
## [Feature Name]

[Brief description]

### Usage

```typescript
// Example code
```

### Configuration

[Configuration options]

### Examples

[More examples]
```

### Pattern 2: Troubleshooting

```markdown
## [Error Name]

**Symptoms:**
[What you see]

**Root Cause:**
[Why it happens]

**Solutions:**

1. [Solution 1]
2. [Solution 2]
```

### Pattern 3: Migration Guide

```markdown
# [Feature] Migration

**Status:** ✅ Complete / 🟡 In Progress  
**Date:** [Date]  
**Description:** [What changed]

## Changes Made

[What changed]

## Breaking Changes

[Any breaking changes]

## Migration Steps

1. [Step 1]
2. [Step 2]
```

---

## Best Practices

### ✅ DO

1. **Keep it updated** - Update docs when code changes
2. **Use examples** - Show, don't just tell
3. **Link related docs** - Help readers discover more
4. **Be consistent** - Follow established patterns
5. **Test examples** - Ensure code examples work
6. **Use clear headings** - Help with navigation
7. **Include context** - Explain why, not just how

### ❌ DON'T

1. **Don't duplicate** - Link instead of copying
2. **Don't be vague** - Be specific and clear
3. **Don't skip examples** - Code examples are essential
4. **Don't use jargon** - Define terms on first use
5. **Don't forget links** - Help readers navigate
6. **Don't leave outdated info** - Remove or update old content
7. **Don't write novels** - Be concise

---

## Review Checklist

Before submitting documentation:

- [ ] Follows file structure standards
- [ ] Uses consistent terminology
- [ ] Includes code examples
- [ ] Links to related docs
- [ ] Has table of contents (if long)
- [ ] Code examples are tested
- [ ] No broken links
- [ ] Clear headings
- [ ] Accurate information
- [ ] Up-to-date with code

---

## See Also

- [Agent Pipeline](../docs/03-agent-pipeline.md)
- [Logging Patterns](../patterns/logging.md)
- [Validation Patterns](../patterns/validation.md)

