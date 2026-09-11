"""Tests for the turn loop (src/innovation/engine/game.py)."""

import pytest

from innovation.engine.actions import answer_share, pending_decision
from innovation.engine.game import (
    start_turn,
    take_achieve_action,
    take_dogma_action,
    take_draw_action,
    take_meld_action,
)
from innovation.model.card import Card, CardIcons, Dogma, DogmaEffect
from innovation.model.enums import Color, Icon
from innovation.model.game_state import GameState
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


def _card(name: str, age: int = 1, color: Color = Color.RED, icon: Icon = Icon.NONE) -> Card:
    return Card(
        name=name,
        age=age,
        color=color,
        icons=CardIcons(
            top_left=icon,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
    )


def _melded_player(name: str, card_name: str = "Opener") -> PlayerState:
    return PlayerState(name=name, board={Color.RED: Pile(cards=(_card(card_name),))})


def _card_with_dogma(name: str, effect: DogmaEffect, icon: Icon = Icon.CROWN) -> Card:
    return Card(
        name=name,
        age=1,
        color=Color.RED,
        icons=CardIcons(
            top_left=Icon.NONE,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
        dogmas=(Dogma(text="Do nothing.", icon=icon, effect=effect),),
    )


def test_start_turn_grants_one_action_on_the_very_first_turn() -> None:
    state = GameState(players=(_melded_player("Ada"), _melded_player("Grace")))

    state = start_turn(state)

    assert state.actions_remaining == 1
    assert state.first_turn_taken is True


def test_start_turn_grants_two_actions_on_a_later_turn() -> None:
    state = GameState(
        players=(_melded_player("Ada"), _melded_player("Grace")), first_turn_taken=True
    )

    state = start_turn(state)

    assert state.actions_remaining == 2


def test_start_turn_raises_when_a_turn_is_already_in_progress() -> None:
    state = GameState(players=(_melded_player("Ada"),), actions_remaining=1)

    with pytest.raises(ValueError, match="already in progress"):
        start_turn(state)


def test_start_turn_raises_when_a_decision_is_still_pending() -> None:
    def effect(state: GameState, player_index: int) -> GameState:
        return state

    active_card = _card_with_dogma("Effectful", effect)
    active = PlayerState(name="Ada", board={Color.RED: Pile(cards=(active_card,))})
    sharer = PlayerState(
        name="Grace", board={Color.YELLOW: Pile(cards=(_card("Crowned", icon=Icon.CROWN),))}
    )
    state = GameState(players=(active, sharer), actions_remaining=1, first_turn_taken=True)
    state = take_dogma_action(state, player_index=0, card_name="Effectful")
    assert state.actions_remaining == 0
    assert pending_decision(state) is not None

    with pytest.raises(ValueError, match="unresolved decision"):
        start_turn(state)


def test_take_draw_action_consumes_one_action_without_ending_the_turn() -> None:
    card = _card("Drawn")
    state = GameState(
        players=(_melded_player("Ada"), _melded_player("Grace")),
        supply={1: (card,)},
        actions_remaining=2,
        first_turn_taken=True,
    )

    state = take_draw_action(state, player_index=0)

    assert state.players[0].hand == (card,)
    assert state.actions_remaining == 1
    assert state.current_player_index == 0


def test_second_action_ends_the_turn_and_advances_to_the_next_player() -> None:
    state = GameState(
        players=(_melded_player("Ada"), _melded_player("Grace")),
        supply={1: (_card("A"), _card("B"))},
        actions_remaining=2,
        first_turn_taken=True,
    )

    state = take_draw_action(state, player_index=0)
    state = take_draw_action(state, player_index=0)

    assert state.actions_remaining == 0
    assert state.current_player_index == 1


def test_the_very_first_turn_ends_after_a_single_action() -> None:
    state = GameState(
        players=(_melded_player("Ada"), _melded_player("Grace")),
        supply={1: (_card("A"),)},
    )

    state = start_turn(state)
    state = take_draw_action(state, player_index=0)

    assert state.actions_remaining == 0
    assert state.current_player_index == 1


def test_take_meld_action_melds_the_named_card_and_consumes_an_action() -> None:
    card = _card("Pottery", color=Color.BLUE)
    player = PlayerState(
        name="Ada", hand=(card,), board={Color.RED: Pile(cards=(_card("Opener"),))}
    )
    state = GameState(players=(player,), actions_remaining=2, first_turn_taken=True)

    state = take_meld_action(state, player_index=0, card_name="Pottery")

    assert state.players[0].board[Color.BLUE].cards == (card,)
    assert state.actions_remaining == 1


def test_take_action_raises_when_it_is_not_the_given_players_turn() -> None:
    state = GameState(
        players=(_melded_player("Ada"), _melded_player("Grace")),
        actions_remaining=2,
        first_turn_taken=True,
    )

    with pytest.raises(ValueError, match="not player 1"):
        take_draw_action(state, player_index=1)


def test_take_action_raises_when_no_actions_remain() -> None:
    state = GameState(players=(_melded_player("Ada"),), actions_remaining=0, first_turn_taken=True)

    with pytest.raises(ValueError, match="no actions remaining"):
        take_draw_action(state, player_index=0)


def test_take_dogma_action_consumes_the_turn_action_even_with_sharing_still_pending() -> None:
    def effect(state: GameState, player_index: int) -> GameState:
        return state

    active_card = _card_with_dogma("Effectful", effect)
    active = PlayerState(name="Ada", board={Color.RED: Pile(cards=(active_card,))})
    sharer = PlayerState(
        name="Grace", board={Color.YELLOW: Pile(cards=(_card("Crowned", icon=Icon.CROWN),))}
    )
    state = GameState(
        players=(active, sharer), actions_remaining=1, current_player_index=0, first_turn_taken=True
    )

    state = take_dogma_action(state, player_index=0, card_name="Effectful")

    assert state.actions_remaining == 0
    assert state.current_player_index == 1
    decision = pending_decision(state)
    assert decision is not None
    assert decision.player_index == 1


def test_take_action_raises_while_a_decision_from_a_previous_action_is_pending() -> None:
    def effect(state: GameState, player_index: int) -> GameState:
        return state

    active_card = _card_with_dogma("Effectful", effect)
    active = PlayerState(name="Ada", board={Color.RED: Pile(cards=(active_card,))})
    sharer = PlayerState(
        name="Grace",
        hand=(_card("InHand"),),
        board={Color.YELLOW: Pile(cards=(_card("Crowned", icon=Icon.CROWN),))},
    )
    state = GameState(
        players=(active, sharer), actions_remaining=1, current_player_index=0, first_turn_taken=True
    )
    state = take_dogma_action(state, player_index=0, card_name="Effectful")
    assert state.current_player_index == 1

    with pytest.raises(ValueError, match="unresolved decision"):
        take_meld_action(state, player_index=1, card_name="InHand")

    # Resolving it unblocks the next player's turn.
    state = answer_share(state, share=False)
    assert pending_decision(state) is None
    state = start_turn(state)
    state = take_meld_action(state, player_index=1, card_name="InHand")
    assert state.players[1].board[Color.RED].cards[0].name == "InHand"


def test_take_achieve_action_raises_not_implemented() -> None:
    state = GameState(players=(_melded_player("Ada"),), actions_remaining=1, first_turn_taken=True)

    with pytest.raises(NotImplementedError):
        take_achieve_action(state, player_index=0)
