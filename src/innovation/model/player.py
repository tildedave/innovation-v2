"""Per-player game state."""

from __future__ import annotations

from dataclasses import dataclass, field

from innovation.model.card import Card
from innovation.model.enums import Color
from innovation.model.pile import Pile


@dataclass
class PlayerState:
    """Mutable state owned by a single player.

    ``board`` only holds entries for colors the player has melded at
    least one card of -- see ``innovation.engine.board`` for splaying
    and icon-visibility queries.

    TODO: Add achievement/special-achievement bookkeeping details once
    the engine's action logic (see docs/rules/actions.md) is designed.
    """

    name: str
    hand: list[Card] = field(default_factory=list)
    score_pile: list[Card] = field(default_factory=list)
    board: dict[Color, Pile] = field(default_factory=dict)
    achievements: list[Card] = field(default_factory=list)
