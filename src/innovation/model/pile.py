"""A single color pile on a player's board."""

from __future__ import annotations

from dataclasses import dataclass, field

from innovation.model.card import Card
from innovation.model.enums import Splay


@dataclass
class Pile:
    """One color's stack of melded cards for a single player.

    ``cards[0]`` is the top of the pile and is always fully visible;
    the rest are covered, ordered from just-underneath-the-top to the
    bottom. ``splay`` controls which icons of the covered cards are
    also visible -- see ``innovation.engine.board.count_icons``.
    """

    cards: list[Card] = field(default_factory=list)
    splay: Splay = Splay.NONE
