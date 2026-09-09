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

## GameState models "what's it waiting on," not just board state

`GameState` carries `current_player_index` (whose turn it is) and
`pending_steps` (see [pending.py](../src/innovation/model/pending.py)
and `innovation.engine.actions.dogma`/`answer_share`) -- the queue of
decisions/effects still needed to finish resolving something in
progress, e.g. asking each player eligible to share a dogma effect, in
turn, before the active player's own effect runs. This is deliberate:
a future UI (or any driver) should be able to render "whose turn is
it" and "what decision is pending" directly from `GameState` fields,
rather than needing to track that separately or replay history to
reconstruct it.

## Effects that "repeat" queue themselves, they don't loop

A dogma effect that repeats a step (e.g. Metalworking: "draw and
reveal a 1, if it has a Castle icon, score it and repeat this effect")
expresses that by appending a new `EffectStep` for itself onto
`pending_steps` and returning, rather than looping internally with a
`while`. `engine.actions._advance` drains the queue one step at a
time, so a Python loop inside an effect function would resolve the
whole chain invisibly in a single step; queuing instead keeps every
iteration ("drew a Castle card, scoring, drawing again") a distinct,
individually-processable entry in `GameState`, which is what a future
UI needs to render each step rather than just a before/after diff. See
`cards.registry._metalworking_dogma` for the pattern.

## Out of scope for now

No CLI, TUI, or other interface exists yet. The engine should be able
to play a complete game headlessly (i.e. be driven entirely by function
calls / a script) before an interface is built on top of it.
`current_player_index` is real state now, but nothing advances it
automatically -- the turn loop itself (whose turn is next, what ends a
turn) isn't designed yet.
