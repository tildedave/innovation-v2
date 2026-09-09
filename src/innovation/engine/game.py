"""Turn-loop orchestration.

TODO: Drive a full game to completion -- alternate player turns, offer
the four actions, and detect the achievement-count and special-
achievement win conditions. See docs/rules/overview.md.
"""

from __future__ import annotations

from innovation.model.game_state import GameState


class Game:
    """Owns a ``GameState`` and runs turns against it."""

    def __init__(self, state: GameState) -> None:
        self.state = state

    def play_turn(self, player_index: int) -> None:
        raise NotImplementedError

    def is_over(self) -> bool:
        raise NotImplementedError
