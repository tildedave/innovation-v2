"""The four player actions: Draw, Meld, Achieve, and Dogma.

TODO: Implement Meld, Achieve, and Dogma against ``GameState``/
``PlayerState``. See docs/rules/actions.md for the rules each function
must satisfy.
"""

from __future__ import annotations

from innovation.model.card import Card
from innovation.model.game_state import GameState


class SupplyExhaustedError(Exception):
    """No card is available to draw at or above the requested age.

    TODO: this is expected to trigger a special end-of-game condition
    once the turn loop (see docs/rules/overview.md) is designed --
    callers shouldn't silently swallow it.
    """


def draw(state: GameState, player_index: int, age: int) -> Card:
    """The given player draws a card of the given age into their hand.

    If that age's supply pile is empty, draws from the next higher
    age instead, repeating until a card is found or the supply is
    exhausted through age 10.

    TODO: the base turn "Draw" action determines ``age`` itself (from
    the highest age among the player's top cards) rather than taking
    it as a parameter -- that selection isn't implemented yet since it
    needs board/meld state (see ``meld`` below). This function is the
    primitive both that action and "draw a card of age N" dogma
    effects are expected to use.
    """
    if not 1 <= age <= 10:
        raise ValueError(f"age must be between 1 and 10, got {age}")

    card = _draw_card_of_age_or_higher(state, age)
    state.players[player_index].hand.append(card)
    return card


def _draw_card_of_age_or_higher(state: GameState, age: int) -> Card:
    for candidate_age in range(age, 11):
        pile = state.supply.get(candidate_age)
        if pile:
            return pile.pop(0)
    raise SupplyExhaustedError(f"no cards available to draw at age {age} or higher")


def meld(state: GameState, player_index: int, card_name: str) -> None:
    """The active player melds a card from their hand onto their board."""
    raise NotImplementedError


def achieve(state: GameState, player_index: int, age: int) -> None:
    """The active player claims an achievement they qualify for."""
    raise NotImplementedError


def dogma(state: GameState, player_index: int, card_name: str) -> None:
    """The active player activates the dogma effects of a melded card."""
    raise NotImplementedError
