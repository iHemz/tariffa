---
name: prompt-engineer
description: Reference guide for Claude prompt engineering techniques — CoT, few-shot, XML tags, chaining, and structured output.
---

# Prompt Engineering Techniques — Detailed Reference

## Table of Contents
1. Be Clear and Direct
2. Use XML Tags
3. Chain of Thought (CoT)
4. Few-Shot Examples
5. System Prompts and Roles
6. Prefilling Responses (API)
7. Prompt Chaining
8. Long Context Strategies
9. Extended Thinking
10. Structured Output
11. Temperature and Sampling
12. Prompt Templates and Variables

---

## 1. Be Clear and Direct

The single most impactful technique. Claude follows explicit instructions precisely.

### Principles
- State exactly what you want — don't hint or imply
- If you want thoroughness, say "Be thorough and comprehensive"
- If you want brevity, say "Respond in under 50 words"
- Provide motivation: explain WHY you want something, not just WHAT

### Bad vs Good

**Bad:** "Can you help with this code?"

**Good:** "Review this Python function for bugs, performance issues, and readability. For each issue found, explain the problem, show the fix, and rate severity as high/medium/low."

**Bad:** "Summarize this article."

**Good:** "Summarize this article in exactly 3 bullet points, each under 20 words, focusing on the business implications for SaaS companies."

---

## 2. Use XML Tags

XML tags help Claude parse complex prompts with multiple sections, separate context from instructions, and structure output.

### When to Use
- Separating different types of input (documents, data, instructions)
- Defining output structure
- Marking examples
- Wrapping context that should be referenced but not confused with instructions

### Pattern

```xml
<instructions>
Analyze the customer feedback below and categorize each piece as positive, negative, or neutral.
</instructions>

<feedback>
{{CUSTOMER_FEEDBACK}}
</feedback>

<output_format>
Return a JSON array where each item has "text", "sentiment", and "confidence" fields.
</output_format>
```

### Tips
- Use descriptive tag names that explain the content
- Be consistent with tag naming across your prompt
- Nest tags for hierarchical structure
- Claude 4.x models are excellent at respecting XML boundaries

---

## 3. Chain of Thought (CoT)

Asking Claude to reason step-by-step before producing a final answer dramatically improves accuracy on complex tasks.

### When to Use
- Math and logic problems
- Multi-step analysis
- Classification with nuanced criteria
- Any task where "showing work" would help a human get the right answer

### Patterns

**Simple CoT:**
```
Solve this problem step by step, then give your final answer.
```

**Structured CoT with tags:**
```
Reason through this problem step by step in <reasoning> tags, then provide your final answer in <answer> tags.
```

**For Claude 4.x with Extended Thinking:**
Extended thinking is built in — Claude will automatically reason through complex problems when thinking is enabled. You can guide initial thinking:

```
Think carefully about the edge cases before implementing this function.
Consider: What happens with empty input? Null values? Unicode characters?
```

### Important for Opus 4.5 (non-extended-thinking)
Avoid the word "think" — it can cause issues. Use alternatives:
- "Reason through this step by step"
- "Consider each factor carefully"
- "Evaluate the options before deciding"
- "Work through the logic before answering"

---

## 4. Few-Shot Examples

Providing examples is one of the most powerful techniques for controlling output format, style, and behavior.

### Rules for Claude 4.x
1. **Start with 1 example (one-shot).** Add more only if output doesn't match.
2. **Examples are followed very precisely.** Ensure they model exactly what you want.
3. **Include edge cases** in your examples to show how to handle them.
4. **Bad examples produce bad outputs.** Review examples carefully.

### Pattern

```
I want you to extract action items from meeting notes.

<example>
<input>
Meeting: Q4 Planning
John said he'd have the budget ready by Friday.
Sarah will reach out to the design team about the new mockups.
We agreed to revisit the timeline next week.
</input>
<output>
- [ ] John: Prepare Q4 budget (due: Friday)
- [ ] Sarah: Contact design team re: new mockups
- [ ] Team: Revisit project timeline (next week)
</output>
</example>

Now extract action items from these meeting notes:
<input>
{{MEETING_NOTES}}
</input>
```

### Anti-patterns to Avoid
- Examples that are sloppy or inconsistent with each other
- Examples that show behavior you don't want (Claude will replicate it)
- Too many examples that overwhelm the actual task
- Examples with different formatting than what you specified in instructions

---

## 5. System Prompts and Roles

System prompts set persistent behavior for the entire conversation.

### Best Practices
- Keep system prompts focused and not overloaded
- Use for: persona, tone, constraints, default output format, safety rules
- Put the most important instructions first
- Structure with clear sections

### Template

