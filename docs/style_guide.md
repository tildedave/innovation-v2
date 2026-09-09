# Code style guide

Formatting and linting are enforced by `ruff` and `mypy` (see
`pyproject.toml`); this document covers conventions those tools can't
check.

## Typing

- `mypy --strict` passes at all times. Every function has a full
  signature (including `-> None`); no bare `Any` without a comment
  explaining why it's unavoidable.
- Prefer `dataclass` for plain-data types. Every type in
  `innovation.model` is `frozen`, including in-progress game state
  (`PlayerState`, `GameState`) -- see [architecture.md](architecture.md)
  for why. Use tuples, not lists, for their collection fields; a `dict`
  field is fine but typed as `Mapping` so mypy flags accidental
  mutation through it. Engine functions that change state build and
  return a new instance with `dataclasses.replace`, they never mutate
  the one they're given.
- Use `from __future__ import annotations` in every module.

## Naming

- Modules and packages: `snake_case`, matching the concept they hold
  (`game_state.py`, not `state.py` or `gamestate.py`).
- Classes: `PascalCase`. Enums are `PascalCase` types with
  `UPPER_CASE` members.
- Functions/methods/variables: `snake_case`. Avoid abbreviations that
  aren't obvious from context (`player_index`, not `pidx`).

## Docstrings and comments

- Every module, public class, and public function gets a one-line (or
  short) docstring stating *what it is/does*, not *how*.
- Don't write a comment that just restates the code. Write one only
  when the *why* isn't obvious from the code itself -- e.g. a rules
  subtlety, or a deliberate simplification with a `TODO` pointing at
  what's missing.
- `TODO` comments should say what's missing and, where relevant, point
  at the doc (usually under `docs/rules/`) that describes the target
  behavior.

## Structure

- No abstraction for a single implementation. Don't introduce a base
  class, interface, or plugin mechanism until there are at least two
  concrete cases that need it.
- Keep `innovation.model` free of rules logic; see
  [architecture.md](architecture.md) for the model/engine split this
  is meant to preserve.

## Tests

- `pytest`, one test module per source module it exercises
  (`tests/test_card.py` for `src/innovation/model/card.py`), mirroring
  the package's directory structure under `tests/`.
- Test function names describe the behavior under test:
  `test_<unit>_<condition>_<expected outcome>` where that reads
  naturally, e.g. `test_meld_replaces_top_card_of_matching_color`.
- A card's dogma implementation should be tested against the exact
  rules-text scenario it's meant to satisfy (see `docs/rules/`), not
  just "runs without error."
