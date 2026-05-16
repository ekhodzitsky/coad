# COAD Validator

Reference validator for COAD contract files.

## Usage

```bash
uv run coad-validate ../../examples/minimal --schema-dir ../../schema
uv run coad-validate ../.. --schema-dir ../../schema --format json
```

The first version validates Markdown YAML frontmatter against JSON schemas and checks that the contract graph references existing contracts.

## Tests

```bash
uv run pytest
```
