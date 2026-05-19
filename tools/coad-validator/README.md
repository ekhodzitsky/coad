# COAD Validator

Reference validator for COAD contract files.

Current released package version: `0.7.5`.

## Usage

```bash
uv run coad check ../../examples/minimal --schema-dir ../../schema
uv run coad check ../../examples/minimal --schema-dir ../../schema --format json
```

`coad check` is the only public command. It prints one line in text mode and
returns a non-zero exit code when required boundary or evidence checks fail.

The validator checks root `AGENTS.md` onboarding guidance, Markdown YAML
frontmatter against JSON schemas, module `README.md`/`TODO.md` context,
semantic contract quality, workcell context budgets, optional `.coad/leases.yml`
write ownership, release metadata consistency when present, and contract graph
references. Invalid UTF-8 in project-controlled inputs is reported as a
validation issue instead of terminating the process. When execution contracts
are present, the same command also evaluates readiness, proof evidence,
scheduling, ledger evidence, goal policy
constraints, handoff diff honesty, task write-scope integrity, and proof result
integrity across handoffs and ledgers. Ledger entries must also point at
matching handoffs with the same task and changed files. Methodology file changes
must be declared in `HANDOFF.contract_updates` with non-empty reasons. Passing
ledger proof results must point at non-empty relative proof artifacts that stay
inside the checked root and match their declared SHA-256 digest plus byte size.
When a passing result omits digest metadata but the artifact exists, the
structured issue message includes the expected value to record.
JSON proof artifacts are also validated against the proof artifact schema, and
their command/status must match the ledger proof result. The validator also
checks JSON artifact exit-code, timestamp, cwd, tool, and output-path
provenance. When a JSON artifact declares `output_path`, that linked output
must be non-empty and match declared `output_sha256` plus `output_bytes`
metadata. The check also emits a required `methodology-loop` report that
summarizes orient, scope, execute, prove, update-knowledge, and handoff phases
without adding public CLI flags. That report is explicit about its boundary:
it checks workflow evidence, not agent intent, and each phase includes source
reports, blocking issues, and a recommended repair.

Internal report builders remain available to this package's tests, but they are
not user-facing CLI commands.
The package bundles the COAD schemas, so installed usage does not require
`--schema-dir`.

JSON output is the agent-facing control plane. Agents should inspect
`agent_status`, apply typed `next_actions` by `action_code` and `target_field`,
and rerun `coad check --format json` until completion is unblocked. JSON
outputs are covered by report schemas in `../../schema/reports/`.
Humans normally adopt COAD through Markdown Core files. The JSON layer is for
agents and CI, not a hand-authored project-management surface.

## Tests

```bash
uv run pytest
```
