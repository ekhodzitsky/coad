# docs/archive

Pre-v2 COAD prose, kept for historical context. None of these files are
required reading. They describe the methodology and orchestration story
COAD told before it collapsed to a fifteen-rule standard.

| File                                          | What it was                                  |
| --------------------------------------------- | -------------------------------------------- |
| `SPEC.md.v0.7.7`                              | Full COAD methodology specification          |
| `PRINCIPLES.md.v0.7.7`                        | Ten design principles                        |
| `AGENT_FLOW.md.v0.7.7`                        | Agent entry/edit/prove/handoff flow          |
| `COAD_PROJECT_STANDARD.md.v0.7.7`             | Long-form project shape (replaced by STANDARD.md) |
| `ADOPTION.md.v0.7.7`                          | Five-phase adoption guide                    |
| `GETTING_STARTED.md.v0.7.7`                   | Long-form onboarding (replaced by AGENT_ONBOARDING.md + README) |
| `GLOSSARY.md.v0.7.7`                          | Terminology                                  |
| `COAD_PROFILE.json.v0.7.7`                    | Conformance profile manifest (Evidence)      |
| `TODO.md.v0.7.7`                              | Pre-v2 root TODO list                        |
| `contracts.v0.7.7/`                           | Per-contract-kind specifications             |
| `playbooks.v0.7.7/`                           | Repeatable orchestration flows               |
| `agent-decision-rules.md.v0.7.7`              | Agent decision heuristics                    |
| `agent-integration.md.v0.7.7`                 | Integration notes for agent runtimes         |
| `anti-patterns.md.v0.7.7`                    | What not to do                               |
| `artifact-export.md.v0.7.7`                   | Evidence export bundle                       |
| `attestation-bundle.md.v0.7.7`                | Evidence attestation                         |
| `conformance-profile.md.v0.7.7`               | Conformance profile spec                     |
| `context-packs.md.v0.7.7`                     | Bounded context packing                      |
| `contract-graph.md.v0.7.7`                    | Cross-contract graph (Evidence)              |
| `execution-ledger.md.v0.7.7`                  | Execution ledger format (Evidence)           |
| `maturity-model.md.v0.7.7`                    | Five-level maturity model                    |
| `normative-language.md.v0.7.7`                | RFC 2119 MUST/SHOULD use                     |
| `orchestration-model.md.v0.7.7`               | Orchestration model (Evidence)               |
| `policy-enforcement.md.v0.7.7`                | Goal-policy enforcement (Evidence)           |
| `proof-matrix.md.v0.7.7`                      | Proof matrix (Evidence)                      |
| `release-gates.md.v0.7.7`                     | Release gate manifest                        |
| `report-versioning.md.v0.7.7`                 | Report versioning                            |
| `tool-output-schemas.md.v0.7.7`               | Tool output schemas                          |
| `workcells.md.v0.7.7`                         | Long-form workcell model                     |

The standard is now in [STANDARD.md](../../STANDARD.md). The orchestration
story (task contracts, execution ledgers, proof artifacts) lives in the
optional `schema/extensions/` schemas plus the
`coad_validator.extensions.evidence` namespace.
