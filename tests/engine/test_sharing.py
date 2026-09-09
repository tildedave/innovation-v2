"""Tests for dogma sharing eligibility (src/innovation/engine/sharing.py)."""

from innovation.engine.sharing import eligible_to_share
from innovation.model.card import Card, CardIcons
from innovation.model.enums import Color, Icon
from innovation.model.game_state import GameState
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


def _card_with_icon(name: str, icon: Icon) -> Card:
    return Card(
        name=name,
        age=1,
        color=Color.RED,
        icons=CardIcons(
            top_left=icon,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
    )


_COLORS = (Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE, Color.PURPLE)


def _player(name: str, crowns: int) -> PlayerState:
    # One card per color pile, since a pile's top card (only) is always
    # visible regardless of splay -- avoids depending on splay behavior
    # just to set up a player's icon count for these tests.
    board = {
        color: Pile(cards=(_card_with_icon(f"{name}-{i}", Icon.CROWN),))
        for i, color in enumerate(_COLORS[:crowns])
    }
    return PlayerState(name=name, board=board)


def test_a_player_with_more_of_the_icon_is_eligible_to_share() -> None:
    active = _player("Active", crowns=1)
    other = _player("Other", crowns=2)
    state = GameState(players=(active, other))

    assert eligible_to_share(state, active_player_index=0, icon=Icon.CROWN) == [1]


def test_a_player_with_the_same_number_of_the_icon_is_eligible_to_share() -> None:
    active = _player("Active", crowns=2)
    other = _player("Other", crowns=2)
    state = GameState(players=(active, other))

    assert eligible_to_share(state, active_player_index=0, icon=Icon.CROWN) == [1]


def test_a_player_with_fewer_of_the_icon_is_not_eligible_to_share() -> None:
    active = _player("Active", crowns=2)
    other = _player("Other", crowns=1)
    state = GameState(players=(active, other))

    assert eligible_to_share(state, active_player_index=0, icon=Icon.CROWN) == []


def test_the_active_player_is_never_included() -> None:
    active = _player("Active", crowns=0)
    state = GameState(players=(active,))

    assert eligible_to_share(state, active_player_index=0, icon=Icon.CROWN) == []


def test_only_eligible_players_are_returned_from_several() -> None:
    active = _player("Active", crowns=2)
    fewer = _player("Fewer", crowns=1)
    same = _player("Same", crowns=2)
    more = _player("More", crowns=3)
    state = GameState(players=(active, fewer, same, more))

    assert eligible_to_share(state, active_player_index=0, icon=Icon.CROWN) == [2, 3]


def test_eligible_players_are_returned_in_clockwise_turn_order_from_the_active_player() -> None:
    active = _player("Active", crowns=2)
    a = _player("A", crowns=2)
    b = _player("B", crowns=2)
    c = _player("C", crowns=2)
    state = GameState(players=(a, b, active, c))

    assert eligible_to_share(state, active_player_index=2, icon=Icon.CROWN) == [3, 0, 1]


def test_turn_order_skips_ineligible_players_but_keeps_relative_order() -> None:
    eligible_a = _player("EligibleA", crowns=2)
    active = _player("Active", crowns=2)
    fewer = _player("Fewer", crowns=1)
    eligible_b = _player("EligibleB", crowns=3)
    state = GameState(players=(eligible_a, active, fewer, eligible_b))

    assert eligible_to_share(state, active_player_index=1, icon=Icon.CROWN) == [3, 0]


def test_a_different_icon_type_is_not_counted() -> None:
    active = PlayerState(
        name="Active", board={Color.RED: Pile(cards=(_card_with_icon("A", Icon.CROWN),))}
    )
    other = PlayerState(
        name="Other", board={Color.RED: Pile(cards=(_card_with_icon("B", Icon.LEAF),))}
    )
    state = GameState(players=(active, other))

    assert eligible_to_share(state, active_player_index=0, icon=Icon.CROWN) == []
