"""Per-player game state."""

from __future__ import annotations

from dataclasses import dataclass, field

from innovation.model.card import Card
from innovation.model.enums import Color


@dataclass
class PlayerState:
    """Mutable state owned by a single player.

    TODO: ``board`` currently models each color pile as an unsplayed
    stack. Add splay direction and tucked/scored bookkeeping once the
    engine's action logic (see docs/rules/actions.md) is designed.
    """

    name: str
    hand: list[Card] = field(default_factory=list)
    score_pile: list[Card] = field(default_factory=list)
    board: dict[Color, list[Card]] = field(default_factory=dict)
    achievements: list[Card] = field(default_factory=list)
