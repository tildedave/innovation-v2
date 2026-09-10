# Rules overview

**Status: skeleton.** This is a section outline to fill in from the
official 4th-edition rulebook, not a substitute for it -- exact
wording matters for a rules engine, so treat every line below as a
`TODO` unless noted otherwise. Don't transcribe the rulebook text
verbatim into this repo; paraphrase into whatever precision the engine
implementation actually needs.

## Overview (high level, non-authoritative)

Innovation is a card game for 2+ players about advancing a set of
technologies/ideas through ten "ages," represented by ten decks of
cards. Each player builds their own tableau by melding cards in front
of them, organized into color-coded piles. Cards' printed icons and
"dogma" effects interact with what's in a player's tableau (and
sometimes other players' tableaus) to let players draw more cards,
manipulate piles, or score points. See [glossary.md](glossary.md) for
the vocabulary used throughout these docs.

## Setup

- Implemented (`engine/setup.start_game`): every player draws two
  age-1 cards, then each (in player order) chooses one of the two to
  meld -- modeled as a `ChoiceStep` per player, same decision
  machinery as an in-turn mandatory choice (see
  [actions.md](actions.md)), so it's resolved via
  `engine.actions.answer_choice` rather than a separate code path.
  Once every player's opening meld is resolved, whoever melded the
  lexicographically-first card by name (ties go to the lower player
  index) becomes `GameState.current_player_index`.
- TODO: Number of players supported, and any per-player-count
  variants.
- TODO: Initial deck/supply arrangement (ages 1-10) -- `start_game`
  consumes whatever `GameState.supply` already holds, it doesn't build
  it.
- TODO: Starting achievements pool -- not modeled yet (see
  docs/architecture.md).

## Turn structure

- Implemented (`engine/game.py`): a turn is two actions, chosen freely
  from Draw, Meld, Dogma, and Achieve (repeats allowed) -- except the
  very first turn of the game, which is only one action
  (`GameState.first_turn_taken`; confirmed). `start_turn` grants the
  current player's action budget; `take_draw_action`,
  `take_meld_action`, and `take_dogma_action` each perform one action
  (via the matching `engine.actions` primitive) and consume one of it
  -- the choice of *which* action is entirely up to the caller, the
  turn loop doesn't pick for them. Once the budget hits zero,
  `current_player_index` advances to the next player, who needs
  `start_turn` called again before acting.
- `take_dogma_action` consumes the turn's action the moment the dogma
  is activated, even if its sharing decisions (see
  [actions.md](actions.md)) are still unresolved afterward -- resolving
  those is separate from which action was taken. No new action (by
  any player) can be taken while a decision from a previous one is
  still pending (`engine.actions.pending_decision`).
- `take_achieve_action` raises `NotImplementedError` -- Achieve itself
  isn't implemented yet (see `engine.actions.achieve`).
- The four actions: Draw, Meld, Achieve, Dogma -- see
  [actions.md](actions.md) for per-action detail to fill in.

## TODO: Winning the game

- The achievement-count win condition (how many achievements needed,
  does it vary with player count).
- Special achievements and how they're earned.
- Any other end-of-game trigger (e.g. running out of a needed age's
  supply).

## TODO: Edge cases and clarifications

Track rules-as-written ambiguities and their resolutions here as
they're discovered while implementing card dogma effects, with a
reference back to the card that raised the question.
