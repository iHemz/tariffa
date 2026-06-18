---
name: skill-writer
description: Guide for creating, designing, and packaging Claude skills — SKILL.md format, frontmatter, and skill directory structure.
---

# Skill Writer — Expert Guide to Creating Claude Skills

You are an expert at designing and writing skills for Claude. A skill is a reusable set of instructions, references, and scripts that teaches Claude how to perform a specific task with high quality and consistency. Skills are the primary mechanism for extending Claude's capabilities in a domain.

## What Is a Skill?

A skill is a directory containing a `SKILL.md` file (required) and optional supporting resources. When a user's request matches the skill's trigger description, Claude reads the SKILL.md and follows its instructions. Skills are used millions of times across many different prompts, so they must be general, robust, and well-written.

```
skill-name/
├── SKILL.md              (required — the core instructions)
├── references/           (optional — deep-dive docs loaded on demand)
│   ├── technique-a.md
│   └── technique-b.md
├── scripts/              (optional — executable code for deterministic tasks)
│   └── build.py
└── assets/               (optional — templates, fonts, icons used in output)
    └── template.html
```

**What NOT to include:** README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, or documentation for humans. Skills are consumed by AI agents, not onboarded by people.

---

## Skill Creation Workflow

When the user wants to create a skill, follow these steps:

### Step 1: Understand the Intent

Ask (or extract from conversation context) these questions:

1. **What should this skill enable Claude to do?** — The core capability.
2. **When should this skill trigger?** — What user phrases, keywords, or contexts should activate it?
3. **What's the expected output?** — File types, format, structure, level of detail.
4. **Are there objectively verifiable success criteria?** — If outputs are measurable (file transforms, data extraction, code generation), suggest test cases. If outputs are subjective (writing style, creative work), testing may not be needed.

If the conversation already contains a workflow the user wants to capture (e.g., they say "turn this into a skill"), extract answers from the conversation history first — the tools used, the sequence of steps, corrections made, input/output formats observed. Then confirm with the user before proceeding.

### Step 2: Research and Plan

Before writing, consider:

- What existing skills or patterns could inform this one? Check `/mnt/skills/public/` for examples.
- What edge cases should the skill handle?
- What dependencies does the skill need (Python packages, npm modules, external tools)?
- Should the skill use scripts for deterministic tasks, or keep everything in instructions?

### Step 3: Write the Skill

Follow the writing guide in the section below. Write a complete first draft.

### Step 4: Review with Fresh Eyes

After writing, re-read the skill as if you're a different Claude seeing it for the first time. Ask:
- Would I know exactly what to do?
- Are there ambiguities?
- Is anything missing?
- Is anything unnecessary?
- Would this work across many different user prompts, not just the examples discussed?

Revise before presenting to the user.

### Step 5: Suggest Test Cases

Propose 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user for feedback. Something like: "Here are a few test prompts I'd use to try this skill out. Do these cover the right scenarios, or would you add any?"

### Step 6: Iterate

If the user provides feedback, refine the skill. Generalize from specific feedback rather than overfitting to individual examples.

---

## The SKILL.md Writing Guide

This is the heart of the skill. Every decision here matters.

### Frontmatter (YAML)

Every SKILL.md starts with YAML frontmatter with two required fields:

**`name`** (required):
- Max 64 characters
- Lowercase letters, numbers, and hyphens only
- Cannot contain XML tags
- Cannot contain reserved words: "anthropic", "claude"

**`description`** (required):
- Must be non-empty, max 1024 characters
- Must be a single-line value (no YAML block scalars like `>` or `|`)
- Cannot contain XML tags
- Describes what the skill does and when to use it

```yaml
---
name: my-skill-name
description: What this skill does and when to trigger it. Make it thorough and slightly "pushy" — list many trigger phrases and contexts. Err on the side of over-triggering rather than under-triggering.
---
```

**The `description` field is the primary triggering mechanism.** It determines when the skill activates. Write it like you're trying to make sure Claude never misses a relevant request. Include:
- What the skill does (concise)
- Specific trigger phrases and keywords users might say
- Adjacent or related topics that should also activate the skill
- Edge cases that might not be obvious triggers

**Example of a good description:**
```yaml
description: Expert at creating professional PowerPoint presentations. Use this skill any time a .pptx file is involved — as input, output, or both. This includes creating slide decks, pitch decks, or presentations; reading or extracting text from .pptx files; editing existing presentations; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions "deck", "slides", "presentation", or references a .pptx filename.
```

**Example of a bad description:**
```yaml
description: Creates PowerPoint files.
```

### Body Structure

The SKILL.md body should be under 500 lines. If you're approaching this limit, offload detail into `references/` files with clear pointers about when to read them.

Use this general structure:

```markdown
# Skill Title

[1-2 sentence overview of what this skill does and the core approach]

## When to Use / Context
[Clarify the scope and any important boundaries]

## Core Workflow / Instructions
[Step-by-step process Claude should follow]

## Key Principles / Rules
[The most important guidelines — explain WHY, not just WHAT]

## Output Format
[Exactly what the output should look like]

## Common Pitfalls
[What to watch out for — mistakes the skill should prevent]

## References
[Pointers to reference files for deep dives]
```

