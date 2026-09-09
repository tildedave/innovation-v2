"""Tests for the Draw, Meld, and Tuck actions (src/innovation/engine/actions.py)."""

import pytest

from innovation.engine.actions import (
    SupplyExhaustedError,
    draw,
    draw_and_meld,
    draw_and_tuck,
    meld,
    tuck,
)
from innovation.model.card import Card, CardIcons
from innovation.model.enums import Color, Icon, Splay
from innovation.model.game_state import GameState
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


def _card(name: str, age: int = 1, color: Color = Color.RED) -> Card:
    return Card(
        name=name,
        age=age,
        color=color,
        icons=CardIcons(
            top_left=Icon.NONE,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
    )


def test_draw_moves_the_top_card_of_the_requested_age_to_the_players_hand() -> None:
    card = _card("Pottery", age=1)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (card,)})

    new_state, drawn = draw(state, player_index=0, age=1)

    assert drawn is card
    assert new_state.players[0].hand == (card,)
    assert new_state.supply[1] == ()


def test_draw_does_not_modify_the_original_state() -> None:
    card = _card("Pottery", age=1)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (card,)})

    draw(state, player_index=0, age=1)

    assert state.players[0].hand == ()
    assert state.supply[1] == (card,)


def test_draw_takes_the_first_card_in_the_pile() -> None:
    first = _card("First", age=1)
    second = _card("Second", age=1)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (first, second)})

    new_state, drawn = draw(state, player_index=0, age=1)

    assert drawn is first
    assert new_state.supply[1] == (second,)


def test_draw_falls_back_to_the_next_age_when_the_pile_is_empty() -> None:
    card = _card("Currency", age=2)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (), 2: (card,)})

    new_state, drawn = draw(state, player_index=0, age=1)

    assert drawn is card
    assert new_state.supply[2] == ()


def test_draw_falls_back_through_several_empty_piles() -> None:
    card = _card("Machinery", age=4)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (), 2: (), 3: (), 4: (card,)})

    _, drawn = draw(state, player_index=0, age=1)

    assert drawn is card


def test_draw_falls_back_when_the_requested_age_has_no_supply_entry_at_all() -> None:
    card = _card("Canning", age=3)
    state = GameState(players=(PlayerState(name="Ada"),), supply={3: (card,)})

    _, drawn = draw(state, player_index=0, age=1)

    assert drawn is card


def test_draw_raises_supply_exhausted_when_no_higher_age_has_cards_either() -> None:
    state = GameState(players=(PlayerState(name="Ada"),), supply={9: (), 10: ()})

    with pytest.raises(SupplyExhaustedError, match="age 9"):
        draw(state, player_index=0, age=9)


def test_draw_raises_supply_exhausted_with_no_supply_data_at_all() -> None:
    state = GameState(players=(PlayerState(name="Ada"),))

    with pytest.raises(SupplyExhaustedError):
        draw(state, player_index=0, age=1)


@pytest.mark.parametrize("age", [0, -1, 11])
def test_draw_rejects_an_age_outside_one_through_ten(age: int) -> None:
    state = GameState(players=(PlayerState(name="Ada"),))

    with pytest.raises(ValueError, match="age"):
        draw(state, player_index=0, age=age)


def test_draw_and_meld_places_the_card_directly_onto_a_new_pile() -> None:
    card = _card("Pottery", age=1, color=Color.RED)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (card,)})

    new_state, melded = draw_and_meld(state, player_index=0, age=1)

    assert melded is card
    assert new_state.players[0].hand == ()
    assert new_state.players[0].board[Color.RED].cards == (card,)
    assert new_state.supply[1] == ()


def test_draw_and_meld_places_the_card_on_top_of_an_existing_pile() -> None:
    old_top = _card("OldTop", color=Color.RED)
    new_card = _card("NewTop", age=1, color=Color.RED)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(old_top,))})
    state = GameState(players=(player,), supply={1: (new_card,)})

    new_state, _ = draw_and_meld(state, player_index=0, age=1)

    assert new_state.players[0].board[Color.RED].cards == (new_card, old_top)


