# checkout demo before COAD

This repository has billing code and checkout code, but no COAD entrypoint.
An agent must infer ownership, consumers, and proof by reading source files or
chat history.

The hidden coupling is that checkout expects billing to return
`discount_cents`.
