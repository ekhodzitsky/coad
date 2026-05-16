# Release Gates

`schema/release-manifest.json` is the machine-readable release checklist for
this repository. It names the checks that must remain wired into CI before a
change can be treated as releasable.

The manifest is intentionally separate from `.github/workflows/ci.yml`:

- CI executes the gates.
- The manifest declares the expected gate names and commands.
- The internal drift report checks that the manifest and CI stay aligned.

## Manifest Contract

Each release gate includes:

- `id` - stable machine identifier.
- `name` - CI step name expected in the workflow.
- `command` - command expected in the workflow.
- `working_directory` - directory where the command runs.
- `required` - whether the gate blocks release.

`schema/release-manifest.schema.json` validates the manifest shape. The current
policy is that every listed gate is required.

The gate set is deliberately small: validator tests, the public
`coad check .` command, and JSON schema syntax validation.

## Drift Contract

The internal drift report fails when a required release gate is missing from CI.
This gives the repository a stable way to detect release-readiness drift without
parsing GitHub Actions semantics in every test.

To verify locally:

```bash
cd tools/coad-validator
uv run --locked pytest tests/test_drift.py
```
