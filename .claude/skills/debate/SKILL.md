---
name: debate
description: Multi-model debate orchestrator - Claude vs Codex analysis across 3 rounds with synthesis
argument-hint: "[topic or decision]"

---

# Debate Orchestrator: System Overview

This document outlines a structured framework for orchestrating multi-model debate analysis. The system coordinates two independent AI analysts—Claude and Codex—to examine topics from naturally different perspectives across three rounds.

## Core Architecture

The orchestrator operates as a **coordinator, not an analyst**. It delegates analysis to specialized agents while handling clarification, state management, and synthesis. The system explicitly prohibits the orchestrator from providing independent analysis or filtering agent responses.

## Seven-Phase Process

**Phase 1** establishes context by parsing the topic, creating output directories, and optionally exploring project files and the specs under `/docs/`. This gathers relevant architectural or code-related background.

**Phase 2** focuses on clarification through 2-4 targeted questions about the decision, constraints, success criteria, and user leanings. Results lock into a `brief.md` document.

**Phase 3** establishes the agent array: Claude and Codex operating as independent analysts without forced personas.

**Phases 4-5** execute three sequential rounds. Round 1 spawns agents in parallel to provide opening positions. Rounds 2-3 follow sequentially, with each agent receiving all previous responses for cross-examination and refinement.

**Phase 6** synthesizes findings by identifying consensus points, key disagreements, recommendations, and validation steps. The orchestrator performs this synthesis directly without spawning additional agents.

**Phase 7** assembles all artifacts into a final `debate.md` file and reports completion to the user.

## Key Mechanisms

The system includes fallback procedures: if Codex becomes unavailable, Claude-haiku replaces it as Analyst B. All agent responses append directly to `state.md` without filtering. State persistence across rounds enables meaningful cross-examination and evolution of positions.

The framework prioritizes structured output and explicit reasoning trails over speed or consensus-forcing.