```
You are [ROLE] with expertise in [DOMAIN].

## Communication Style
- [tone and style guidelines]

## Constraints
- [what NOT to do]
- [boundaries]

## Output Defaults
- [default format unless otherwise specified]

## Uncertainty Handling
- If unsure, say so explicitly. Do not guess or fabricate.
```

### Role Assignment Tips
- Be specific: "senior backend engineer with 10 years of Python experience" beats "programmer"
- Include domain expertise: "specializing in HIPAA-compliant healthcare systems"
- Define the audience: "explaining concepts to a non-technical product manager"

---

## 6. Prefilling Responses (API Only)

Start the assistant's response to guide the output format or direction.

### Pattern
```json
{
  "role": "assistant",
  "content": "{\"analysis\": {\""
}
```

This forces Claude to continue in JSON format starting with the analysis key.

### Use Cases
- Force JSON output by starting with `{`
- Force a specific language or format
- Skip preamble: prefill with the answer structure
- Continue a partially written response

---

## 7. Prompt Chaining

Break complex tasks into sequential subtasks, where each step's output feeds the next step's input.

### When to Use
- Tasks with 3+ distinct phases
- When accuracy at each step matters more than speed
- When you need to validate intermediate results
- Complex research -> analysis -> synthesis workflows

### Design Principles
1. Each step should be a standalone, clear prompt
2. Define the interface between steps (output format of N = input format of N+1)
3. Include validation: check step N's output before feeding to step N+1
4. Keep each step focused on one thing

### Example Chain

**Step 1: Extract** -> "Extract all dates and events from this document. Return as JSON array."
**Step 2: Categorize** -> "Given these events: {{STEP_1_OUTPUT}}, categorize each as 'milestone', 'deadline', or 'meeting'."
**Step 3: Synthesize** -> "Given these categorized events: {{STEP_2_OUTPUT}}, create a project timeline summary."

---

## 8. Long Context Strategies

For prompts with large amounts of context (documents, codebases, data).

### Key Principles
- **Put instructions at the top AND bottom** of the prompt
- Use XML tags to clearly section different documents/data
- Tell Claude which parts are most important
- For very large contexts, summarize or highlight key sections
- Claude 4.5 models have excellent recall across their full context window

### Pattern
```xml
<instructions>
[Your main instructions here -- Claude reads these first]
</instructions>

<document_1>
[Large document content]
</document_1>

<document_2>
[Another large document]
</document_2>

<reminder>
[Repeat the most critical instructions here -- Claude reads these last]
Remember: Focus on [key priority]. Output format: [format].
</reminder>
```

---

## 9. Extended Thinking

Claude's extended thinking capability enables deep reasoning for complex tasks.

### When to Enable
- Complex mathematical proofs
- Multi-step logical reasoning
- Code architecture decisions
- Nuanced analysis requiring weighing many factors

### How to Guide Thinking
You can guide Claude's initial thinking to set direction:

```
Before answering, carefully consider:
1. What are the edge cases?
2. What assumptions am I making?
3. What would a skeptic argue?
Then provide your analysis.
```

### Interleaved Thinking
For tool-use workflows, Claude can reason between tool calls — reflecting on results before deciding the next action.

---

## 10. Structured Output

Getting Claude to return data in a specific, parseable format.

### Techniques
1. **JSON Schema** — Provide the exact schema you expect
2. **Prefilling** — Start the response with `{` (API only)
3. **Examples** — Show a complete example of the desired output
4. **Explicit instruction** — "Return ONLY valid JSON, no markdown, no explanation"

### Reliability Tips
- Combine schema definition + example + explicit instruction for highest reliability
- For API use, enable structured output mode if available
- Always include what NOT to include: "Do not wrap in markdown code fences"
- Test with edge cases (empty input, unexpected data)

---

## 11. Temperature and Sampling

### Guidelines
- **Temperature 0**: Deterministic, best for factual tasks, classification, extraction
- **Temperature 0.3-0.7**: Balanced creativity and consistency; good default for most tasks
- **Temperature 0.8-1.0**: More creative, varied output; good for brainstorming, creative writing
- **Top-p and top-k**: Usually leave at defaults unless you have specific needs

---

## 12. Prompt Templates and Variables

For production prompts, use variables/placeholders for dynamic content.

### Pattern
```
Analyze the following {{DOCUMENT_TYPE}} from {{COMPANY_NAME}}.

<document>
{{DOCUMENT_CONTENT}}
</document>

Focus on: {{ANALYSIS_FOCUS}}
Output format: {{OUTPUT_FORMAT}}
```

### Best Practices
- Use consistent variable naming (UPPER_SNAKE_CASE is clear)
- Document what each variable expects
- Set defaults for optional variables
- Validate variable content before injection (prevent prompt injection)
