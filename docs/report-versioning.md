# Report Versioning

COAD report JSON is a machine contract between tools, orchestrators, and agents.
Every machine report MUST include:

```json
{
  "schema_version": 1
}
```

## Version 1 Policy

Version 1 reports are allowed to evolve only through backward-compatible
changes:

- adding optional fields;
- adding new enum values only when consumers are documented to tolerate them;
- adding new report types with their own schema files;
- tightening producer behavior when existing valid payloads remain valid.

Breaking changes require a new major report version:

- removing a field;
- renaming a field;
- changing a field type;
- changing status or relation semantics;
- making an optional field required for existing report types.

## Compatibility Rules

Consumers SHOULD reject reports with unsupported `schema_version` values.

Producers MUST update the matching file in `schema/reports/` and the test suite
in the same change that modifies a report payload.

The internal drift report exists to catch local repository drift around the
public command, report schemas, docs, and CI. It does not replace schema
compatibility review.
