# Commit 01 Design Note

## Goal

Establish one stable local quality baseline for linting, testing, and type checking without changing runtime behavior.

## Decisions

- Keep tool configuration centralized in `pyproject.toml`.
- Route `Makefile` commands through `python -m ...` instead of console entrypoints so local execution does not depend on potentially stale virtualenv shims.
- Scope `mypy` to the existing core modules that already have stricter typing expectations, matching the roadmap acceptance criteria.

## Result

Developers can run `make lint`, `make test`, and `make typecheck` against the same baseline used by CI, and the repository now has a regression test that checks those quality entrypoints remain declared.
