# innovation

A rules engine for Asmadi Games' *Innovation* (4th edition), in Python 3.

This file is the entry point for how the project is organized and how
to work in it. See also:

- [docs/architecture.md](docs/architecture.md) -- package layout and responsibilities
- [docs/style_guide.md](docs/style_guide.md) -- coding conventions
- [docs/rules/](docs/rules/) -- the game rules this engine implements

## Tooling

The project is managed with [uv](https://docs.astral.sh/uv/).

```bash
uv sync              # install/update the dev environment
uv run pytest        # run tests
uv run ruff check .  # lint
uv run ruff format .  # format
uv run mypy           # type-check
```

## Current status

Only the project skeleton exists so far: data model shapes, empty
action/engine stubs, and no card data. There is no gameplay yet. See
the `TODO` notes in each module and in `docs/rules/` for the intended
next steps.

## Scope

This is a rules engine first (see [docs/architecture.md](docs/architecture.md)).

A CLI or other interface is deliberately out of scope until the engine
can play a full game.
