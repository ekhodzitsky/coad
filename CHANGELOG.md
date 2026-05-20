# Changelog

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
