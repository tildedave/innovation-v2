"""Loads and exposes canonical ``Card`` definitions.

TODO: Decide how card data is sourced (e.g. a data file under this
package vs. Python literals here) and populate it card by card, age by
age. Track progress in docs/rules/cards.md.
"""

from __future__ import annotations

from innovation.model.card import Card

CARDS_BY_NAME: dict[str, Card] = {}


def all_cards() -> list[Card]:
    """Return every known card definition."""
    return list(CARDS_BY_NAME.values())


def cards_of_age(age: int) -> list[Card]:
    """Return every known card definition for a given age."""
    return [card for card in CARDS_BY_NAME.values() if card.age == age]
