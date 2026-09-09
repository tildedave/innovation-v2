"""Top-level game state."""

from __future__ import annotations

from dataclasses import dataclass, field

from innovation.model.card import Card
from innovation.model.player import PlayerState


@dataclass
class GameState:
    """The full state of a single game in progress.

    ``supply`` maps age -> that age's remaining deck, with ``[0]`` the
    next card to be drawn (see ``innovation.engine.actions.draw``).

    TODO: Add current-player/turn tracking and the special-achievements
    pool once the turn loop (see ``innovation.engine.game``) is designed.
    """

    players: list[PlayerState] = field(default_factory=list)
    supply: dict[int, list[Card]] = field(default_factory=dict)
    achievements_available: list[Card] = field(default_factory=list)
