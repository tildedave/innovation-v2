"""The four player actions: Draw, Meld, Achieve, and Dogma.

TODO: Implement each action against ``GameState``/``PlayerState``. See
docs/rules/actions.md for the rules each function must satisfy.
"""

from __future__ import annotations

from innovation.model.game_state import GameState


def draw(state: GameState, player_index: int) -> None:
    """The active player draws the top card of their lowest available age."""
    raise NotImplementedError


def meld(state: GameState, player_index: int, card_name: str) -> None:
    """The active player melds a card from their hand onto their board."""
    raise NotImplementedError


def achieve(state: GameState, player_index: int, age: int) -> None:
    """The active player claims an achievement they qualify for."""
    raise NotImplementedError


def dogma(state: GameState, player_index: int, card_name: str) -> None:
    """The active player activates the dogma effects of a melded card."""
    raise NotImplementedError
