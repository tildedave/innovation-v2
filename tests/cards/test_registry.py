"""Tests for the card registry (src/innovation/cards/registry.py)."""

import pytest

from innovation.cards.registry import (
    AGRICULTURE,
    METALWORKING,
    SAILING,
    _metalworking_dogma,
    all_cards,
    cards_of_age,
)
from innovation.engine.actions import (
    SupplyExhaustedError,
    answer_optional,
    dogma,
    pending_decision,
)
from innovation.model.card import Card, CardIcons
from innovation.model.enums import Color, Icon
from innovation.model.game_state import GameState
from innovation.model.pending import EffectStep, OptionalStep
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


def _card(name: str, age: int = 1, color: Color = Color.BLUE, icon: Icon = Icon.NONE) -> Card:
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


def test_sailings_dogma_draws_and_melds_a_card_of_age_one() -> None:
    drawn_card = _card("Pottery", color=Color.BLUE)
    player = PlayerState(name="Ada", board={Color.GREEN: Pile(cards=(SAILING,))})
    state = GameState(players=(player,), supply={1: (drawn_card,)})

    new_state = dogma(state, player_index=0, card_name="Sailing")

    assert new_state.players[0].board[Color.BLUE].cards == (drawn_card,)


def test_sailings_dogma_falls_back_to_a_higher_age_when_the_one_pile_is_empty() -> None:
    drawn_card = _card("Currency", age=2, color=Color.BLUE)
    player = PlayerState(name="Ada", board={Color.GREEN: Pile(cards=(SAILING,))})
    state = GameState(players=(player,), supply={1: (), 2: (drawn_card,)})

    new_state = dogma(state, player_index=0, card_name="Sailing")

    assert new_state.players[0].board[Color.BLUE].cards == (drawn_card,)


def test_metalworking_is_a_red_age_one_card() -> None:
    assert METALWORKING.age == 1
    assert METALWORKING.color == Color.RED


def test_metalworking_icons() -> None:
    assert METALWORKING.icons.top_left == Icon.CASTLE
    assert METALWORKING.icons.bottom_left == Icon.CASTLE
    assert METALWORKING.icons.bottom_center == Icon.NONE
    assert METALWORKING.icons.bottom_right == Icon.CASTLE


def test_metalworking_has_one_castle_dogma_with_an_implemented_effect() -> None:
    assert len(METALWORKING.dogmas) == 1
    assert METALWORKING.dogmas[0].icon == Icon.CASTLE
    assert METALWORKING.dogmas[0].effect is not None


def test_all_cards_and_cards_of_age_include_every_registered_card() -> None:
    assert all_cards() == [SAILING, METALWORKING, AGRICULTURE]
    assert cards_of_age(1) == [SAILING, METALWORKING, AGRICULTURE]
    assert cards_of_age(2) == []


def test_metalworkings_dogma_keeps_a_non_castle_card_in_hand_and_stops() -> None:
    plain_card = _card("Plain", icon=Icon.NONE)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(METALWORKING,))})
    state = GameState(players=(player,), supply={1: (plain_card,)})

    new_state = dogma(state, player_index=0, card_name="Metalworking")

    assert new_state.players[0].hand == (plain_card,)
    assert new_state.players[0].score_pile == ()


def test_metalworkings_dogma_scores_a_castle_card_and_repeats() -> None:
    castle_card = _card("CastleCard", icon=Icon.CASTLE)
    plain_card = _card("Plain", icon=Icon.NONE)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(METALWORKING,))})
    state = GameState(players=(player,), supply={1: (castle_card, plain_card)})

    new_state = dogma(state, player_index=0, card_name="Metalworking")

    assert new_state.players[0].score_pile == (castle_card,)
    assert new_state.players[0].hand == (plain_card,)
    assert new_state.supply[1] == ()


def test_metalworkings_dogma_chains_through_multiple_castle_cards() -> None:
    castle_a = _card("CastleA", icon=Icon.CASTLE)
    castle_b = _card("CastleB", icon=Icon.CASTLE)
    plain_card = _card("Plain", icon=Icon.NONE)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(METALWORKING,))})
    state = GameState(players=(player,), supply={1: (castle_a, castle_b, plain_card)})

    new_state = dogma(state, player_index=0, card_name="Metalworking")

    assert new_state.players[0].score_pile == (castle_a, castle_b)
    assert new_state.players[0].hand == (plain_card,)


def test_metalworkings_dogma_stops_if_the_supply_runs_out_while_scoring() -> None:
    castle_card = _card("CastleCard", icon=Icon.CASTLE)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(METALWORKING,))})
    state = GameState(players=(player,), supply={1: (castle_card,)})

    with pytest.raises(SupplyExhaustedError):
        dogma(state, player_index=0, card_name="Metalworking")


