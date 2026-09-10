"""Tests for game setup (src/innovation/engine/setup.py)."""

from innovation.engine.actions import answer_choice, pending_decision
from innovation.engine.setup import start_game
from innovation.model.card import Card, CardIcons
from innovation.model.enums import Color, Icon
from innovation.model.game_state import GameState
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


def test_start_game_deals_two_age_one_cards_to_each_player() -> None:
    bravo, zulu = _card("Bravo"), _card("Zulu")
    alpha, yankee = _card("Alpha"), _card("Yankee")
    state = GameState(
        players=(PlayerState(name="Ada"), PlayerState(name="Grace")),
        supply={1: (bravo, zulu, alpha, yankee)},
    )

    state = start_game(state)

    assert state.players[0].hand == (bravo, zulu)
    assert state.players[1].hand == (alpha, yankee)
    assert state.supply[1] == ()


def test_start_game_does_not_modify_the_original_state() -> None:
    state = GameState(
        players=(PlayerState(name="Ada"),),
        supply={1: (_card("Bravo"), _card("Zulu"))},
    )

    start_game(state)

    assert state.players[0].hand == ()
    assert state.supply[1] == (_card("Bravo"), _card("Zulu"))


def test_start_game_queues_an_opening_meld_choice_for_each_player_in_order() -> None:
    state = GameState(
        players=(PlayerState(name="Ada"), PlayerState(name="Grace")),
        supply={1: (_card("Bravo"), _card("Zulu"), _card("Alpha"), _card("Yankee"))},
    )

    state = start_game(state)

    decision = pending_decision(state)
    assert decision is not None
    assert decision.player_index == 0
    state = answer_choice(state, "Bravo")

    decision = pending_decision(state)
    assert decision is not None
    assert decision.player_index == 1


def test_start_game_melds_the_chosen_card_and_leaves_the_other_in_hand() -> None:
    bravo, zulu = _card("Bravo"), _card("Zulu")
    state = GameState(players=(PlayerState(name="Ada"),), supply={1: (bravo, zulu)})

    state = start_game(state)
    state = answer_choice(state, "Bravo")

    assert state.players[0].board[Color.RED].cards == (bravo,)
    assert state.players[0].hand == (zulu,)


def test_first_player_is_whoever_melded_the_lexicographically_first_card() -> None:
    bravo, zulu = _card("Bravo"), _card("Zulu")
    alpha, yankee = _card("Alpha"), _card("Yankee")
    delta, whiskey = _card("Delta"), _card("Whiskey")
    state = GameState(
        players=(PlayerState(name="Ada"), PlayerState(name="Grace"), PlayerState(name="Hedy")),
        supply={1: (bravo, zulu, alpha, yankee, delta, whiskey)},
    )

    state = start_game(state)
    state = answer_choice(state, "Bravo")
    state = answer_choice(state, "Alpha")
    state = answer_choice(state, "Delta")

    assert pending_decision(state) is None
    assert state.pending_steps == ()
    assert state.current_player_index == 1


def test_first_player_tie_goes_to_the_lower_player_index() -> None:
    echo_a, other_a = _card("Echo"), _card("Other")
    echo_b, other_b = _card("Echo"), _card("Other")
    state = GameState(
        players=(PlayerState(name="Ada"), PlayerState(name="Grace")),
        supply={1: (echo_a, other_a, echo_b, other_b)},
    )

    state = start_game(state)
    state = answer_choice(state, "Echo")
    state = answer_choice(state, "Echo")

    assert state.current_player_index == 0
