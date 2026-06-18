# Context Engineering for Long-Running AI Agents

> Expert summary synthesized from research by Google (ADK), Anthropic, Stanford/SambaNova (ACE), and Manus AI.
>
> Framed here for tariffa's document-processing pipeline — the agents that extract data from invoices and packing lists, classify HS codes and regulators, check compliance against retrieved regulatory text (RAG), and draft a Form M prep sheet. These principles matter most for the compliance stage, which must reason over retrieved regulatory passages without drowning the relevant rule in noise.

## The Core Problem

**The problem isn't that agents can't hold enough information—it's that every token competes for the model's attention.**

- Longer context windows often make things _worse_, not better
- Critical constraints from early steps get buried under noise from later steps
- The agent doesn't forget because it ran out of space—it forgets because **signal gets drowned by accumulation**
- Transformer attention complexity scales quadratically with context length

**Analogy**: Domain memory is the library; context is the desk. You can have a great library and still fail because your desk is overloaded.

---

## The Four-Layer Memory Model

| Layer               | Description                                                                                                                                                      | Analogy          | Persistence    |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------------- |
| **Working Context** | What's actually sent to the model on each call—instructions, identity, selected history, relevant tool outputs, memory hits. Should be **as small as possible**. | CPU Cache        | Per-call       |
| **Session**         | Structured event logs for the full trajectory—user messages, agent replies, tool calls, results, control signals. **Ground truth** for what happened.            | RAM              | Within session |
| **Memory**          | Searchable knowledge the agent queries on demand—domain memory + insights extracted during the session.                                                          | Disk             | Cross-session  |
| **Artifacts**       | Large objects stored by reference—codebases, PDFs, database results. Not tokenized into the window.                                                              | External Storage | Persistent     |

### Key Insight

Working context is **computed**, not accumulated. Every LLM call assembles a fresh projection against fuller state.

---

## The Nine Scaling Principles

### Principle 1: Context Is Computed, Not Accumulated

Every LLM call should be a freshly computed projection against durable state. The naive pattern—append everything into one giant prompt—collapses under "three-way pressure":

- Cost and latency scale with context length
- Signal degrades as information gets buried ("lost in the middle")
- Irrelevant content competes for attention

**Implementation**: Build fresh working context from the current agent's perspective while preserving factual history in the Session.

### Principle 2: Separate Storage from Presentation

Durable state and per-call views serve different purposes. They should evolve independently.

- Your session stores everything that happened
- Your working context is a computed subset optimized for the model's current decision
- The compilation layer transforms one into the other

**Implementation**: Store tool results in full externally; carry compact references in the context window.

### Principle 3: Scope by Default

Default context should contain **nearly nothing**. Additional information enters through explicit decisions—loading memory, requesting artifacts, querying past results.

This inverts the common pattern where everything gets included by default and you worry about trimming later.

**Rationale**: Every token competes for limited attention. Old information that's "nice to have" dilutes signal from new information that's actually relevant.

### Principle 4: Retrieval Over Pinning

Don't keep everything permanently in context. Even with million-token windows, performance degrades when you pin everything.

Treat memory as something the agent queries on demand, with relevance-ranked results. The working context should be the result of a search, not the accumulation of history.

**Benefit**: Agents differentiate between critical constraints from thirty steps ago and noise from three steps ago.

### Principle 5: Summarization Must Be Schema-Driven

Before you compress anything, **define what must survive**:

- Causal steps—the chain of decisions and why
- Active constraints—rules still in effect
- Failures—what was tried and didn't work
- Open questions—unresolved issues

**Failure modes** (from ACE paper):

- "Brevity bias"—summarization drops domain-specific insights for generic compression
- "Context collapse"—iterative rewriting erodes detail over time

**Test**: Can your summarized context make the same decisions as full context on known examples?

### Principle 6: Offload Heavy State to Tools and Sandboxes

Don't feed the model raw tool results at scale. Write them to disk and pass pointers.

**Manus approach**: Treat the file system as "unlimited context." The model writes to and reads from files on demand, using the file system as structured memory.

Compression becomes reversible—a web page's content can be dropped from context as long as the URL is preserved.

