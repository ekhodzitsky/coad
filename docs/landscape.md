# COAD Landscape

COAD is a lightweight methodology for agent-navigable codebases.

It is not an agent runtime, IDE extension, autonomous orchestrator, or
full-stack agile process. COAD defines how a repository exposes boundaries,
ownership, invariants, proof, and safe write scope so any agent can work inside
it with less global context and fewer guesses.

## Positioning

COAD's category is:

```text
Agent-Navigable Codebase Standard
```

The core promise:

```text
COAD does not run agents. COAD makes a codebase understandable to agents.
```

The public integration surface stays intentionally small:

```bash
coad check .
```

## Adjacent Projects

| Project | What it optimizes | Relationship to COAD |
| --- | --- | --- |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | Spec-driven development workflow. | Strong neighbor. COAD should integrate with spec-first work, but focus on repository shape and module contracts. |
| [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) | AI-driven agile lifecycle with roles, workflows, PRDs, architecture, stories, and reviews. | Strong process competitor. COAD should stay lighter and repo-native. |
| [Superpowers](https://github.com/obra/superpowers) | Skills-based development methodology for coding agents. | Complementary workflow layer. COAD can be the project substrate those skills operate on. |
| [GSD / Get Shit Done](https://github.com/gsd-build/get-shit-done) | Meta-prompting, context engineering, and spec-driven development. | Similar goal of reliable AI development; COAD should differentiate through module-level contracts and validation. |
| [Agent OS](https://github.com/buildermethods/agent-os) | Project standards and specs for agentic development. | Close neighbor. COAD's sharper wedge is module-as-agent-workspace plus one validator command. |
| [Repomix](https://github.com/yamadashy/repomix) | Pack a repository into AI-friendly context. | Complementary, but philosophically different: COAD reduces the need to dump the whole repo by making local context reliable. |
| [OpenHands](https://github.com/OpenHands/OpenHands) | AI-driven development agent platform. | Agent runtime. COAD is the repository standard an OpenHands-style agent could follow. |
| [Cline](https://github.com/cline/cline) | Autonomous coding agent for IDE, CLI, and SDK use. | Agent runtime. COAD gives the agent better repo-local contracts. |
| [Roo Code](https://github.com/RooCodeInc/Roo-Code) | Multi-agent coding environment in the editor. | Runtime and orchestration surface. COAD gives shared module boundaries and proof expectations. |
| [Aider](https://github.com/Aider-AI/aider) | Terminal AI pair programming. | Pairing tool. COAD improves the repository context available to the pair programmer. |

## What COAD Should Not Become

COAD should not compete by adding a heavier agent runtime. That market already
has strong tools.

Avoid:

- custom agent launchers as the primary product;
- mandatory multi-phase project management ceremony;
- large prompt packs that only work in one AI tool;
- speculative automation before the repository contract is clear;
- broad CLI surfaces that make adoption harder than `coad check .`.

## What COAD Should Own

COAD should own the repo shape that makes agentic development safer:

- every important module has a readable local contract;
- surfaces name their consumers, promises, and proof;
- invariants are explicit before agents edit implementation details;
- write scope and forbidden mutations are visible before work starts;
- verification is attached to the module and task, not remembered in chat;
- handoffs carry evidence instead of vague summaries;
- `coad check .` verifies that the project is following the methodology.

## Differentiation

Spec-first systems ask agents to build from a plan.

Agent runtimes ask agents to act in an environment.

Context packers ask agents to read more of the repository.

COAD asks the repository to become navigable: each module should explain itself
well enough that an agent can safely enter, edit, prove, and hand off work
without reconstructing the whole system from scratch.
