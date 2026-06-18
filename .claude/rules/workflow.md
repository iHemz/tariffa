# Workflow Preferences

- Instead of fixing a bug right away, give me some options so I can choose before you fix them
- If you can find an opportunity to improve the output and reliability of the ask, then please suggest. Example: if I ask you to add a field, and you notice the existing fields have inconsistencies or potential bugs, flag them
- Before proposing a frontend solution, check `apps/web` lint/TS config; before a backend one, check `apps/api` ruff config — get the architecture right before writing code

## Git Commit Messages

- Commit messages describe **what changed and why** — never how it was built or what tools/processes were used
- Bad: `feat: added compliance agent through the orchestrate pipeline`
- Good: `feat(compliance): flag missing NAFDAC registration before Form M draft`
- Never mention AI agents, internal tooling, or process in commit messages
- Focus on the user-facing or developer-facing value of the change

## Git Branch Safety

- **NEVER commit directly to `main`**. All work goes on a feature branch and is merged via PR
- If the current branch is `main`, create a new branch first — no exceptions
