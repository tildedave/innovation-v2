An implementation of Asmadi Games Innovation based on fourth edition rules.

(The justification for this is to familiarize myself with LLM coding tools in a non-work context.)

## Status

Project skeleton only -- see [CLAUDE.md](CLAUDE.md) for how the project
is organized, [docs/architecture.md](docs/architecture.md) and
[docs/style_guide.md](docs/style_guide.md) for conventions, and
[docs/rules/](docs/rules/) for the game rules this engine implements
(currently outlines/TODOs, to be filled in from the rulebook).

## Development

Managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync              # install/update the dev environment
uv run pytest        # run tests
uv run ruff check .  # lint
uv run mypy           # type-check
```
