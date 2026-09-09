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

from innovation.engine.actions import draw_and_meld
from innovation.model.card import Card, CardIcons, Dogma
from innovation.model.enums import Color, Icon
from innovation.model.game_state import GameState


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

CARDS_BY_NAME: dict[str, Card] = {card.name: card for card in [SAILING]}


def all_cards() -> list[Card]:
    """Return every known card definition."""
    return list(CARDS_BY_NAME.values())


def cards_of_age(age: int) -> list[Card]:
    """Return every known card definition for a given age."""
    return [card for card in CARDS_BY_NAME.values() if card.age == age]
