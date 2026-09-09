"""The four player actions: Draw, Meld, Achieve, and Dogma.

TODO: Implement Achieve and Dogma against ``GameState``/``PlayerState``.
See docs/rules/actions.md for the rules each function must satisfy.
"""

from __future__ import annotations

from innovation.model.card import Card
from innovation.model.game_state import GameState
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


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
    _validate_age(age)
    card = _draw_card_of_age_or_higher(state, age)
    state.players[player_index].hand.append(card)
    return card


def draw_and_meld(state: GameState, player_index: int, age: int) -> Card:
    """The given player draws a card of the given age and melds it directly.

    Same age-fallback as ``draw``, but the drawn card goes straight
    onto the top of its own color's pile on the player's board -- it
    never enters their hand. Used by "draw and meld" dogma effects.
    """
    _validate_age(age)
    card = _draw_card_of_age_or_higher(state, age)
    _meld_onto_board(state.players[player_index], card)
    return card


def draw_and_tuck(state: GameState, player_index: int, age: int) -> Card:
    """The given player draws a card of the given age and tucks it directly.

    Same age-fallback as ``draw``, but the drawn card goes straight
    onto the *bottom* of its own color's pile on the player's board --
    it never enters their hand. Used by "draw and tuck" dogma effects.
    """
    _validate_age(age)
    card = _draw_card_of_age_or_higher(state, age)
    _tuck_onto_board(state.players[player_index], card)
    return card


def _validate_age(age: int) -> None:
    if not 1 <= age <= 10:
        raise ValueError(f"age must be between 1 and 10, got {age}")


def _draw_card_of_age_or_higher(state: GameState, age: int) -> Card:
    for candidate_age in range(age, 11):
        pile = state.supply.get(candidate_age)
        if pile:
            return pile.pop(0)
    raise SupplyExhaustedError(f"no cards available to draw at age {age} or higher")


def meld(state: GameState, player_index: int, card_name: str) -> Card:
    """The given player melds a named card from their hand onto their board.

    The card is removed from the player's hand and placed on top of
    its own color's pile, creating that pile if this is the player's
    first card of that color. If the pile is already splayed, the
    splay direction carries over unchanged.
    """
    player = state.players[player_index]
    card = _take_from_hand(player, card_name)
    _meld_onto_board(player, card)
    return card


def tuck(state: GameState, player_index: int, card_name: str) -> Card:
    """The given player tucks a named card from their hand under its board pile.

    Same as ``meld``, except the card is removed from hand and placed
    at the *bottom* of its own color's pile (creating the pile if
    needed) rather than on top -- the existing top card and the pile's
    splay direction are unaffected.
    """
    player = state.players[player_index]
    card = _take_from_hand(player, card_name)
    _tuck_onto_board(player, card)
    return card


def _take_from_hand(player: PlayerState, card_name: str) -> Card:
    for index, card in enumerate(player.hand):
        if card.name == card_name:
            return player.hand.pop(index)
    raise ValueError(f"player {player.name!r} has no {card_name!r} in hand")


def _meld_onto_board(player: PlayerState, card: Card) -> None:
    pile = player.board.setdefault(card.color, Pile())
    pile.cards.insert(0, card)


def _tuck_onto_board(player: PlayerState, card: Card) -> None:
    pile = player.board.setdefault(card.color, Pile())
    pile.cards.append(card)


def achieve(state: GameState, player_index: int, age: int) -> None:
    """The active player claims an achievement they qualify for."""
    raise NotImplementedError


def dogma(state: GameState, player_index: int, card_name: str) -> None:
    """The active player activates the dogma effects of a melded card."""
    raise NotImplementedError
