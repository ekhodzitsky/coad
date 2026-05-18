# COAD Validator

Reference validator for COAD contract files.

Current released package version: `0.7.0`.

## Usage

```bash
uv run coad check ../../examples/minimal --schema-dir ../../schema
uv run coad check ../../examples/minimal --schema-dir ../../schema --format json
```

`coad check` is the only public command. It prints one line in text mode and
returns a non-zero exit code when methodology compliance fails.

The validator checks root `AGENTS.md` onboarding guidance, Markdown YAML
frontmatter against JSON schemas, module `README.md`/`TODO.md` context,
semantic contract quality, workcell context budgets, optional `.coad/leases.yml`
write ownership, release metadata consistency when present, and contract graph
references. Invalid UTF-8 in project-controlled inputs is reported as a
validation issue instead of terminating the process. When execution contracts
are present, the same command also
evaluates readiness, proof evidence, scheduling, ledger evidence, goal policy
constraints, handoff diff honesty, task write-scope integrity, and proof result
integrity across handoffs and ledgers. Ledger entries must also point at
matching handoffs with the same task and changed files. Methodology file changes
must be declared in `HANDOFF.contract_updates` with non-empty reasons. Passing
ledger proof results must point at non-empty relative proof artifacts that stay
inside the checked root and match their declared SHA-256 digest plus byte size.
When a passing result omits digest metadata but the artifact exists, the
structured issue message includes the expected value to record.
JSON proof artifacts are also validated against the proof artifact schema, and
their command/status must match the ledger proof result.

Internal report builders remain available to this package's tests, but they are
not user-facing CLI commands.
The package bundles the COAD schemas, so installed usage does not require
`--schema-dir`.

JSON outputs are covered by report schemas in `../../schema/reports/`.

## Tests

```bash
uv run pytest
```
