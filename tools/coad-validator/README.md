# COAD Validator

Reference validator for COAD contract files.

## Usage

```bash
uv run coad-validate ../../examples/minimal --schema-dir ../../schema
```

The first version validates Markdown YAML frontmatter against JSON schemas and checks that the minimal contract graph references existing contracts.
