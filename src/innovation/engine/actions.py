"""The four player actions: Draw, Meld, Achieve, and Dogma.

Every action returns a new ``GameState`` rather than mutating the one
it's given (see ``innovation.model`` and ``innovation.engine`` for why).
Most also return the ``Card`` the action was about, since the caller
usually needs to know which card was drawn/melded/tucked and re-deriving
that from the new state alone would be more awkward than useful.

TODO: Implement Achieve against ``GameState``/``PlayerState``. See
docs/rules/actions.md for the rules each function must satisfy.
"""

from __future__ import annotations

from dataclasses import replace

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


def draw(state: GameState, player_index: int, age: int) -> tuple[GameState, Card]:
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
    state, card = _draw_card_of_age_or_higher(state, age)
    player = state.players[player_index]
    new_player = replace(player, hand=(*player.hand, card))
    return _with_player(state, player_index, new_player), card


def draw_and_meld(state: GameState, player_index: int, *, age: int) -> tuple[GameState, Card]:
    """The given player draws a card of the given age and melds it directly.

    Same age-fallback as ``draw``, but the drawn card goes straight
    onto the top of its own color's pile on the player's board -- it
    never enters their hand. Used by "draw and meld" dogma effects.
    """
    _validate_age(age)
    state, card = _draw_card_of_age_or_higher(state, age)
    new_player = _meld_onto_board(state.players[player_index], card)
    return _with_player(state, player_index, new_player), card


def draw_and_tuck(state: GameState, player_index: int, *, age: int) -> tuple[GameState, Card]:
    """The given player draws a card of the given age and tucks it directly.

    Same age-fallback as ``draw``, but the drawn card goes straight
    onto the *bottom* of its own color's pile on the player's board --
    it never enters their hand. Used by "draw and tuck" dogma effects.
    """
    _validate_age(age)
    state, card = _draw_card_of_age_or_higher(state, age)
    new_player = _tuck_onto_board(state.players[player_index], card)
    return _with_player(state, player_index, new_player), card


def _validate_age(age: int) -> None:
    if not 1 <= age <= 10:
        raise ValueError(f"age must be between 1 and 10, got {age}")


def _draw_card_of_age_or_higher(state: GameState, age: int) -> tuple[GameState, Card]:
    for candidate_age in range(age, 11):
        pile = state.supply.get(candidate_age)
        if pile:
            card, *rest = pile
            new_supply = dict(state.supply)
            new_supply[candidate_age] = tuple(rest)
            return replace(state, supply=new_supply), card
    raise SupplyExhaustedError(f"no cards available to draw at age {age} or higher")


def meld(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
    """The given player melds a named card from their hand onto their board.

    The card is removed from the player's hand and placed on top of
    its own color's pile, creating that pile if this is the player's
    first card of that color. If the pile is already splayed, the
    splay direction carries over unchanged.
    """
    player, card = _take_from_hand(state.players[player_index], card_name)
    new_player = _meld_onto_board(player, card)
    return _with_player(state, player_index, new_player), card


def tuck(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
    """The given player tucks a named card from their hand under its board pile.

    Same as ``meld``, except the card is removed from hand and placed
    at the *bottom* of its own color's pile (creating the pile if
    needed) rather than on top -- the existing top card and the pile's
    splay direction are unaffected.
    """
    player, card = _take_from_hand(state.players[player_index], card_name)
    new_player = _tuck_onto_board(player, card)
    return _with_player(state, player_index, new_player), card


def _with_player(state: GameState, player_index: int, player: PlayerState) -> GameState:
    new_players = list(state.players)
    new_players[player_index] = player
    return replace(state, players=tuple(new_players))


def _take_from_hand(player: PlayerState, card_name: str) -> tuple[PlayerState, Card]:
    for index, card in enumerate(player.hand):
        if card.name == card_name:
            new_hand = player.hand[:index] + player.hand[index + 1 :]
            return replace(player, hand=new_hand), card
    raise ValueError(f"player {player.name!r} has no {card_name!r} in hand")


def _meld_onto_board(player: PlayerState, card: Card) -> PlayerState:
    pile = player.board.get(card.color, Pile())
    new_board = dict(player.board)
    new_board[card.color] = replace(pile, cards=(card, *pile.cards))
    return replace(player, board=new_board)


def _tuck_onto_board(player: PlayerState, card: Card) -> PlayerState:
    pile = player.board.get(card.color, Pile())
    new_board = dict(player.board)
    new_board[card.color] = replace(pile, cards=(*pile.cards, card))
    return replace(player, board=new_board)


def achieve(state: GameState, player_index: int, age: int) -> None:
    """The active player claims an achievement they qualify for."""
    raise NotImplementedError


def dogma(state: GameState, player_index: int, card_name: str) -> GameState:
    """The given player activates the dogma effects of a named card.

    The card must be the top card of one of the player's piles (a
    covered card's dogma can't be activated). Each of the card's
    dogma effects runs in order, for this player only.

    TODO: sharing/demanding other players in this effect isn't
    implemented yet -- see docs/rules/actions.md.
    """
    card = _require_top_card(state.players[player_index], card_name)
    for card_dogma in card.dogmas:
        if card_dogma.effect is None:
            raise NotImplementedError(f"{card_name!r} has no dogma effect implementation yet")
        state = card_dogma.effect(state, player_index)
    return state


def _require_top_card(player: PlayerState, card_name: str) -> Card:
    for pile in player.board.values():
        if pile.cards and pile.cards[0].name == card_name:
            return pile.cards[0]
    raise ValueError(f"player {player.name!r} has no {card_name!r} on top of a pile")