def test_metalworkings_dogma_effect_requeues_itself_rather_than_looping() -> None:
    """Calls the effect function directly (bypassing engine.actions._advance,
    which auto-drains the whole queue) to prove one call does exactly one
    draw/score and defers any repeat to a newly queued EffectStep, rather
    than looping through the whole chain internally.
    """
    castle_a = _card("CastleA", icon=Icon.CASTLE)
    castle_b = _card("CastleB", icon=Icon.CASTLE)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(METALWORKING,))})
    state = GameState(players=(player,), supply={1: (castle_a, castle_b)})

    new_state = _metalworking_dogma(state, player_index=0)

    # Only the first card was drawn and scored -- the second is still
    # untouched in the supply, deferred to the queued repeat step.
    assert new_state.players[0].score_pile == (castle_a,)
    assert new_state.supply[1] == (castle_b,)
    assert len(new_state.pending_steps) == 1
    requeued = new_state.pending_steps[0]
    assert isinstance(requeued, EffectStep)
    assert requeued.player_index == 0
    assert requeued.effect is _metalworking_dogma


def test_metalworkings_dogma_effect_does_not_requeue_when_it_does_not_score() -> None:
    plain_card = _card("Plain", icon=Icon.NONE)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(METALWORKING,))})
    state = GameState(players=(player,), supply={1: (plain_card,)})

    new_state = _metalworking_dogma(state, player_index=0)

    assert new_state.pending_steps == ()


def test_agriculture_is_a_yellow_age_one_card() -> None:
    assert AGRICULTURE.age == 1
    assert AGRICULTURE.color == Color.YELLOW


def test_agriculture_icons() -> None:
    assert AGRICULTURE.icons.top_left == Icon.NONE
    assert AGRICULTURE.icons.bottom_left == Icon.LEAF
    assert AGRICULTURE.icons.bottom_center == Icon.LEAF
    assert AGRICULTURE.icons.bottom_right == Icon.LEAF


def test_agriculture_has_one_leaf_dogma_with_an_implemented_effect() -> None:
    assert len(AGRICULTURE.dogmas) == 1
    assert AGRICULTURE.dogmas[0].icon == Icon.LEAF
    assert AGRICULTURE.dogmas[0].effect is not None


def test_agricultures_dogma_pauses_on_a_return_decision() -> None:
    player = PlayerState(name="Ada", board={Color.YELLOW: Pile(cards=(AGRICULTURE,))})
    state = GameState(players=(player,))

    new_state = dogma(state, player_index=0, card_name="Agriculture")

    decision = pending_decision(new_state)
    assert isinstance(decision, OptionalStep)
    assert decision.player_index == 0
    assert decision.card_name == "Agriculture"


def test_agricultures_dogma_declining_does_nothing_further() -> None:
    hand_card = _card("KeepMe", age=2)
    bonus_card = _card("Bonus", age=3)
    player = PlayerState(
        name="Ada", hand=(hand_card,), board={Color.YELLOW: Pile(cards=(AGRICULTURE,))}
    )
    state = GameState(players=(player,), supply={2: (), 3: (bonus_card,)})

    state = dogma(state, player_index=0, card_name="Agriculture")
    state = answer_optional(state, card_name=None)

    assert state.players[0].hand == (hand_card,)
    assert state.players[0].score_pile == ()
    assert state.supply[3] == (bonus_card,)
    assert pending_decision(state) is None
    assert state.pending_steps == ()


def test_agricultures_dogma_returning_a_card_draws_and_scores_one_higher() -> None:
    returned_card = _card("ReturnMe", age=2)
    bonus_card = _card("Bonus", age=3)
    player = PlayerState(
        name="Ada", hand=(returned_card,), board={Color.YELLOW: Pile(cards=(AGRICULTURE,))}
    )
    state = GameState(players=(player,), supply={2: (), 3: (bonus_card,)})

    state = dogma(state, player_index=0, card_name="Agriculture")
    state = answer_optional(state, card_name="ReturnMe")

    assert state.players[0].hand == ()
    assert state.players[0].score_pile == (bonus_card,)
    assert state.supply[2] == (returned_card,)
    assert state.supply[3] == ()
    assert pending_decision(state) is None


def test_agricultures_dogma_scales_the_draw_age_with_the_returned_cards_age() -> None:
    returned_card = _card("ReturnMe", age=5)
    bonus_card = _card("Bonus", age=6)
    player = PlayerState(
        name="Ada", hand=(returned_card,), board={Color.YELLOW: Pile(cards=(AGRICULTURE,))}
    )
    state = GameState(players=(player,), supply={5: (), 6: (bonus_card,)})

    state = dogma(state, player_index=0, card_name="Agriculture")
    state = answer_optional(state, card_name="ReturnMe")

    assert state.players[0].score_pile == (bonus_card,)


def test_agricultures_dogma_return_raises_for_a_card_not_in_hand() -> None:
    player = PlayerState(name="Ada", board={Color.YELLOW: Pile(cards=(AGRICULTURE,))})
    state = GameState(players=(player,))

    state = dogma(state, player_index=0, card_name="Agriculture")

    with pytest.raises(ValueError, match="NotInHand"):
        answer_optional(state, card_name="NotInHand")
