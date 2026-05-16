# Release Gates

`schema/release-manifest.json` is the machine-readable release checklist for
this repository. It names the checks that must remain wired into CI before a
change can be treated as releasable.

The manifest is intentionally separate from `.github/workflows/ci.yml`:

- CI executes the gates.
- The manifest declares the expected gate names and commands.
- `coad-drift` checks that the manifest and CI stay aligned.

## Manifest Contract

Each release gate includes:

- `id` - stable machine identifier.
- `name` - CI step name expected in the workflow.
- `command` - command expected in the workflow.
- `working_directory` - directory where the command runs.
- `required` - whether the gate blocks release.

`schema/release-manifest.schema.json` validates the manifest shape. The current
policy is that every listed gate is required.

The gate set includes the public `coad check` command plus the detailed
diagnostic reports that keep this repository's own toolchain honest.

## Drift Contract

`coad-drift` fails when a required release gate is missing from CI. This gives an
orchestration control plane a stable way to detect release-readiness drift
without parsing GitHub Actions semantics in detail.

To verify locally:

```bash
cd tools/coad-validator
uv run --locked coad-drift ../..
```
