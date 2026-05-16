# Project Contracts

These contracts apply COAD to this repository itself.

They are separate from `templates/` because templates are intentionally skipped
by repository-wide validation. Each file here describes a real project workcell.

Top-level files such as `docs.md` and `validator.md` may be composite
workcells. Focused child contracts use logical module identifiers plus
`workcell.context_path` so COAD can express smaller ownership units without
moving public files just to satisfy the methodology.
