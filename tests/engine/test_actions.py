"""Tests for the Draw action (src/innovation/engine/actions.py)."""

import pytest

from innovation.engine.actions import SupplyExhaustedError, draw
from innovation.model.card import Card, CardIcons
from innovation.model.enums import Color, Icon
from innovation.model.game_state import GameState
from innovation.model.player import PlayerState


def _card(name: str, age: int) -> Card:
    return Card(
        name=name,
        age=age,
        color=Color.RED,
        icons=CardIcons(
            top_left=Icon.NONE,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
    )


def test_draw_moves_the_top_card_of_the_requested_age_to_the_players_hand() -> None:
    card = _card("Pottery", age=1)
    state = GameState(players=[PlayerState(name="Ada")], supply={1: [card]})

    drawn = draw(state, player_index=0, age=1)

    assert drawn is card
    assert state.players[0].hand == [card]
    assert state.supply[1] == []


def test_draw_takes_the_first_card_in_the_pile() -> None:
    first = _card("First", age=1)
    second = _card("Second", age=1)
    state = GameState(players=[PlayerState(name="Ada")], supply={1: [first, second]})

    drawn = draw(state, player_index=0, age=1)

    assert drawn is first
    assert state.supply[1] == [second]


def test_draw_falls_back_to_the_next_age_when_the_pile_is_empty() -> None:
    card = _card("Currency", age=2)
    state = GameState(players=[PlayerState(name="Ada")], supply={1: [], 2: [card]})

    drawn = draw(state, player_index=0, age=1)

    assert drawn is card
    assert state.supply[2] == []


def test_draw_falls_back_through_several_empty_piles() -> None:
    card = _card("Machinery", age=4)
    state = GameState(players=[PlayerState(name="Ada")], supply={1: [], 2: [], 3: [], 4: [card]})

    drawn = draw(state, player_index=0, age=1)

    assert drawn is card


def test_draw_falls_back_when_the_requested_age_has_no_supply_entry_at_all() -> None:
    card = _card("Canning", age=3)
    state = GameState(players=[PlayerState(name="Ada")], supply={3: [card]})

    drawn = draw(state, player_index=0, age=1)

    assert drawn is card


def test_draw_raises_supply_exhausted_when_no_higher_age_has_cards_either() -> None:
    state = GameState(players=[PlayerState(name="Ada")], supply={9: [], 10: []})

    with pytest.raises(SupplyExhaustedError, match="age 9"):
        draw(state, player_index=0, age=9)


def test_draw_raises_supply_exhausted_with_no_supply_data_at_all() -> None:
    state = GameState(players=[PlayerState(name="Ada")])

    with pytest.raises(SupplyExhaustedError):
        draw(state, player_index=0, age=1)


@pytest.mark.parametrize("age", [0, -1, 11])
def test_draw_rejects_an_age_outside_one_through_ten(age: int) -> None:
    state = GameState(players=[PlayerState(name="Ada")])

    with pytest.raises(ValueError, match="age"):
        draw(state, player_index=0, age=age)
