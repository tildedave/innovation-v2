"""The four player actions: Draw, Meld, Achieve, and Dogma.

Every action returns a new ``GameState`` rather than mutating the one
it's given (see ``innovation.model`` and ``innovation.engine`` for why).
Most also return the ``Card`` the action was about, since the caller
usually needs to know which card was drawn/melded/tucked and re-deriving
that from the new state alone would be more awkward than useful.

TODO: Implement Achieve against ``GameState``/``PlayerState``. See
docs/rules/actions.md for the rules each function must satisfy.
"""

from __future__ import annotations

from dataclasses import replace

from innovation.engine.sharing import eligible_to_share
from innovation.model.card import Card
from innovation.model.enums import Zone
from innovation.model.game_state import GameState
from innovation.model.pending import (
    ChoiceStep,
    DrawHighestStep,
    EffectStep,
    OptionalStep,
    PendingStep,
    ShareStep,
)
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


class SupplyExhaustedError(Exception):
    """No card is available to draw at or above the requested age.

    TODO: this is expected to trigger a special end-of-game condition
    once the turn loop (see docs/rules/overview.md) is designed --
    callers shouldn't silently swallow it.
    """


def draw(state: GameState, player_index: int, age: int | None = None) -> tuple[GameState, Card]:
    """The given player draws a card into their hand.

    ``age`` set explicitly draws a card of that age, falling back to
    the next higher age if that pile is empty (repeating through age
    10) -- used by dogma effects that name an age (e.g. Sailing's
    "draw and meld a 1"). Left unset, ``age`` is the player's own
    highest melded top-card age instead (same fallback from there) --
    this is the base turn's Draw action (see docs/rules/actions.md)
    and the sharing bonus draw (see ``DrawHighestStep``); raises
    ``ValueError`` if the player has no melded cards to determine an
    age from.
    """
    if age is None:
        age = _highest_melded_age(state.players[player_index])
    _validate_age(age)
    state, card = _draw_card_of_age_or_higher(state, age)
    player = state.players[player_index]
    new_player = replace(player, hand=(*player.hand, card))
    return _with_player(state, player_index, new_player), card


def _highest_melded_age(player: PlayerState) -> int:
    top_ages = [pile.cards[0].age for pile in player.board.values() if pile.cards]
    if not top_ages:
        raise ValueError(f"player {player.name!r} has no melded cards to draw from")
    return max(top_ages)


def draw_and_meld(state: GameState, player_index: int, *, age: int) -> tuple[GameState, Card]:
    """The given player draws a card of the given age and melds it directly.

    Same age-fallback as ``draw``, but the drawn card goes straight
    onto the top of its own color's pile on the player's board -- it
    never enters their hand. Used by "draw and meld" dogma effects.
    """
    _validate_age(age)
    state, card = _draw_card_of_age_or_higher(state, age)
    new_player = _meld_onto_board(state.players[player_index], card)
    return _with_player(state, player_index, new_player), card


def draw_and_tuck(state: GameState, player_index: int, *, age: int) -> tuple[GameState, Card]:
    """The given player draws a card of the given age and tucks it directly.

    Same age-fallback as ``draw``, but the drawn card goes straight
    onto the *bottom* of its own color's pile on the player's board --
    it never enters their hand. Used by "draw and tuck" dogma effects.
    """
    _validate_age(age)
    state, card = _draw_card_of_age_or_higher(state, age)
    new_player = _tuck_onto_board(state.players[player_index], card)
    return _with_player(state, player_index, new_player), card


def _validate_age(age: int) -> None:
    if not 1 <= age <= 10:
        raise ValueError(f"age must be between 1 and 10, got {age}")


def _draw_card_of_age_or_higher(state: GameState, age: int) -> tuple[GameState, Card]:
    for candidate_age in range(age, 11):
        pile = state.supply.get(candidate_age)
        if pile:
            card, *rest = pile
            new_supply = dict(state.supply)
            new_supply[candidate_age] = tuple(rest)
            return replace(state, supply=new_supply), card
    raise SupplyExhaustedError(f"no cards available to draw at age {age} or higher")


