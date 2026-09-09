"""The card data model."""

from __future__ import annotations

from dataclasses import dataclass, field

from innovation.model.enums import Color, Icon


@dataclass(frozen=True)
class Dogma:
    """A single dogma effect printed on a card.

    TODO: Replace the raw-text placeholder with a structured effect
    once the action/effect system in ``innovation.engine`` is designed.
    """

    text: str


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
