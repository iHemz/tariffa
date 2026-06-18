# Auto-Investigate for Complex Questions

When the user asks a question that requires deep codebase understanding, **automatically invoke `/investigate`** instead of attempting to answer directly. Do not ask if they want to investigate — just do it.

## Trigger Signals

Auto-invoke `/investigate` when the user's question matches ANY of these patterns:

1. **"What exactly happens when..."** — Tracing execution flow across the agent pipeline or multiple files
2. **"Why does X return/show/produce [unexpected result]"** — Debugging unexpected behavior (e.g. a misclassified HS code, a missed compliance flag)
3. **"How does [feature] work end-to-end"** — Understanding a full pipeline or flow (e.g. upload → extraction → classification → compliance → Form M draft)
4. **"What should happen when..."** — Understanding expected vs actual behavior
5. **Questions involving 3+ agents/layers** — Cross-cutting concerns that span `apps/web` and `apps/api`
6. **"Where does [data/state] come from"** — Data flow tracing across the thin client, the FastAPI layer, and Postgres
7. **Debugging questions with a screenshot** — User shows unexpected UI/data and asks why

## DO NOT auto-invoke when:

- The user asks a simple "where is X" question (use Grep/Glob directly)
- The user asks about a single file or function (just read it)
- The user gives a direct implementation instruction ("add field X to Y")
- The user explicitly says "quick question" or similar
- The question can be answered by reading 1-2 files

## How to invoke

Pass the user's question as the argument:

```
/investigate "[user's question verbatim]"
```

## Why

Complex codebase questions answered without systematic investigation often miss cross-module interactions, produce incomplete answers, and waste time with follow-up corrections. The investigate skill's multi-phase approach (context scan, codebase analysis, synthesis) produces reliable answers the first time.
