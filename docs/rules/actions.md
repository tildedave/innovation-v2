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

- Implemented for a single (non-shared, non-demanded) player
  (`engine/actions.dogma`): the named card must be the top card of one
  of the acting player's piles; each of its `Dogma.effect`s (see
  `innovation.model.card.DogmaEffect`) runs in order against the game
  state, for that player only. Raises `NotImplementedError` if a
  `Dogma` has no `effect` implemented yet (data entered, behavior not
  written -- see docs/rules/cards.md), and `ValueError` if the named
  card isn't on top of one of the player's piles.
- Each `Dogma` also carries an `icon` (the icon type it's printed
  under on the card), which determines share/demand eligibility.
- Share eligibility is implemented (`engine/sharing.eligible_to_share`):
  a non-active player is eligible to share a dogma effect when their
  count of the dogma's `icon` is >= the active player's count (ties
  are eligible; confirmed). This only answers "who *may* share" --
  `dogma` doesn't consult it yet, and sharing is optional per eligible
  player, so activating a dogma once sharing is wired in becomes a
  multi-step process (each eligible player decides in turn) rather
  than the single-player call it is today.
- TODO: demanding -- when the active player forces a non-eligible
  (i.e. fewer-icon) player to suffer part of the effect instead -- has
  no eligibility query yet, symmetric to `eligible_to_share` but with
  the comparison flipped.
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