def reveal(state: GameState, player_index: int, card: Card, zone: Zone) -> GameState:
    """Reveal ``card`` (currently in ``zone``) to the table -- a no-op.

    This changes nothing about game state; it exists purely as an
    explicit call site so effects that reveal a card (e.g.
    Metalworking revealing the card it just drew, in ``Zone.HAND``)
    say so in code, rather than that only existing as a comment. A
    future UI has something concrete to key off of ("Player 2 reveals
    Pottery in their hand") instead of having to infer it.
    """
    return state


def meld(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
    """The given player melds a named card from their hand onto their board.

    The card is removed from the player's hand and placed on top of
    its own color's pile, creating that pile if this is the player's
    first card of that color. If the pile is already splayed, the
    splay direction carries over unchanged.
    """
    player, card = _take_from_hand(state.players[player_index], card_name)
    new_player = _meld_onto_board(player, card)
    return _with_player(state, player_index, new_player), card


def tuck(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
    """The given player tucks a named card from their hand under its board pile.

    Same as ``meld``, except the card is removed from hand and placed
    at the *bottom* of its own color's pile (creating the pile if
    needed) rather than on top -- the existing top card and the pile's
    splay direction are unaffected.
    """
    player, card = _take_from_hand(state.players[player_index], card_name)
    new_player = _tuck_onto_board(player, card)
    return _with_player(state, player_index, new_player), card


def score(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
    """The given player scores a named card from their hand.

    The card is removed from the player's hand and added to their
    score pile.

    TODO: this only covers scoring a card already in hand. See
    docs/rules/glossary.md for what score-pile value ends up meaning.
    """
    player, card = _take_from_hand(state.players[player_index], card_name)
    new_player = replace(player, score_pile=(*player.score_pile, card))
    return _with_player(state, player_index, new_player), card


def return_card(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
    """The given player returns a named card from their hand to the
    bottom of its own age's supply pile.

    The card is removed from hand and appended to the end of
    ``state.supply[card.age]`` -- the bottom of that age's deck,
    opposite the end ``draw`` takes from. Not revealed.
    """
    player, card = _take_from_hand(state.players[player_index], card_name)
    state = _with_player(state, player_index, player)
    new_supply = dict(state.supply)
    new_supply[card.age] = (*new_supply.get(card.age, ()), card)
    return replace(state, supply=new_supply), card


def validate_lowest_in_hand(state: GameState, player_index: int, card_name: str) -> None:
    """Raise ``ValueError`` unless ``card_name`` is (one of, if tied)
    the lowest-age card(s) in the given player's hand.

    A reusable ``CardChoiceValidator`` (see
    ``innovation.model.pending``) for "the lowest card in your hand"
    effects -- e.g. Domestication's ``ChoiceStep.validate`` -- so any
    future dogma with this same constraint can reuse it rather than
    reimplementing the comparison.
    """
    hand = state.players[player_index].hand
    chosen = next((card for card in hand if card.name == card_name), None)
    if chosen is None:
        raise ValueError(
            f"player {state.players[player_index].name!r} has no {card_name!r} in hand"
        )
    lowest_age = min(card.age for card in hand)
    if chosen.age != lowest_age:
        raise ValueError(
            f"{card_name!r} (age {chosen.age}) is not the lowest card in hand (age {lowest_age})"
        )


def _with_player(state: GameState, player_index: int, player: PlayerState) -> GameState:
    new_players = list(state.players)
    new_players[player_index] = player
    return replace(state, players=tuple(new_players))


def _take_from_hand(player: PlayerState, card_name: str) -> tuple[PlayerState, Card]:
    for index, card in enumerate(player.hand):
        if card.name == card_name:
            new_hand = player.hand[:index] + player.hand[index + 1 :]
            return replace(player, hand=new_hand), card
    raise ValueError(f"player {player.name!r} has no {card_name!r} in hand")


def _meld_onto_board(player: PlayerState, card: Card) -> PlayerState:
    pile = player.board.get(card.color, Pile())
    new_board = dict(player.board)
    new_board[card.color] = replace(pile, cards=(card, *pile.cards))
    return replace(player, board=new_board)


def _tuck_onto_board(player: PlayerState, card: Card) -> PlayerState:
    pile = player.board.get(card.color, Pile())
    new_board = dict(player.board)
    new_board[card.color] = replace(pile, cards=(*pile.cards, card))
    return replace(player, board=new_board)


def achieve(state: GameState, player_index: int, age: int) -> None:
    """The active player claims an achievement they qualify for."""
    raise NotImplementedError


def dogma(state: GameState, player_index: int, card_name: str) -> GameState:
    """The given player activates the dogma effects of a named card.

    The card must be the top card of one of the player's piles (a
    covered card's dogma can't be activated). For each of the card's
    dogma effects, in order, this queues a ``ShareStep`` for every
    player eligible to share (in clockwise turn order from the active
    player -- see ``innovation.engine.sharing.eligible_to_share``),
    followed by an ``EffectStep`` that runs it for the active player.

    Steps that need no decision run immediately; the returned state
    pauses at the first step that does (see ``pending_decision`` and
    ``answer_share``) -- when nobody is eligible to share anything,
    that means every effect has already run by the time this returns.

    TODO: demanding isn't implemented yet -- see docs/rules/actions.md.
    """
    card = _require_top_card(state.players[player_index], card_name)
    new_steps: list[PendingStep] = []
    for card_dogma in card.dogmas:
        if card_dogma.effect is None:
            raise NotImplementedError(f"{card_name!r} has no dogma effect implementation yet")
        sharers = eligible_to_share(state, player_index, card_dogma.icon)
        new_steps.extend(
            ShareStep(
                player_index=sharer,
                active_player_index=player_index,
                card_name=card_name,
                effect=card_dogma.effect,
            )
            for sharer in sharers
        )
        new_steps.append(EffectStep(player_index=player_index, effect=card_dogma.effect))
    state = replace(state, pending_steps=(*state.pending_steps, *new_steps))
    return _advance(state)


def pending_decision(state: GameState) -> ShareStep | OptionalStep | ChoiceStep | None:
    """Return the decision currently awaiting an answer, if any.

    A ``ShareStep`` (see ``answer_share``), ``OptionalStep`` (see
    ``answer_optional``), or ``ChoiceStep`` (see ``answer_choice``);
    ``None`` if nothing needs a decision right now.
    """
    if state.pending_steps and isinstance(
        state.pending_steps[0], ShareStep | OptionalStep | ChoiceStep
    ):
        return state.pending_steps[0]
    return None


def answer_share(state: GameState, share: bool) -> GameState:
    """Resolve the pending share decision (see ``pending_decision``).

    Every eligible player's ``ShareStep`` for this effect is asked
    before any of their effects run: a "yes" here only queues the
    sharer's own ``EffectStep`` (see ``_queue_share_effect``) -- it
    doesn't run anything yet, since a later player in the same round
    still has to answer. Only once the round's last ``ShareStep`` is
    resolved does ``_advance`` fall through and actually run the
    queued effects, in turn order, followed by the active player's own
    ``EffectStep``. The first "yes" for the current dogma activation
    also queues a ``DrawHighestStep`` for the active player at the end
    of the queue (see ``DrawHighestStep``); a "no" queues neither.
    Raises ``ValueError`` if no share decision is pending.
    """
    step = pending_decision(state)
    if not isinstance(step, ShareStep):
        raise ValueError("no pending share decision to answer")
    state = replace(state, pending_steps=state.pending_steps[1:])
    if share:
        state = _queue_share_effect(state, step)
        state = _queue_share_bonus_draw(state, step.active_player_index)
    return _advance(state)


def _queue_share_effect(state: GameState, step: ShareStep) -> GameState:
    """Queue the sharer's own copy of the effect, to run once the round's
    remaining ``ShareStep``s are all answered (see ``answer_share``).

    Inserted immediately before the active player's closing
    ``EffectStep`` for this same dogma effect -- the only ``EffectStep``
    in the queue at this point (any earlier "yes" this round already
    landed here too, so this keeps every sharer's effect in turn order,
    ahead of the active player's).
    """
    pending = state.pending_steps
    anchor = next(
        index
        for index, queued in enumerate(pending)
        if isinstance(queued, EffectStep) and queued.player_index == step.active_player_index
    )
    sharer_step = EffectStep(player_index=step.player_index, effect=step.effect)
    new_pending = (*pending[:anchor], sharer_step, *pending[anchor:])
    return replace(state, pending_steps=new_pending)


def answer_optional(state: GameState, card_name: str | None) -> GameState:
    """Resolve the pending optional-action decision (see ``pending_decision``).

    Pass the name of the card to act on, or ``None`` to decline. If a
    name is given and the step has a ``validate`` (see ``OptionalStep``),
    it runs first and can reject the choice with a ``ValueError``
    before anything else happens; otherwise (or if there's no
    ``validate``) the step's ``action`` runs on it and then ``if_done``
    runs with the resulting card. If ``None``, ``if_declined`` runs
    instead (if it's set). Raises ``ValueError`` if no optional
    decision is pending.
    """
    step = pending_decision(state)
    if not isinstance(step, OptionalStep):
        raise ValueError("no pending optional decision to answer")
    state = replace(state, pending_steps=state.pending_steps[1:])
    if card_name is not None:
        if step.validate is not None:
            step.validate(state, step.player_index, card_name)
        state, acted_on_card = step.action(state, step.player_index, card_name)
        state = step.if_done(state, step.player_index, acted_on_card)
    elif step.if_declined is not None:
        state = step.if_declined(state, step.player_index)
    return _advance(state)


def answer_choice(state: GameState, card_name: str) -> GameState:
    """Resolve the pending mandatory-choice decision (see ``pending_decision``).

    Unlike ``answer_optional``, there's no declining -- ``card_name``
    is required. If the step has a ``validate`` (see ``ChoiceStep``),
    it runs first and can reject the choice with a ``ValueError``
    before anything else happens; then the step's ``action`` runs on
    it and ``if_done`` runs with the resulting card. Raises
    ``ValueError`` if no choice decision is pending.
    """
    step = pending_decision(state)
    if not isinstance(step, ChoiceStep):
        raise ValueError("no pending choice decision to answer")
    state = replace(state, pending_steps=state.pending_steps[1:])
    if step.validate is not None:
        step.validate(state, step.player_index, card_name)
    state, acted_on_card = step.action(state, step.player_index, card_name)
    state = step.if_done(state, step.player_index, acted_on_card)
    return _advance(state)


def _queue_share_bonus_draw(state: GameState, active_player_index: int) -> GameState:
    already_queued = any(isinstance(step, DrawHighestStep) for step in state.pending_steps)
    if already_queued:
        return state
    bonus_step = DrawHighestStep(player_index=active_player_index)
    return replace(state, pending_steps=(*state.pending_steps, bonus_step))


def _advance(state: GameState) -> GameState:
    """Run leading no-decision steps until the queue empties or hits a ``ShareStep``."""
    while state.pending_steps and isinstance(state.pending_steps[0], EffectStep | DrawHighestStep):
        step = state.pending_steps[0]
        state = replace(state, pending_steps=state.pending_steps[1:])
        if isinstance(step, DrawHighestStep):
            state, _ = draw(state, step.player_index)
        else:
            state = step.effect(state, step.player_index)
    return state


def _require_top_card(player: PlayerState, card_name: str) -> Card:
    for pile in player.board.values():
        if pile.cards and pile.cards[0].name == card_name:
            return pile.cards[0]
    raise ValueError(f"player {player.name!r} has no {card_name!r} on top of a pile")
