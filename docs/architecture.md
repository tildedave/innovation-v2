# Architecture

## Package layout

```
src/innovation/
    model/       plain-data types: Card, PlayerState, GameState
    cards/       canonical Card definitions, including dogma effects
    engine/      rules enforcement: primitive actions and the turn loop
```

## Design principle: data model vs. rules engine

`innovation.model` only defines *shapes* -- `Card`, `PlayerState`,
`GameState` -- and every one of them is frozen (immutable). Nothing in
that package enforces a rule or produces a new state on its own. Every
*primitive* state transition (drawing, melding, tucking, splaying,
activating a card's dogma effects, ...) lives in `innovation.engine`
and works by returning a *new* state rather than mutating the one it's
given (e.g. `engine.actions.meld` takes a `GameState` and returns a
new one with the card moved, leaving the original untouched).

This split exists so that:

- The rules engine can be tested against hand-built `GameState`
  fixtures without going through a full game setup.
- A future interface (CLI, web, etc.) only needs to depend on
  `innovation.engine` and `innovation.model`, not reimplement rules.
- Immutable, copy-free state transitions are what future search
  algorithms (minimax, MCTS, etc.) need to branch and backtrack over
  possible games without deep-copying state or writing undo logic.

## Cards are data plus their dogma effects, colocated

A `Card` (see [card.py](../src/innovation/model/card.py)) is an
immutable definition: name, age, color, icons, and its `Dogma`s (each
carrying its rules text, its governing icon, and -- once implemented
-- an executable `effect`). A card's full definition, data and
behavior together, lives in one place in `innovation.cards.registry`
(e.g. `SAILING`'s dogma effect is `_sailing_dogma`, defined right next
to it), rather than being split across packages: a card and what it
does are one unit of work to add. Effects are *built from* primitives
in `innovation.engine.actions` (e.g. `draw_and_meld`) -- the primitive
state transitions themselves still only live in `innovation.engine`,
`innovation.cards` just composes them per card. Entering a card's data
and implementing its effect(s) can still be done as separate steps:
`Dogma.effect` is `None` until written (see docs/rules/cards.md).

## Out of scope for now

No CLI, TUI, or other interface exists yet. The engine should be able
to play a complete game headlessly (i.e. be driven entirely by function
calls / a script) before an interface is built on top of it.
