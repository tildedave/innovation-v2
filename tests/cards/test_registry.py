"""Tests for the card registry (src/innovation/cards/registry.py)."""

from innovation.cards.registry import SAILING, all_cards, cards_of_age
from innovation.engine.actions import dogma
from innovation.model.card import Card, CardIcons
from innovation.model.enums import Color, Icon
from innovation.model.game_state import GameState
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


def test_sailing_is_a_green_age_one_card() -> None:
    assert SAILING.age == 1
    assert SAILING.color == Color.GREEN


def test_sailing_icons() -> None:
    assert SAILING.icons.top_left == Icon.CROWN
    assert SAILING.icons.bottom_left == Icon.CROWN
    assert SAILING.icons.bottom_center == Icon.NONE
    assert SAILING.icons.bottom_right == Icon.LEAF


def test_sailing_has_one_crown_dogma_with_an_implemented_effect() -> None:
    assert len(SAILING.dogmas) == 1
    assert SAILING.dogmas[0].icon == Icon.CROWN
    assert SAILING.dogmas[0].effect is not None


def test_sailing_is_registered() -> None:
    assert all_cards() == [SAILING]
    assert cards_of_age(1) == [SAILING]
    assert cards_of_age(2) == []


def test_sailings_dogma_draws_and_melds_a_card_of_age_one() -> None:
    drawn_card = Card(
        name="Pottery",
        age=1,
        color=Color.BLUE,
        icons=CardIcons(
            top_left=Icon.NONE,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
    )
    player = PlayerState(name="Ada", board={Color.GREEN: Pile(cards=(SAILING,))})
    state = GameState(players=(player,), supply={1: (drawn_card,)})

    new_state = dogma(state, player_index=0, card_name="Sailing")

    assert new_state.players[0].board[Color.BLUE].cards == (drawn_card,)


def test_sailings_dogma_falls_back_to_a_higher_age_when_the_one_pile_is_empty() -> None:
    drawn_card = Card(
        name="Currency",
        age=2,
        color=Color.BLUE,
        icons=CardIcons(
            top_left=Icon.NONE,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
    )
    player = PlayerState(name="Ada", board={Color.GREEN: Pile(cards=(SAILING,))})
    state = GameState(players=(player,), supply={1: (), 2: (drawn_card,)})

    new_state = dogma(state, player_index=0, card_name="Sailing")

    assert new_state.players[0].board[Color.BLUE].cards == (drawn_card,)