def test_draw_and_meld_preserves_the_splay_of_an_existing_pile() -> None:
    old_top = _card("OldTop", color=Color.RED)
    new_card = _card("NewTop", age=1, color=Color.RED)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(old_top,), splay=Splay.UP)})
    state = GameState(players=(player,), supply={1: (new_card,)})

    new_state, _ = draw_and_meld(state, player_index=0, age=1)

    assert new_state.players[0].board[Color.RED].splay is Splay.UP


def test_draw_and_meld_falls_back_to_the_next_age_when_the_pile_is_empty() -> None:
    card = _card("Currency", age=2)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (), 2: (card,)})

    _, melded = draw_and_meld(state, player_index=0, age=1)

    assert melded is card


def test_draw_and_meld_raises_supply_exhausted_when_nothing_is_available() -> None:
    state = GameState(players=(PlayerState(name="Ada"),), supply={9: (), 10: ()})

    with pytest.raises(SupplyExhaustedError, match="age 9"):
        draw_and_meld(state, player_index=0, age=9)


@pytest.mark.parametrize("age", [0, -1, 11])
def test_draw_and_meld_rejects_an_age_outside_one_through_ten(age: int) -> None:
    state = GameState(players=(PlayerState(name="Ada"),))

    with pytest.raises(ValueError, match="age"):
        draw_and_meld(state, player_index=0, age=age)


def test_meld_moves_the_card_from_hand_to_a_new_pile_of_its_color() -> None:
    card = _card("Pottery", color=Color.RED)
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),))

    new_state, melded = meld(state, player_index=0, card_name="Pottery")

    assert melded is card
    assert new_state.players[0].hand == ()
    assert new_state.players[0].board[Color.RED].cards == (card,)


def test_meld_does_not_modify_the_original_state() -> None:
    card = _card("Pottery", color=Color.RED)
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),))

    meld(state, player_index=0, card_name="Pottery")

    assert state.players[0].hand == (card,)
    assert state.players[0].board == {}


def test_meld_places_the_card_on_top_of_an_existing_pile_of_the_same_color() -> None:
    old_top = _card("OldTop", color=Color.RED)
    new_card = _card("NewTop", color=Color.RED)
    player = PlayerState(name="Ada", hand=(new_card,), board={Color.RED: Pile(cards=(old_top,))})
    state = GameState(players=(player,))

    new_state, _ = meld(state, player_index=0, card_name="NewTop")

    assert new_state.players[0].board[Color.RED].cards == (new_card, old_top)


def test_meld_preserves_the_splay_of_an_existing_pile() -> None:
    old_top = _card("OldTop", color=Color.RED)
    new_card = _card("NewTop", color=Color.RED)
    player = PlayerState(
        name="Ada",
        hand=(new_card,),
        board={Color.RED: Pile(cards=(old_top,), splay=Splay.LEFT)},
    )
    state = GameState(players=(player,))

    new_state, _ = meld(state, player_index=0, card_name="NewTop")

    assert new_state.players[0].board[Color.RED].splay is Splay.LEFT


def test_meld_creates_separate_piles_per_color() -> None:
    red_card = _card("Red", color=Color.RED)
    blue_card = _card("Blue", color=Color.BLUE)
    player = PlayerState(name="Ada", hand=(red_card, blue_card))
    state = GameState(players=(player,))

    state, _ = meld(state, player_index=0, card_name="Red")
    state, _ = meld(state, player_index=0, card_name="Blue")

    assert state.players[0].board[Color.RED].cards == (red_card,)
    assert state.players[0].board[Color.BLUE].cards == (blue_card,)


def test_meld_removes_only_the_named_card_from_hand() -> None:
    keep = _card("Keep")
    melded_card = _card("Meld")
    player = PlayerState(name="Ada", hand=(keep, melded_card))
    state = GameState(players=(player,))

    new_state, _ = meld(state, player_index=0, card_name="Meld")

    assert new_state.players[0].hand == (keep,)


def test_meld_raises_for_a_card_not_in_hand() -> None:
    player = PlayerState(name="Ada", hand=(_card("Pottery"),))
    state = GameState(players=(player,))

    with pytest.raises(ValueError, match="Currency"):
        meld(state, player_index=0, card_name="Currency")


