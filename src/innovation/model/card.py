"""The card data model."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from innovation.model.enums import Color, Icon

if TYPE_CHECKING:
    from innovation.model.game_state import GameState

DogmaEffect = Callable[["GameState", int], "GameState"]
"""Given the game state and the index of the player currently eligible
for this portion of a dogma effect, returns the new state after
applying it. Built from primitives in ``innovation.engine.actions``
and stored alongside the card's data in ``innovation.cards.registry``
-- see docs/architecture.md.
"""


@dataclass(frozen=True)
class Dogma:
    """A single dogma effect printed on a card.

    ``text`` is the effect's rules text, present as soon as a card's
    data is entered. ``icon`` is the icon type this dogma is printed
    under, which will determine share/demand eligibility once that's
    implemented (see docs/rules/actions.md) -- it's inert data for now.
    ``effect`` is the executable behavior and is ``None`` until it's
    been implemented -- entering a card's data and implementing its
    dogma effects are deliberately separate steps (see
    docs/rules/cards.md).

    TODO: sharing/demanding (other players benefiting from or being
    forced to suffer part of the effect) isn't modeled yet -- ``effect``
    only covers what happens for one eligible player at a time. See
    docs/rules/actions.md.
    """

    text: str
    icon: Icon
    effect: DogmaEffect | None = None


@dataclass(frozen=True)
class CardIcons:
    """The four icon positions printed on a card.

    A position holds ``Icon.NONE`` when the card has no icon there.
    See ``innovation.engine.board`` for how pile splay direction
    affects which of a covered card's icons are visible/countable.
    """

    top_left: Icon
    bottom_left: Icon
    bottom_center: Icon
    bottom_right: Icon

    def all_icons(self) -> tuple[Icon, Icon, Icon, Icon]:
        """All four icons, in no particular order (visibility-agnostic)."""
        return (self.top_left, self.bottom_left, self.bottom_center, self.bottom_right)


@dataclass(frozen=True)
class Card:
    """An immutable definition of one Innovation card.

    Card instances are canonical, shared definitions looked up via
    ``innovation.cards.registry`` -- game state tracks *which* cards
    are where (see ``innovation.model.game_state``), not separate
    mutable copies of this class.
    """

    name: str
    age: int
    color: Color
    icons: CardIcons
    dogmas: tuple[Dogma, ...] = field(default_factory=tuple)
