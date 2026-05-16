# COAD Validator

Reference validator for COAD contract files.

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
references. When execution contracts are present, the same command also
evaluates readiness, proof evidence, scheduling, ledger evidence, and goal
policy constraints.

Internal report builders remain available to this package's tests, but they are
not user-facing CLI commands.
The package bundles the COAD schemas, so installed usage does not require
`--schema-dir`.

JSON outputs are covered by report schemas in `../../schema/reports/`.

## Tests

```bash
uv run pytest
```
