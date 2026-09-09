# Actions

**Status: skeleton.** Each section is a `TODO` to fill in from the
rulebook with enough precision to implement and test the matching
function in
[engine/actions.py](../../src/innovation/engine/actions.py).

## Draw

- The primitive (`engine/actions.draw`) is implemented: draw a card of
  a given age, falling back to the next higher age if that pile is
  empty, up through age 10; raises `SupplyExhaustedError` if nothing
  is available at or above the requested age.
- TODO: which age the base turn "Draw" action passes in -- the player's
  current highest melded age, most likely -- isn't determined yet
  since it needs `meld`/board state.
- TODO: what actually happens when `SupplyExhaustedError` is raised
  (an end-of-game trigger per the rulebook) isn't handled yet; that
  belongs in the turn loop (`engine/game.py`), not in `draw` itself.
- `engine/actions.draw_and_meld` and `engine/actions.draw_and_tuck` are
  the "draw and meld"/"draw and tuck" variants used by many dogma
  effects: same age-fallback as `draw`, but the card goes straight
  onto the board (see Meld below) instead of the hand.

## Meld

- Implemented (`engine/actions.meld`): moves a named card from hand to
  the top of its own color's pile, creating the pile if needed. A
  pile's existing splay direction carries over unchanged when a new
  card is melded onto it (confirmed).
- Tuck (`engine/actions.tuck`) is the same, except the card goes to
  the *bottom* of its color's pile instead of the top -- used by
  "tuck" dogma effects rather than the base turn actions.
- Splaying: what it is, the four directions, and which icons become
  visible/countable as a result. (See [glossary.md](glossary.md).)
  Splay left (`engine/board.splay_left`) exposes the bottom-right icon
  of each covered card; splay right (`engine/board.splay_right`)
  exposes the top-left and bottom-left icons; splay up
  (`engine/board.splay_up`) exposes every icon except top-left. All
  three directions are implemented.

## Achieve

- Eligibility: score total required relative to the achievement's age,
  and whether a matching top-card icon count is also required.
- What happens to the claimed achievement card.

## Dogma

- Implemented (`engine/actions.dogma`): the named card must be the top
  card of one of the acting player's piles. For each of the card's
  `Dogma`s (see `innovation.model.card.DogmaEffect`), in order, this
  queues a `ShareStep` for every eligible player (see below), then an
  `EffectStep` that runs it for the active player -- see "Sharing" below
  for how that queue is resolved. Raises `NotImplementedError` if a
  `Dogma` has no `effect` implemented yet (data entered, behavior not
  written -- see docs/rules/cards.md), and `ValueError` if the named
  card isn't on top of one of the player's piles.
- Each `Dogma` also carries an `icon` (the icon type it's printed
  under on the card), which determines share/demand eligibility.

### Sharing

- Share eligibility is implemented (`engine/sharing.eligible_to_share`):
  a non-active player is eligible to share a dogma effect when their
  count of the dogma's `icon` is >= the active player's count (ties
  are eligible; confirmed). Returned in clockwise turn order starting
  from the player after the active one.
- Sharing is optional per eligible player, so activating a dogma with
  sharing involved is a multi-step process rather than a single call:
  `GameState.pending_steps` (see `innovation.model.pending`) is the
  queue of what's left to resolve. `dogma` builds it as
  `[ShareStep, ShareStep, ..., EffectStep]` (one `ShareStep` per
  eligible player in turn order, then the active player's own
  `EffectStep`) and auto-runs any `EffectStep`s at the front (no
  decision needed) until it hits a `ShareStep` or empties the queue.
  `pending_decision(state)` returns the `ShareStep` currently awaiting
  an answer (`None` if nothing's pending), and
  `answer_share(state, share)` resolves it -- running that player's
  copy of the effect first if `share` is `True` -- then advances the
  queue the same way. When nobody is eligible, the queue is just
  `[EffectStep]` and it all resolves inside the original `dogma` call,
  same as before sharing existed.
- TODO: demanding -- when the active player forces a non-eligible
  (i.e. fewer-icon) player to suffer part of the effect instead -- has
  no eligibility query or step type yet, symmetric to
  `eligible_to_share`/`ShareStep` but with the comparison flipped.
- TODO: The "I" rule for repeating an effect once per matching icon --
  confirm and state precisely once found in the rulebook. (Note:
  Sailing does *not* use this pattern -- its dogma is a flat "draw and
  meld a 1," not repeated per icon.)
- TODO: What "flow of the game" cards vs. combat/attack-style cards
  commonly do differently, if that distinction matters for how effects
  are implemented.

## Cross-cutting: per-card dogma effects

The rules above describe the *action* mechanics generic to all cards.
Each individual card's dogma effect is additional rules text that
needs its own entry -- track that in
[cards.md](cards.md) rather than here.