**Tool design**: Use fewer than 20 atomic tools (bash, file system operations, code execution). Let the sandbox handle complexity rather than bloating function-calling layer.

### Principle 7: Isolate Context with Sub-Agents

Multi-agent systems should manage context, not mimic org charts. Sub-agents exist to give different work its own window—not to roleplay human teams.

**Communication protocols**:

- Simple tasks: Pass instructions via function call, return structured result
- Complex tasks: Full file-based context sharing

**Output follows a schema**: Constrained decoding ensures adherence. No free-form responses.

**Test**: "What gets clearer or more correct with separate windows?" If you can't answer that, the split is probably wrong.

### Principle 8: Design for Cache Stability

KV-cache hit rate may be the single most important metric for production agents. It directly affects latency and cost.

With Claude Sonnet, cached tokens cost $0.30 per million versus $3.00 for uncached—**10x difference**.

**Requirements**:

- **Keep prompt prefixes stable**: Don't include timestamps at the beginning of system prompts
- **Make context append-only**: Don't modify previous actions or observations
- **Ensure deterministic serialization**: Many JSON libraries don't guarantee key ordering
- **Mark cache breakpoints explicitly**: Ensure breakpoints cover the system prompt

### Principle 9: Let Context Evolve Through Execution

Static prompts freeze agents at version one. The agent never learns from experience.

**ACE Framework** (Generator → Reflector → Curator):

1. **Generator**: Produces reasoning trajectories, surfacing strategies and pitfalls
2. **Reflector**: Critiques traces to extract lessons
3. **Curator**: Synthesizes lessons into context updates

**Results**: +10.6% on agent benchmarks, +8.6% on finance tasks, with 86.9% lower adaptation latency.

**Key**: Uses execution feedback rather than labeled data. No human annotation required.

---

## The Nine Failure Modes

### 1. The Append-Everything Trap

Keep a single growing transcript and hand it to the model every turn. Cost and latency scale linearly. Attention dilutes as stale events accumulate. Performance degrades predictably.

### 2. Blind Summarization

Compress "to save space" without defining what must survive. Agents forget edge cases, constraints, what was already tried. Becomes impossible to debug.

### 3. The Long-Context Delusion

Upgrade to a million-token model and assume the problem is solved. Performance gets worse. You're paying more for a more distracted model.

### 4. Observability as Context

Stick debug logs, raw tool output, stack traces into the same buffer as task instructions. Conflate what you need for debugging with what the model needs for decisions.

### 5. Tool Schema Bloat

Bind dozens of tools with detailed descriptions. Each description consumes attention budget. Overlapping tools create ambiguity.

### 6. Anthropomorphic Multi-Agent

Create Designer Agent, PM Agent, Engineer Agent because it feels like good division of labor. They share a giant context and "communicate" by appending messages. Result: accumulated noise without context isolation benefits.

### 7. Static Configurations

No accumulation of knowledge. No sharpening of heuristics. Rebuild from scratch every session. The agent running this morning doesn't inform the agent running this afternoon.

### 8. Over-Structured Harness

Build elaborate multi-step planners, strict tool hierarchies, complex routing logic. When you swap in a better model, performance barely changes. The harness is the bottleneck.

### 9. Cache Destruction

Rebuild prompts every turn with unstable prefixes. Timestamps, non-deterministic serialization, reorganized content. Pay full cost for identical logical content.

---

## What Becomes Possible

With proper context engineering:

- **Multi-hour autonomy**: Research tasks, code migrations, audit workflows that run for hours and touch hundreds of files
- **Self-improving agents**: Systems that log strategies, update heuristics, learn from mistakes without retraining
- **Scalable personalization**: Persistent preferences, learned constraints, prior outcomes—without ballooning context
- **Multi-agent coordination that works**: Planner/executor/validator collaborating through structured artifacts instead of shared context
- **Reasoning over large corpora**: Codebases treated as artifacts rather than tokenized wholesale
- **Auditable systems**: Full reconstructability of what the model saw and why — essential when a compliance flag has to be defensible to the user or their broker
- **Viable economics**: Sub-linear cost growth through cache reuse and intelligent compaction
- **Domain-specific workspaces**: A compliance agent with durable regulatory context (NAFDAC/SON rules retrieved on demand), an extraction agent with the current shipment's document set as artifacts

