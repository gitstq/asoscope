# Contributing to asoscope

Thanks for taking the time to contribute! asoscope is a small, focused
tool and keeping it **zero-dependency** and **cross-platform** is the
core design contract.

## Development setup

```bash
git clone https://github.com/gitstq/asoscope.git
cd asoscope
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

No runtime dependency is ever required. Python 3.8+ standard library only.

## Running tests

```bash
make test                 # or:
python3 -m unittest discover -s tests -v
```

Tests must pass **offline**: HTTP interaction is faked through captured
fixtures under `tests/fixtures/`. When adding a new endpoint, capture a
real (trimmed) response and add a fixture instead of hitting the network
in tests.

## Coding conventions

- Follow PEP 8; keep line length at 100.
- Every public function/class needs a docstring; complex branches need
  inline comments explaining *why*, not *what*.
- Never add a third-party runtime dependency without opening an issue
  first — the stdlib-only guarantee is a feature.
- Handle Windows / macOS / Linux path differences through the helpers in
  `asoscope/store.py` rather than hard-coding separators.
- All user-facing errors must go through the typed classes in
  `asoscope/errors.py` so CLI exit codes stay deterministic.

## Commit messages

Use the [Angular Conventional Commits](https://www.conventionalcommits.org/)
style:

- `feat: add new capability`
- `fix: correct a bug`
- `docs: documentation only`
- `refactor: internal change with no behavior change`
- `test: add or correct tests`
- `chore: tooling / packaging`

## Pull requests

1. Fork and create a branch named `feat/<short-topic>` or `fix/<topic>`.
2. Add tests for any behavior change; keep coverage of the new code.
3. Update `CHANGELOG.md` under an `Unreleased` heading.
4. Ensure the full suite passes on Python 3.8+ semantics (do not use
   syntax/stdlib features newer than 3.8).
5. Keep PRs focused: one logical change per pull request.

## Issues

Please include: command run, storefront country, Python version
(`python3 --version`), OS, expected vs actual output, and the full error
message. Feature requests should describe the use case first.

## Code of conduct

Be kind, technical, and respectful. Criticize ideas, never people.