def test_tuck_moves_the_card_from_hand_to_a_new_pile_of_its_color() -> None:
    card = _card("Pottery", color=Color.RED)
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),))

    new_state, tucked = tuck(state, player_index=0, card_name="Pottery")

    assert tucked is card
    assert new_state.players[0].hand == ()
    assert new_state.players[0].board[Color.RED].cards == (card,)


def test_tuck_places_the_card_underneath_an_existing_pile_of_the_same_color() -> None:
    old_top = _card("OldTop", color=Color.RED)
    new_card = _card("NewBottom", color=Color.RED)
    player = PlayerState(name="Ada", hand=(new_card,), board={Color.RED: Pile(cards=(old_top,))})
    state = GameState(players=(player,))

    new_state, _ = tuck(state, player_index=0, card_name="NewBottom")

    assert new_state.players[0].board[Color.RED].cards == (old_top, new_card)


def test_tuck_preserves_the_splay_of_an_existing_pile() -> None:
    old_top = _card("OldTop", color=Color.RED)
    new_card = _card("NewBottom", color=Color.RED)
    player = PlayerState(
        name="Ada",
        hand=(new_card,),
        board={Color.RED: Pile(cards=(old_top,), splay=Splay.RIGHT)},
    )
    state = GameState(players=(player,))

    new_state, _ = tuck(state, player_index=0, card_name="NewBottom")

    assert new_state.players[0].board[Color.RED].splay is Splay.RIGHT


def test_tuck_removes_only_the_named_card_from_hand() -> None:
    keep = _card("Keep")
    tucked_card = _card("Tuck")
    player = PlayerState(name="Ada", hand=(keep, tucked_card))
    state = GameState(players=(player,))

    new_state, _ = tuck(state, player_index=0, card_name="Tuck")

    assert new_state.players[0].hand == (keep,)


def test_tuck_raises_for_a_card_not_in_hand() -> None:
    player = PlayerState(name="Ada", hand=(_card("Pottery"),))
    state = GameState(players=(player,))

    with pytest.raises(ValueError, match="Currency"):
        tuck(state, player_index=0, card_name="Currency")


def test_draw_and_tuck_places_the_card_directly_onto_a_new_pile() -> None:
    card = _card("Pottery", age=1, color=Color.RED)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (card,)})

    new_state, tucked = draw_and_tuck(state, player_index=0, age=1)

    assert tucked is card
    assert new_state.players[0].hand == ()
    assert new_state.players[0].board[Color.RED].cards == (card,)
    assert new_state.supply[1] == ()


def test_draw_and_tuck_places_the_card_underneath_an_existing_pile() -> None:
    old_top = _card("OldTop", color=Color.RED)
    new_card = _card("NewBottom", age=1, color=Color.RED)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(old_top,))})
    state = GameState(players=(player,), supply={1: (new_card,)})

    new_state, _ = draw_and_tuck(state, player_index=0, age=1)

    assert new_state.players[0].board[Color.RED].cards == (old_top, new_card)


def test_draw_and_tuck_preserves_the_splay_of_an_existing_pile() -> None:
    old_top = _card("OldTop", color=Color.RED)
    new_card = _card("NewBottom", age=1, color=Color.RED)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(old_top,), splay=Splay.LEFT)})
    state = GameState(players=(player,), supply={1: (new_card,)})

    new_state, _ = draw_and_tuck(state, player_index=0, age=1)

    assert new_state.players[0].board[Color.RED].splay is Splay.LEFT


def test_draw_and_tuck_falls_back_to_the_next_age_when_the_pile_is_empty() -> None:
    card = _card("Currency", age=2)
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (), 2: (card,)})

    _, tucked = draw_and_tuck(state, player_index=0, age=1)

    assert tucked is card


def test_draw_and_tuck_raises_supply_exhausted_when_nothing_is_available() -> None:
    state = GameState(players=(PlayerState(name="Ada"),), supply={9: (), 10: ()})

    with pytest.raises(SupplyExhaustedError, match="age 9"):
        draw_and_tuck(state, player_index=0, age=9)


@pytest.mark.parametrize("age", [0, -1, 11])
def test_draw_and_tuck_rejects_an_age_outside_one_through_ten(age: int) -> None:
    state = GameState(players=(PlayerState(name="Ada"),))

    with pytest.raises(ValueError, match="age"):
        draw_and_tuck(state, player_index=0, age=age)
