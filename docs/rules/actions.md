# Actions

**Status: skeleton.** Each section is a `TODO` to fill in from the
rulebook with enough precision to implement and test the matching
function in
[engine/actions.py](../../src/innovation/engine/actions.py).

## Draw

- Which age a player draws from (their current lowest available, vs.
  highest melded, etc.) and what happens when that age's supply is
  empty.

## Meld

- Mechanics of moving a card from hand to the front of its color pile
  on the player's board.
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

- Resolution order when a card has multiple effects.
- The share/demand distinction: when non-active players participate
  "for free" (share) vs. only if they meet an icon-count threshold
  (demand), and what the active player's icon count controls.
- The "I" rule for repeating an effect once per matching icon --
  confirm and state precisely once found in the rulebook.
- What "flow of the game" cards vs. combat/attack-style cards commonly
  do differently, if that distinction matters for how effects are
  implemented.

## Cross-cutting: per-card dogma effects

The rules above describe the *action* mechanics generic to all cards.
Each individual card's dogma effect is additional rules text that
needs its own entry -- track that in
[cards.md](cards.md) rather than here.
