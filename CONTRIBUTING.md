# Contributing to Digital Invoicing

This repository is intended to stay easy to review, safe to operate, and
straightforward to contribute to. Use this guide for code, docs, bug reports,
and release-facing changes.

## Before You Start

- Read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Read [SECURITY.md](SECURITY.md) before reporting any security issue
- Use [SUPPORT.md](SUPPORT.md) for usage questions and non-bug support requests

## Ways to Contribute

### Report Bugs

- Open a GitHub issue using the bug report template
- Include the DI version, Frappe version, ERPNext version, install method, and
  exact reproduction steps
- Include sanitized logs, stack traces, payload samples, or screenshots when
  they help reproduce the problem

### Propose Features

- Open a GitHub issue using the feature request template
- Describe the user problem first, then the proposed change
- Call out FBR or ERPNext workflow impact if the feature affects compliance or
  invoice submission

### Submit Pull Requests

1. Fork the repository.
2. Branch from `develop`.
3. Keep each pull request focused on one change area.
4. Add or update tests when behavior changes.
5. Run the required checks locally before opening the PR.
6. Fill out the pull request template completely.

## Local Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- MariaDB 10.6+
- Redis
- Frappe Bench

### Setup

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/kodlyft/di --branch develop
bench setup requirements
bench --site your-site install-app di

cd apps/di
pip install pre-commit
pre-commit install
```

## Required Checks

Run these before opening a pull request:

```bash
cd apps/di
pre-commit run --all-files
bench --site your-site run-tests --app di
```

If your change affects build assets or client-side behavior, also run:

```bash
bench build
```

## Tooling

| Tool | Purpose |
| --- | --- |
| `ruff` | Python linting and formatting |
| `eslint` | JavaScript linting |
| `prettier` | Markdown, YAML, and frontend formatting |
| `pre-commit` | Local automation wrapper for all configured checks |
| `pip-audit` | Dependency vulnerability scanning in CI |
| `CodeQL` | GitHub code scanning for Python and JavaScript |

## Coding Guidelines

### Python

- Follow the existing tab-indented style used by the repository
- Keep integration code deterministic and explicit around request payloads
- Prefer small functions with clear validation and error paths
- Use translatable user-facing messages where appropriate
- Avoid logging secrets, bearer tokens, NTN/CNIC values, or raw production
  payloads unnecessarily

### JavaScript

- Follow existing Frappe client-side patterns
- Keep UI actions thin and push business logic to the server where possible
- Use `__()` for translatable strings
- Avoid adding browser-only dependencies unless they are necessary

### Fixtures and Generated Files

- Do not reformat or rewrite generated JSON files unless the change is
  intentional
- Keep fixture updates tied to the code change that requires them

### Tests

- Add regression coverage for bug fixes when practical
- Prefer narrow tests around changed business rules over broad unrelated edits
- Include sandbox and production edge cases when the change affects FBR payloads

## Pull Request Expectations

- Explain the problem and the chosen fix
- Reference related issues using `Closes #123` when applicable
- Include screenshots or example payloads for UI or document-output changes
- Highlight migration, permissions, or compliance impact explicitly

## Release Notes

If your change should appear in release notes, describe the user-visible impact
clearly in the pull request. GitHub release notes are generated from tagged
releases.
