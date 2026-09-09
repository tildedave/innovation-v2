"""Core enumerations shared across the rules engine.

TODO: Verify this against the official 4th-edition rulebook and the
physical cards before card data (see ``innovation.cards.registry``) is
filled in -- names here are provisional. See docs/rules/glossary.md
for the definitions each member is expected to satisfy.
"""

from __future__ import annotations

from enum import Enum, auto


class Color(Enum):
    """The five card colors used in the base game."""

    RED = auto()
    YELLOW = auto()
    GREEN = auto()
    BLUE = auto()
    PURPLE = auto()


class Icon(Enum):
    """The icon types that can appear in each of a card's four corners."""

    CASTLE = auto()
    CROWN = auto()
    LEAF = auto()
    FACTORY = auto()
    CLOCK = auto()
    BULB = auto()
    NONE = auto()


class Splay(Enum):
    """How a color pile is fanned out, exposing covered cards' icons.

    NONE means unsplayed: only the top card of the pile is visible.
    """

    NONE = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()


class Zone(Enum):
    """Where a card is when it's revealed -- see engine.actions.reveal.

    Matches the places a card actually lives in the model: a player's
    hand or score pile or board (``PlayerState``), or the supply
    (``GameState``).
    """

    HAND = auto()
    SCORE_PILE = auto()
    BOARD = auto()
    SUPPLY = auto()