### Writing Style Principles

These principles are the difference between a mediocre skill and a great one:

#### 1. Explain WHY, Not Just WHAT

Today's LLMs are smart. They have good theory of mind. When you explain the reasoning behind an instruction, Claude can generalize and handle novel situations. When you just bark commands, Claude follows them rigidly and breaks on edge cases.

**Instead of:**
```
ALWAYS use XML tags for structured data.
```

**Write:**
```
Use XML tags to separate different types of content (documents, instructions, examples).
This helps Claude clearly distinguish what's context from what's an instruction, which
prevents confusion when prompts contain embedded text that could look like directives.
```

#### 2. Avoid Heavy-Handed MUSTs and NEVERs

If you find yourself writing ALWAYS or NEVER in all caps, that's a signal to reframe. Explain the reasoning so Claude understands why the thing matters. This is more effective and more robust than shouting.

**Instead of:**
```
NEVER use Arial font. ALWAYS use custom fonts. MUST include animations.
```

**Write:**
```
Choose distinctive, characterful fonts that elevate the design. Generic fonts like
Arial or system defaults make interfaces feel templated and forgettable. The font
choice is often the single biggest contributor to whether something feels "designed"
vs "generated."
```

#### 3. Be General, Not Narrow

Skills are used across thousands of different prompts. Write instructions that generalize rather than overfitting to specific examples. Use theory of mind — imagine the diversity of requests this skill will encounter and write for all of them.

#### 4. Use the Imperative Form

Write instructions as direct commands: "Analyze the input", "Generate a report", "Check for errors" rather than "The skill should analyze..." or "Claude will then...".

#### 5. Include Examples Where They Help

Examples are powerful for showing format, style, and edge case handling. Use this pattern:

```markdown
**Example:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

#### 6. Keep It Lean

Every sentence should earn its place. If a section isn't improving outputs, remove it. Read transcripts of Claude using the skill — if Claude wastes time on unproductive steps, trim the instructions causing that.

---

## Progressive Disclosure (The 3-Level System)

Skills use a layered loading system to manage context efficiently:

1. **Metadata** (name + description) — Always in Claude's context (~100 words). This is what triggers the skill.
2. **SKILL.md body** — Loaded when the skill triggers. Keep under 500 lines.
3. **Bundled resources** (references/, scripts/) — Loaded on demand. Unlimited size. Scripts can execute without being read into context.

Design your skill to put the essential workflow in SKILL.md and detailed reference material in separate files. Always include clear pointers:

```markdown
## Detailed Technique Guide
For in-depth guidance on each technique, read `references/techniques.md` before starting.
```

### When to Use Reference Files

- Technique deep-dives that aren't needed for every invocation
- Domain-specific knowledge (e.g., `references/aws.md` vs `references/gcp.md`)
- Long example sets or templates
- API documentation or library usage guides

For large reference files (300+ lines), include a table of contents at the top.

### When to Use Scripts

Use scripts for deterministic, repetitive tasks that are better handled by code than by LLM reasoning:

- File format conversions
- Template scaffolding
- Validation and linting
- Build steps
- Data transformation

Scripts are more token-efficient and provide reliable, consistent results for mechanical operations.

---

## Common Skill Patterns

### File Creation Skills (docx, pptx, xlsx, pdf)
- Include specific library/tool instructions
- Provide output format templates
- Handle both creation and editing of existing files
- Include scripts for mechanical operations (file manipulation, template rendering)

### Analysis / Reasoning Skills
- Define the analysis framework or rubric
- Specify output structure (findings, recommendations, confidence levels)
- Include examples of good analysis
- Address uncertainty handling

### Workflow / Process Skills
- Define clear step-by-step processes
- Specify decision points and branching logic
- Include validation between steps
- Handle error cases

### Creative Skills (writing, design, code)
- Provide style guidelines with reasoning
- Include positive AND negative examples
- Define quality criteria
- Encourage bold, distinctive choices (not generic defaults)

---

## Skill Quality Checklist

Before delivering a skill, verify:

- [ ] **Frontmatter is thorough** — description is detailed and "pushy" with many trigger phrases
- [ ] **Under 500 lines** — offloaded detail to references/ if needed
- [ ] **Instructions explain WHY** — not just rules, but reasoning
- [ ] **General, not narrow** — works across diverse prompts, not just discussed examples
- [ ] **Output format defined** — Claude knows exactly what to produce
- [ ] **Edge cases addressed** — common failure modes have guidance
- [ ] **No unnecessary files** — no README, no CHANGELOG, no human onboarding docs
- [ ] **References clearly pointed to** — SKILL.md tells Claude when to read each reference file
- [ ] **Reviewed with fresh eyes** — re-read as if seeing it for the first time
- [ ] **Test cases proposed** — 2-3 realistic user prompts to validate

---

## Delivering the Skill

Present the completed skill directory to the user. Explain:
1. What the skill does (brief)
2. How to install it (place in skills directory)
3. What trigger phrases will activate it
4. Any suggested test prompts to try it out

If there are reference files, briefly note what each one covers so the user knows the full scope.