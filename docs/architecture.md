# Architecture

## Package layout

```
src/innovation/
    model/       plain-data types: Card, PlayerState, GameState
    cards/       canonical Card definitions (the "card database")
    engine/      rules enforcement: actions and the turn loop
```

## Design principle: data model vs. rules engine

`innovation.model` only defines *shapes* -- `Card`, `PlayerState`,
`GameState`. Nothing in that package enforces a rule or mutates state
on its own. `innovation.engine` is the only package that should apply
rules and produce state transitions (e.g. `engine.actions.meld`
mutating a `GameState`).

This split exists so that:

- Card data (`innovation.cards`) can be authored/tested independently
  of rules logic.
- The rules engine can be tested against hand-built `GameState`
  fixtures without going through a full game setup.
- A future interface (CLI, web, etc.) only needs to depend on
  `innovation.engine` and `innovation.model`, not reimplement rules.

## Cards are data, dogma effects are code

A `Card` (see [card.py](../src/innovation/model/card.py)) is an
immutable definition: name, age, color, icons, and its dogma text.
Card *identity* and *printed text* belong in `innovation.cards`.
What a dogma effect actually *does* is executable behavior and belongs
in `innovation.engine` -- the two are being kept decoupled from the
start so that adding a card's rules text (data) and implementing what
it does (code) can be separate, individually testable steps. How that
executable behavior is represented (e.g. one function per card, a
small effect-description DSL) is not yet decided.

## Out of scope for now

No CLI, TUI, or other interface exists yet. The engine should be able
to play a complete game headlessly (i.e. be driven entirely by function
calls / a script) before an interface is built on top of it.
