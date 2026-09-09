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