---

## Manus AI Production Lessons

After four complete architecture redesigns, Manus converged on these strategies:

| Strategy                     | Implementation                                                                    |
| ---------------------------- | --------------------------------------------------------------------------------- |
| **Design Around KV-Cache**   | Stable prompt prefixes, append-only context, explicit cache breakpoints           |
| **Mask, Don't Remove**       | Don't dynamically remove tools—mask them via token logits to preserve cache       |
| **File System as Context**   | Treat external storage as unlimited context; read/write on demand                 |
| **Attention via Recitation** | Agent updates a `todo.md` file, reciting goals at context end to maintain focus   |
| **Keep Wrong Stuff In**      | Leave failed actions in context—helps agent learn from errors                     |
| **Avoid Few-Shot Mimicry**   | Introduce controlled diversity in templates/formatting to prevent rigid imitation |

---

## The 12 Design Prompts

Use these prompts to design your own context architecture:

1. **State Persistence Analysis** — Classify what your agent must remember vs. discard
2. **View Compilation Design** — Define the minimal context needed for each decision
3. **Retrieval Trigger Design** — Solve the problem of memory that never gets used
4. **Attention Budget Allocation** — Justify every token in your context window
5. **Summarization Schema Design** — Specify what must survive compression
6. **External Memory Architecture** — Draw the line between recitation and storage
7. **Multi-Agent Scope Design** — Test whether agent splits add clarity or just complexity
8. **Cache Stability Optimization** — Audit for cost and latency at scale
9. **Failure Reflection System** — Design how agents learn from mistakes
10. **Architecture Ceiling Test** — Find where your harness limits model capability
11. **Context Observability Audit** — Build the tracing layer for production debugging
12. **The Non-Tech Prompt** — Make sense of all this if you're NOT an engineer

---

## Actionable Audit Checklist

- [ ] **Map against the four layers**: Where does working context end and session begin? What qualifies as memory versus artifact?
- [ ] **Measure your context window**: What percentage is actually relevant to the current decision?
- [ ] **Examine summarization**: Is it schema-driven or blind compression? Can you reconstruct decision-relevant structure?
- [ ] **Audit tool surface**: Could you achieve the same capability with fewer, more orthogonal tools? More than 20 likely means problems.
- [ ] **Check prefix stability**: What changes between calls? Is the system prompt truly stable?
- [ ] **Run the ceiling test**: If you swap in a more capable model, does your agent get proportionally better?
- [ ] **Design for feedback**: How do outcomes feed back into context refinement?

---

## Source Papers

1. **Google ADK**: [Architecting efficient context-aware multi-agent frameworks for production](https://developers.googleblog.com/)
   - Separates storage from presentation, uses explicit context transformations, scopes each agent call to minimum required context

2. **Manus Context Engineering**: [Context Engineering in Manus](https://www.marktechpost.com/2025/07/22/context-engineering-for-ai-agents-key-lessons-from-manus/)
   - Three strategies: reduce via compaction/summarization, isolate via sub-agents, offload to file system

3. **Stanford/SambaNova ACE**: [Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models](https://arxiv.org/abs/2512.16970)
   - Treats context as evolving playbooks, achieving +10.6% on agent benchmarks while reducing adaptation cost

4. **Anthropic**: [Effective context engineering for AI agents](https://www.anthropic.com/news/context-management)
   - Context is a tiny desk: optimize via compaction, structured note-taking, sub-agents, and just-in-time retrieval

---

## Key Takeaway

> **Domain memory gives agents continuity across sessions. Context engineering gives agents coherence within sessions. Both are necessary. Neither is sufficient alone.**

The organizations getting agents to work at scale have internalized both. They're not waiting for models to get smarter or context windows to get bigger. They're building the memory infrastructure that makes current models reliable.

---

_Source: [Nate's Substack - Get the Cheat Code on Long-Running AI Agents](https://natesnewsletter.substack.com/p/i-read-everything-google-anthropic) (Dec 2025)_
