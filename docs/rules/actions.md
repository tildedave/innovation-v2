# Actions

**Status: skeleton.** Each section is a `TODO` to fill in from the
rulebook with enough precision to implement and test the matching
function in
[engine/actions.py](../../src/innovation/engine/actions.py).

## Draw

- The primitive (`engine/actions.draw`) is implemented: draw a card
  into the player's hand, falling back to the next higher age if the
  requested age's pile is empty, up through age 10; raises
  `SupplyExhaustedError` if nothing is available at or above the
  requested age.
- `age` is optional. Passed explicitly, it's used as given (e.g.
  Sailing's "draw and meld a 1" passes `age=1`). Left unset, `age` is
  the player's own highest melded top-card age instead (same
  fallback from there) -- this is both the base turn's Draw action and
  the sharing bonus draw (`DrawHighestStep`, see "Sharing" below), which
  share this exact rule ("draw a card of your highest top-card age").
  Raises `ValueError` if the player has no melded cards to determine
  an age from -- shouldn't happen mid-game since the opening meld
  (`engine/setup.start_game`) guarantees at least one before any
  turn starts.
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
- Score (`engine/actions.score`) moves a named card from hand to the
  score pile instead of the board -- used by "score" dogma effects
  (e.g. Metalworking).
- Reveal (`engine/actions.reveal`) is a no-op on game state, contextual
  to a `Zone` (see [glossary.md](glossary.md)) -- used by "draw and
  reveal" dogma effects (e.g. Metalworking) so the act of showing a
  card to the table has an explicit call site, even though nothing
  currently tracks "the revealed card" in `GameState`.
- Return (`engine/actions.return_card`) moves a named card from hand
  to the *bottom* of its own age's supply pile (the end `draw` doesn't
  take from) -- not revealed. Used by "return" dogma effects (e.g.
  Agriculture). See "Optional actions within an effect" below for how
  a card decides *whether* to return one.
- Splaying: what it is, the four directions, and which icons become
  visible/countable as a result. (See [glossary.md](glossary.md).)
  Splay left (`engine/board.splay_left`) exposes the bottom-right icon
  of each covered card; splay right (`engine/board.splay_right`)
  exposes the top-left and bottom-left icons; splay up
  (`engine/board.splay_up`) exposes every icon except top-left. All
  three directions are implemented.

## Achieve

- Implemented (`engine/actions.achieve`): one card per age is set aside
  at game start as that age's achievement (`GameState.achievements_available`);
  each can be claimed by at most one player. To claim the achievement
  of a given age, a player spends one of their per-turn actions and
  must satisfy both:
  - A top card on one of their piles of age >= the achievement's age.
  - A score pile whose total value (`engine/actions.score_pile_value`
    -- the sum of its cards' ages) is >= 5 times the achievement's age.
  Raises `ValueError` if no achievement of that age is available, or if
  either condition isn't met.
- The claimed card moves from `achievements_available` to the player's
  `PlayerState.achievements`; it can't be claimed again by anyone else.

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
  `EffectStep`) and auto-runs any `EffectStep`s (or `DrawHighestStep`s)
  at the front (no decision needed) until it hits a step that needs
  one or empties the queue. `pending_decision(state)` returns whatever
  decision-requiring step is currently at the front (a `ShareStep` or
  `OptionalStep`; `None` if nothing's pending).
- Eligibility runs first, for every eligible player at once, before
  anyone's effect executes: `answer_share(state, share)` resolves a
  pending `ShareStep` by asking, not acting -- a `True` answer only
  queues that player's own copy of the effect (immediately before the
  active player's closing `EffectStep`, so it still lands in turn
  order), it doesn't run it yet (it raises if the pending step isn't a
  `ShareStep`). Only once every eligible player in the round has
  answered -- i.e. once the front of the queue is no longer a
  `ShareStep` for this effect -- does the queue fall through and
  actually run the queued effects, in turn order, followed by the
  active player's own. When nobody is eligible, the queue is just
  `[EffectStep]` and it all resolves inside the original `dogma` call,
  same as before sharing existed.
- Confirmed: if *any* player shares (the first "yes" for a given dogma
  activation, regardless of how many eventually share), the active
  player draws a bonus card of their own highest top-card age -- once
  per activation, not once per sharer. Implemented as a
  `DrawHighestStep` (see `innovation.model.pending`), queued by
  `answer_share` at the *end* of `pending_steps` the first time
  `share=True` is answered (a second "yes" finds one already queued
  and doesn't add another), and auto-run like an `EffectStep` once the
  queue reaches it.
- TODO: demanding -- when the active player forces a non-eligible
  (i.e. fewer-icon) player to suffer part of the effect instead -- has
  no eligibility query or step type yet, symmetric to
  `eligible_to_share`/`ShareStep` but with the comparison flipped.

### Optional actions within an effect

- The "you may X a card from your hand. If you do, Y. If you don't,
  Z." pattern (e.g. Agriculture: "you may return a card from your
  hand. If you do, draw and score a card of value one higher than the
  card you return") is a decision by the *active* player, not other
  players -- modeled similarly to sharing, via a queued step and an
  `answer_*` function, but kept as a separate step type
  (`OptionalStep`, see `innovation.model.pending`) rather than reusing
  `ShareStep`: sharing has its own ramifications (the bonus-draw rule
  above) that don't apply to an ordinary optional action.
- `OptionalStep` generalizes over *which* action is optional: its
  `action` field is any `CardAction` -- a function shaped like
  `engine.actions.meld`/`tuck`/`score`/`return_card`, i.e. `(state,
  player_index, card_name) -> (state, Card)` -- so a future "you may
  meld/tuck/score a card..." effect reuses this same step type with a
  different `action`, not a new one. Agriculture's is `return_card`.
  `if_done` runs afterward with the resulting card; `if_declined` runs
  instead if they decline (a no-op if `None` -- Agriculture has no "if
  you don't"). `answer_optional(state, card_name)` resolves it --
  `card_name=None` means decline, matching `answer_share`'s pattern of
  "raise if the pending step isn't this type."
- `OptionalStep.validate`, if set, is a `CardChoiceValidator` that
  `answer_optional` calls *before* `action` when a card is chosen --
  it can reject an otherwise-in-hand card that isn't legal for that
  specific decision (beyond "is it in hand," which `action` already
  checks), by raising `ValueError`. Not called on decline. Agriculture
  leaves it `None` since "any card in hand" is already a fully legal
  choice; it exists for a future card with a real constraint (e.g. "a
  card of a color you don't have").

### Mandatory choices within an effect

- Some effects aren't optional at all but still require the player to
  pick *which* card -- e.g. Domestication: "meld the lowest card in
  your hand. Draw a 1." (there may be a tie for lowest age, so it's a
  real choice, just a constrained one). This is `ChoiceStep`, not
  `OptionalStep`: reusing `OptionalStep` here by simply never answering
  `None` would leave a caller able to "decline" a decision the rules
  text doesn't allow declining, so there's no `if_declined` and no
  concept of skipping it at all.
- `ChoiceStep` shares `action`/`if_done`/`validate` with `OptionalStep`
  (same `CardAction`/`CardEffect`/`CardChoiceValidator` shapes), but
  `answer_choice(state, card_name)` takes `card_name: str` -- required,
  not `str | None` -- so there's no decline path in the type itself.
  Domestication's `validate` is `engine.actions.validate_lowest_in_hand`,
  a reusable check (not specific to Domestication) for "is this card
  (one of, if tied) the lowest-age card in the player's hand" -- other
  "lowest card in hand" effects should reuse it rather than
  reimplementing the comparison.
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
