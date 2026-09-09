"""Canonical ``Card`` definitions, keyed by name.

A card's data (identity, printed text) and its dogma effect
implementations are deliberately colocated here, in one place per
card, rather than split across packages -- effects are built from
primitives in ``innovation.engine.actions``. See docs/architecture.md.

TODO: Decide how card data is sourced (e.g. a data file under this
package vs. Python literals here) once there are enough cards for a
single module to be unwieldy. Track progress in docs/rules/cards.md.
"""

from __future__ import annotations

from dataclasses import replace

from innovation.engine.actions import (
    draw,
    draw_and_meld,
    meld,
    return_card,
    reveal,
    score,
    validate_lowest_in_hand,
)
from innovation.model.card import Card, CardIcons, Dogma
from innovation.model.enums import Color, Icon, Zone
from innovation.model.game_state import GameState
from innovation.model.pending import ChoiceStep, EffectStep, OptionalStep


def _sailing_dogma(state: GameState, player_index: int) -> GameState:
    """Sailing's dogma: draw and meld a card of age 1 (or higher, as a fallback)."""
    new_state, _ = draw_and_meld(state, player_index, age=1)
    return new_state


SAILING = Card(
    name="Sailing",
    age=1,
    color=Color.GREEN,
    icons=CardIcons(
        top_left=Icon.CROWN,
        bottom_left=Icon.CROWN,
        bottom_center=Icon.NONE,
        bottom_right=Icon.LEAF,
    ),
    dogmas=(Dogma(text="Draw and meld a 1.", icon=Icon.CROWN, effect=_sailing_dogma),),
)


def _metalworking_dogma(state: GameState, player_index: int) -> GameState:
    """Metalworking's dogma: draw and reveal a 1; if it has a Castle
    icon, score it and repeat this effect.

    "Repeat" is expressed as data, not control flow: rather than
    looping internally, this queues another ``EffectStep`` for itself
    (see ``innovation.engine.actions._advance``, which drains
    ``pending_steps`` one step at a time). That keeps every "draw,
    check, maybe score" cycle a visible, individually-processable step
    in the queue -- important for an eventual UI that wants to show
    each one, rather than the whole chain resolving invisibly inside
    one function call.
    """
    state, card = draw(state, player_index, age=1)
    state = reveal(state, player_index, card, Zone.HAND)
    if Icon.CASTLE not in card.icons.all_icons():
        return state
    state, _ = score(state, player_index, card.name)
    repeat_step = EffectStep(player_index=player_index, effect=_metalworking_dogma)
    return replace(state, pending_steps=(*state.pending_steps, repeat_step))


METALWORKING = Card(
    name="Metalworking",
    age=1,
    color=Color.RED,
    icons=CardIcons(
        top_left=Icon.CASTLE,
        bottom_left=Icon.CASTLE,
        bottom_center=Icon.NONE,
        bottom_right=Icon.CASTLE,
    ),
    dogmas=(
        Dogma(
            text="Draw and reveal a 1. If it has a Castle icon, score it and repeat this effect.",
            icon=Icon.CASTLE,
            effect=_metalworking_dogma,
        ),
    ),
)


def _agriculture_dogma(state: GameState, player_index: int) -> GameState:
    """Agriculture's dogma: you may return a card from your hand. If
    you do, draw and score a card of value one higher than the card
    you return.
    """

    def after_return(state: GameState, player_index: int, returned_card: Card) -> GameState:
        state, drawn = draw(state, player_index, age=returned_card.age + 1)
        state, _ = score(state, player_index, drawn.name)
        return state

    optional_step = OptionalStep(
        player_index=player_index,
        card_name="Agriculture",
        action=return_card,
        if_done=after_return,
    )
    return replace(state, pending_steps=(*state.pending_steps, optional_step))


AGRICULTURE = Card(
    name="Agriculture",
    age=1,
    color=Color.YELLOW,
    icons=CardIcons(
        top_left=Icon.NONE,
        bottom_left=Icon.LEAF,
        bottom_center=Icon.LEAF,
        bottom_right=Icon.LEAF,
    ),
    dogmas=(
        Dogma(
            text=(
                "You may return a card from your hand. If you do, draw and score a "
                "card of value one higher than the card you return."
            ),
            icon=Icon.LEAF,
            effect=_agriculture_dogma,
        ),
    ),
)


def _domestication_dogma(state: GameState, player_index: int) -> GameState:
    """Domestication's dogma: meld the lowest card in your hand, then draw a 1.

    Not optional -- melding happens no matter what -- but the player
    still chooses *which* card (there may be a tie for lowest age);
    the choice is validated to actually be a lowest-age card rather
    than picked automatically.
    """

    def after_meld(state: GameState, player_index: int, melded_card: Card) -> GameState:
        state, _ = draw(state, player_index, age=1)
        return state

    choice_step = ChoiceStep(
        player_index=player_index,
        card_name="Domestication",
        action=meld,
        if_done=after_meld,
        validate=validate_lowest_in_hand,
    )
    return replace(state, pending_steps=(*state.pending_steps, choice_step))


DOMESTICATION = Card(
    name="Domestication",
    age=1,
    color=Color.YELLOW,
    icons=CardIcons(
        top_left=Icon.CASTLE,
        bottom_left=Icon.CROWN,
        bottom_center=Icon.NONE,
        bottom_right=Icon.CASTLE,
    ),
    dogmas=(
        Dogma(
            text="Meld the lowest card in your hand. Draw a 1.",
            icon=Icon.CASTLE,
            effect=_domestication_dogma,
        ),
    ),
)

CARDS_BY_NAME: dict[str, Card] = {
    card.name: card for card in [SAILING, METALWORKING, AGRICULTURE, DOMESTICATION]
}


def all_cards() -> list[Card]:
    """Return every known card definition."""
    return list(CARDS_BY_NAME.values())


def cards_of_age(age: int) -> list[Card]:
    """Return every known card definition for a given age."""
    return [card for card in CARDS_BY_NAME.values() if card.age == age]
