# Repository Guidelines

## General rules

- Every time you are told to do something do any actions required to collect all the needed
  information and then explain what changes will be done to achieve the results without editing a
  single file, and ask for approval to continue. Only edit the files after the user says "go".
- When given instructions, always stick strictly to the plan. Do not improve the proposal or the
  instructions unless being explicitly told to do so. In particular, never add any options or
  possibilities that were not included in the original request.
- If you detect missing options or possibilities while designing an attack plan, stop and mention
  them to the user, to let them decide whether they need to be covered or not. For example, if the
  user asks to implement a function and certain edge case is not covered, stop and ask whether the
  edge case should be covered and whether an argument should exist to control it instead of
  silently adding the argument and the optional flow branch.
- In just a few words: "Never attempt to outsmart the user"

## Clarify Unknowns (Do Not Guess)

- If any requirement depends on unknown details (e.g., UI labels/selectors, URLs, credentials,
  expected text, data setup, environment variables, or external service behavior), stop and ask for
  clarification before implementing.
- Do not add “best guess” or heuristic-based solutions (e.g., regex-based selector searches,
  fallback locators, broad try/catch loops) to bypass missing information. Prefer explicit,
  confirmed selectors and acceptance criteria.
- If the needed information is expected to exist in the repo, search/read the relevant files first,
  and then always ask for confirmation to corroborate the found information. Absolutely never
  proceed with an execution plan solely based on the information you collected on your own.

## Project Structure & Module Organization

- `blanket/__main__.py` is the current entry point for the linter.
- `docs/` captures technical references (`docs/CONVENTIONS.md`, `docs/TESTING.md`).
- `scripts/` holds developer utilities such as `scripts/lint.sh`.
- `pyproject.toml` defines packaging metadata and tool configuration.
- `Makefile` exposes install, lint, and test helpers.

## Build, Test, and Development Commands

- Install with `make install` (package install) or `make install-develop` (editable with dev
  extras).
- Quality gates: `make ruff` (lint), `make ruff-format` (format), `make lint` (both); tests via
  `make test` (pytest with coverage) or `make coverage` for an HTML report.

## Coding Style & Naming Conventions

- Python 3.11+, 4-space indent, max line length 99; follow `docs/CONVENTIONS.md`.
- Ruff enforces linting/formatting; relative imports are banned—use absolute package paths.
- Prefer clear snake_case for functions/vars, PascalCase for classes; keep docstrings meaningful
  and avoid stray whitespace.

## Testing Guidelines

- Follow `docs/TESTING.md` for how to write and run tests.
- Use pytest for unit/integration tests; place tests beside the code they cover or under `tests/`
  with `test_*.py` naming.
- Aim for coverage on new logic and error paths; keep tests deterministic and avoid external
  network calls when possible.

## Commit & Pull Request Guidelines

- Recent history favors short, descriptive titles (e.g., “Expose the query model as a parameter”);
  keep summaries under ~70 characters.
- Before opening a PR, run `make lint` and `make test`; include what changed, why, and how to
  verify (commands, data setup). Link issues/tasks and add screenshots for UI/report adjustments.
- Keep PRs scoped: backend model/migration changes should call out data impacts; note any new
  environment variables or scripts.
