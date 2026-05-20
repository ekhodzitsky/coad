# Changelog

## 0.9.4 - 2026-05-20

### Added

- SPEC §4 lifecycle now opens with a Mermaid flowchart showing the
  six phases plus the escalation exit. Visual entry point for humans;
  the prose table beneath is unchanged.
- SPEC §12 «Measuring adoption» — five qualitative signals a team
  can watch for to know whether COAD is actually getting used.
- SPEC §13 «Influences and acknowledgements» names the sources COAD
  synthesises: Domain-Driven Design (bounded contexts), Architecture
  Decision Records, GitHub CODEOWNERS, contract testing, AI-agent
  repo-instruction conventions.

### Changed

- `AGENTS.md` renamed to `CONTRIBUTING.md` to avoid collision with
  the industry convention (`AGENTS.md` is widely used for instructions
  to AI agents consuming the repository, not for contributors).
  `CONTRIBUTING.md` is now structured as a standard contribution guide:
  scope of welcome changes, scope requiring discussion, house rules,
  PR conventions.
- SPEC §1 vocabulary now states explicitly that «module» and «workcell»
  are synonyms for the basic case, and that the distinction only
  matters when one module contains sub-modules edited by different
  agents. The rest of the document uses «module» by default.

## 0.9.3 - 2026-05-20

### Added

- `LICENSE` (MIT). Repository can now be adopted in commercial
  projects.
- README §«Compared to adjacent practices» — one comparison table
  against Spec Kit, BMAD, Agent OS, Repomix, CODEOWNERS, ADR, and
  `.cursorrules` / `CLAUDE.md`. Answers «why COAD and not X?» in the
  first document a reader opens.
- SPEC §3 — full reference `MODULE_CONTRACT.md` (~30 lines, Markdown
  form) so AI agents see the target shape instead of imitating from
  a YAML stub.
- PRINCIPLES.md — each of the ten principles now ends with a
  `→ SPEC …` pointer that names the section where it is defined or
  worked through with an example.

### Changed

- README badge row now includes MIT license badge.
- README repository map lists `LICENSE`.

## 0.9.2 - 2026-05-20

### Changed

- Removed every remaining reference to a validator, CLI, or
  enforcement tool from the live documents. COAD is now described
  consistently as a written methodology.
- README rewritten with an AI-readable opening: explicit why-this-
  exists, who-this-is-for, who-this-is-not-for, and a two-track
  «how to use this repository» (human and AI agent). Badges updated to
  reflect that the project is prose, not software.

## 0.9.1 - 2026-05-20

### Added

- `SPEC.md` at the repository root. The methodology now has a body:
  vocabulary (module, workcell, surface, consumer, invariant, proof,
  dependency, drift, lease, handoff, read/write scope), the six-phase
  lifecycle, three worked examples, explicit when-to-use /
  when-not-to-use, integration with code review, CODEOWNERS, ADRs,
  design docs, and adjacent agent-development methods, a limitations
  section, and a five-step maturity ladder.
- `README.md`, `AGENT_ONBOARDING.md`, and `AGENTS.md` reference
  `SPEC.md` as the source of vocabulary.

## 0.9.0 - 2026-05-20

### Changed

- COAD became a written methodology. Everything that was not prose was
  removed from the working tree: Python validator, JSON schemas,
  examples, starter templates, self-dogfooding contracts, CI workflow,
  and the rule-based standard document.
- `PRINCIPLES.md` returned to the repository root as the methodology's
  canonical statement.
- README, AGENTS.md, and AGENT_ONBOARDING.md were rewritten around a
  single message: COAD is prose. Adoption means writing four files and
  using judgment.

Earlier drafts (rule-based standard, validator code, JSON schemas)
remain in git history at tags before `v0.9.0`.
