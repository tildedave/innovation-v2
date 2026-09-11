"""Tests for the Draw, Meld, Tuck, and Dogma actions (src/innovation/engine/actions.py)."""

from dataclasses import replace

import pytest

from innovation.engine.actions import (
    SupplyExhaustedError,
    achieve,
    answer_optional,
    answer_share,
    dogma,
    draw,
    draw_and_meld,
    draw_and_tuck,
    meld,
    pending_decision,
    return_card,
    reveal,
    score,
    score_pile_value,
    tuck,
)
from innovation.model.card import Card, CardIcons, Dogma
from innovation.model.enums import Color, Icon, Splay, Zone
from innovation.model.game_state import GameState
from innovation.model.pending import OptionalStep, ShareStep
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


def test_score_moves_the_card_from_hand_to_the_score_pile() -> None:
    card = _card("Pottery")
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),))

    new_state, scored = score(state, player_index=0, card_name="Pottery")

    assert scored is card
    assert new_state.players[0].hand == ()
    assert new_state.players[0].score_pile == (card,)


def test_score_does_not_modify_the_original_state() -> None:
    card = _card("Pottery")
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),))

    score(state, player_index=0, card_name="Pottery")

    assert state.players[0].hand == (card,)
    assert state.players[0].score_pile == ()


def test_score_appends_after_existing_scored_cards() -> None:
    already_scored = _card("Already")
    new_card = _card("New")
    player = PlayerState(name="Ada", hand=(new_card,), score_pile=(already_scored,))
    state = GameState(players=(player,))

    new_state, _ = score(state, player_index=0, card_name="New")

    assert new_state.players[0].score_pile == (already_scored, new_card)


def test_score_removes_only_the_named_card_from_hand() -> None:
    keep = _card("Keep")
    scored_card = _card("Score")
    player = PlayerState(name="Ada", hand=(keep, scored_card))
    state = GameState(players=(player,))

    new_state, _ = score(state, player_index=0, card_name="Score")

    assert new_state.players[0].hand == (keep,)


def test_score_raises_for_a_card_not_in_hand() -> None:
    player = PlayerState(name="Ada", hand=(_card("Pottery"),))
    state = GameState(players=(player,))

    with pytest.raises(ValueError, match="Currency"):
        score(state, player_index=0, card_name="Currency")


def test_return_card_moves_the_card_from_hand_to_the_bottom_of_its_age_supply_pile() -> None:
    card = _card("Pottery", age=2)
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),), supply={2: ()})

    new_state, returned = return_card(state, player_index=0, card_name="Pottery")

    assert returned is card
    assert new_state.players[0].hand == ()
    assert new_state.supply[2] == (card,)


def test_return_card_does_not_modify_the_original_state() -> None:
    card = _card("Pottery", age=2)
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),), supply={2: ()})

    return_card(state, player_index=0, card_name="Pottery")

    assert state.players[0].hand == (card,)
    assert state.supply[2] == ()


def test_return_card_appends_after_existing_cards_of_that_age() -> None:
    already_there = _card("AlreadyThere", age=2)
    returned_card = _card("Returned", age=2)
    player = PlayerState(name="Ada", hand=(returned_card,))
    state = GameState(players=(player,), supply={2: (already_there,)})

    new_state, _ = return_card(state, player_index=0, card_name="Returned")

    assert new_state.supply[2] == (already_there, returned_card)


def test_return_card_creates_a_new_supply_entry_if_none_existed_for_that_age() -> None:
    card = _card("Pottery", age=3)
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),))

    new_state, _ = return_card(state, player_index=0, card_name="Pottery")

    assert new_state.supply[3] == (card,)


def test_return_card_removes_only_the_named_card_from_hand() -> None:
    keep = _card("Keep")
    returned_card = _card("Return")
    player = PlayerState(name="Ada", hand=(keep, returned_card))
    state = GameState(players=(player,), supply={1: ()})

    new_state, _ = return_card(state, player_index=0, card_name="Return")

    assert new_state.players[0].hand == (keep,)


def test_return_card_raises_for_a_card_not_in_hand() -> None:
    player = PlayerState(name="Ada", hand=(_card("Pottery"),))
    state = GameState(players=(player,))

    with pytest.raises(ValueError, match="Currency"):
        return_card(state, player_index=0, card_name="Currency")


@pytest.mark.parametrize("zone", list(Zone))
def test_reveal_is_a_no_op_regardless_of_zone(zone: Zone) -> None:
    card = _card("Pottery")
    state = GameState(players=(PlayerState(name="Ada", hand=(card,)),))

    new_state = reveal(state, player_index=0, card=card, zone=zone)

    assert new_state == state


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


def _card_with_dogmas(name: str, *dogmas: Dogma, color: Color = Color.RED) -> Card:
    return Card(
        name=name,
        age=1,
        color=color,
        icons=CardIcons(
            top_left=Icon.NONE,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
        dogmas=dogmas,
    )


def test_dogma_applies_the_named_cards_effect_for_the_acting_player() -> None:
    def draw_two_ones(state: GameState, player_index: int) -> GameState:
        state, _ = draw(state, player_index, age=1)
        state, _ = draw(state, player_index, age=1)
        return state

    active_card = _card_with_dogmas(
        "Effectful", Dogma(text="Draw two 1s.", icon=Icon.CROWN, effect=draw_two_ones)
    )
    card_a = _card("A", age=1)
    card_b = _card("B", age=1)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(active_card,))})
    state = GameState(players=(player,), supply={1: (card_a, card_b)})

    new_state = dogma(state, player_index=0, card_name="Effectful")

    assert new_state.players[0].hand == (card_a, card_b)


def test_dogma_does_not_modify_the_original_state() -> None:
    def draw_one(state: GameState, player_index: int) -> GameState:
        state, _ = draw(state, player_index, age=1)
        return state

    active_card = _card_with_dogmas(
        "Effectful", Dogma(text="Draw a 1.", icon=Icon.CROWN, effect=draw_one)
    )
    card_a = _card("A", age=1)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(active_card,))})
    state = GameState(players=(player,), supply={1: (card_a,)})

    dogma(state, player_index=0, card_name="Effectful")

    assert state.players[0].hand == ()
    assert state.supply[1] == (card_a,)


def test_dogma_applies_multiple_dogma_effects_in_order() -> None:
    calls: list[str] = []

    def first_effect(state: GameState, player_index: int) -> GameState:
        calls.append("first")
        return state

    def second_effect(state: GameState, player_index: int) -> GameState:
        calls.append("second")
        return state

    active_card = _card_with_dogmas(
        "TwoEffects",
        Dogma(text="First.", icon=Icon.CROWN, effect=first_effect),
        Dogma(text="Second.", icon=Icon.LEAF, effect=second_effect),
    )
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(active_card,))})
    state = GameState(players=(player,))

    dogma(state, player_index=0, card_name="TwoEffects")

    assert calls == ["first", "second"]


def test_dogma_raises_for_a_card_not_on_the_board() -> None:
    state = GameState(players=(PlayerState(name="Ada"),))

    with pytest.raises(ValueError, match="Sailing"):
        dogma(state, player_index=0, card_name="Sailing")


def test_dogma_raises_for_a_card_not_on_top_of_its_pile() -> None:
    covered = _card("Covered", color=Color.RED)
    top = _card("Top", color=Color.RED)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(top, covered))})
    state = GameState(players=(player,))

    with pytest.raises(ValueError, match="Covered"):
        dogma(state, player_index=0, card_name="Covered")


def test_dogma_raises_not_implemented_for_a_dogma_without_an_effect() -> None:
    active_card = _card_with_dogmas(
        "NoEffectYet", Dogma(text="Some text, no behavior yet.", icon=Icon.CROWN)
    )
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=(active_card,))})
    state = GameState(players=(player,))

    with pytest.raises(NotImplementedError, match="NoEffectYet"):
        dogma(state, player_index=0, card_name="NoEffectYet")


def _card_with_icon(name: str, icon: Icon, color: Color = Color.RED) -> Card:
    return Card(
        name=name,
        age=1,
        color=color,
        icons=CardIcons(
            top_left=icon,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
    )


def _crown_pile(name: str, color: Color) -> Pile:
    return Pile(cards=(_card_with_icon(f"{name}-crown", Icon.CROWN, color=color),))


def test_pending_decision_is_none_by_default() -> None:
    state = GameState(players=(PlayerState(name="Ada"),))

    assert pending_decision(state) is None


def test_answer_share_raises_when_nothing_is_pending() -> None:
    state = GameState(players=(PlayerState(name="Ada"),))

    with pytest.raises(ValueError, match="no pending share decision"):
        answer_share(state, share=True)


def test_answer_optional_raises_when_nothing_is_pending() -> None:
    state = GameState(players=(PlayerState(name="Ada"),))

    with pytest.raises(ValueError, match="no pending optional decision"):
        answer_optional(state, card_name=None)


def test_answer_share_raises_when_an_optional_decision_is_pending() -> None:
    def if_done(state: GameState, player_index: int, acted_on: Card) -> GameState:
        return state

    optional_step = OptionalStep(
        player_index=0, card_name="Agriculture", action=return_card, if_done=if_done
    )
    state = GameState(players=(PlayerState(name="Ada"),), pending_steps=(optional_step,))

    with pytest.raises(ValueError, match="no pending share decision"):
        answer_share(state, share=True)


def test_answer_optional_raises_when_a_share_decision_is_pending() -> None:
    def effect(state: GameState, player_index: int) -> GameState:
        return state

    share_step = ShareStep(
        player_index=0, active_player_index=0, card_name="Sailing", effect=effect
    )
    state = GameState(players=(PlayerState(name="Ada"),), pending_steps=(share_step,))

    with pytest.raises(ValueError, match="no pending optional decision"):
        answer_optional(state, card_name=None)


def test_answer_optional_runs_validate_before_the_action() -> None:
    calls: list[str] = []

    def validate(state: GameState, player_index: int, card_name: str) -> None:
        calls.append("validate")

    def action(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
        calls.append("action")
        return score(state, player_index, card_name)

    def if_done(state: GameState, player_index: int, acted_on: Card) -> GameState:
        calls.append("if_done")
        return state

    card = _card("Pottery")
    player = PlayerState(name="Ada", hand=(card,))
    optional_step = OptionalStep(
        player_index=0, card_name="Test", action=action, if_done=if_done, validate=validate
    )
    state = GameState(players=(player,), pending_steps=(optional_step,))

    answer_optional(state, card_name="Pottery")

    assert calls == ["validate", "action", "if_done"]


def test_answer_optional_rejects_an_invalid_choice_before_acting() -> None:
    def validate(state: GameState, player_index: int, card_name: str) -> None:
        raise ValueError(f"{card_name!r} is not a legal choice")

    def action(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
        return score(state, player_index, card_name)

    def if_done(state: GameState, player_index: int, acted_on: Card) -> GameState:
        return state

    card = _card("Pottery")
    player = PlayerState(name="Ada", hand=(card,))
    optional_step = OptionalStep(
        player_index=0, card_name="Test", action=action, if_done=if_done, validate=validate
    )
    state = GameState(players=(player,), pending_steps=(optional_step,))

    with pytest.raises(ValueError, match="not a legal choice"):
        answer_optional(state, card_name="Pottery")

    # Nothing happened -- the original state is untouched (raising means
    # answer_optional never returns a new one).
    assert pending_decision(state) is optional_step
    assert state.players[0].hand == (card,)


def test_answer_optional_does_not_run_validate_on_decline() -> None:
    calls: list[str] = []

    def validate(state: GameState, player_index: int, card_name: str) -> None:
        calls.append("validate")

    def action(state: GameState, player_index: int, card_name: str) -> tuple[GameState, Card]:
        return score(state, player_index, card_name)

    def if_done(state: GameState, player_index: int, acted_on: Card) -> GameState:
        return state

    def if_declined(state: GameState, player_index: int) -> GameState:
        calls.append("declined")
        return state

    optional_step = OptionalStep(
        player_index=0,
        card_name="Test",
        action=action,
        if_done=if_done,
        if_declined=if_declined,
        validate=validate,
    )
    state = GameState(players=(PlayerState(name="Ada"),), pending_steps=(optional_step,))

    answer_optional(state, card_name=None)

    assert calls == ["declined"]


def test_dogma_full_sharing_flow_matches_turn_order_and_resolves_in_order() -> None:
    """Reproduces the example flow: player 2 activates a Crown dogma,
    players 3 and 1 are eligible (in that turn order), player 0 is not.
    """

    def draw_one(state: GameState, player_index: int) -> GameState:
        state, _ = draw(state, player_index, age=1)
        return state

    active_card = _card_with_dogmas(
        "Effectful", Dogma(text="Draw a 1.", icon=Icon.CROWN, effect=draw_one)
    )
    p0 = PlayerState(name="P0")  # no crowns -- not eligible
    p1 = PlayerState(name="P1", board={Color.YELLOW: _crown_pile("P1", Color.YELLOW)})
    active = PlayerState(
        name="Active",
        board={
            Color.RED: Pile(cards=(active_card,)),
            Color.GREEN: _crown_pile("Active", Color.GREEN),
        },
    )
    p3 = PlayerState(
        name="P3",
        board={
            Color.YELLOW: _crown_pile("P3a", Color.YELLOW),
            Color.BLUE: _crown_pile("P3b", Color.BLUE),
        },
    )
    card_z, card_y, card_x, card_w = _card("Z"), _card("Y"), _card("X"), _card("W")
    state = GameState(players=(p0, p1, active, p3), supply={1: (card_z, card_y, card_x, card_w)})

    state = dogma(state, player_index=2, card_name="Effectful")

    decision = pending_decision(state)
    assert decision is not None
    assert decision.player_index == 3
    assert decision.card_name == "Effectful"

    # Player 3 shares: eligibility for the whole round is already
    # settled, so this only records their opt-in -- nothing has drawn
    # yet, since Player 1 still hasn't been asked. Sharing does queue a
    # bonus draw for the active player, at the end.
    state = answer_share(state, share=True)
    assert state.players[3].hand == ()
    decision = pending_decision(state)
    assert decision is not None
    assert decision.player_index == 1

    # Player 1 declines. With every eligible player now asked, the
    # queued effects finally run: Player 3's shared copy first (in turn
    # order), then the active player's own, then the queued bonus draw
    # -- two cards for the active player, since their highest top-card
    # age (1) matches the dogma's own draw age.
    state = answer_share(state, share=False)
    assert state.players[1].hand == ()
    assert state.players[3].hand == (card_z,)
    assert state.players[2].hand == (card_y, card_x)
    assert state.supply[1] == (card_w,)
    assert pending_decision(state) is None
    assert state.pending_steps == ()


def test_no_effect_runs_until_every_eligible_player_has_answered() -> None:
    """Sharing is a two-phase process: eligibility and opt-in decisions
    for *every* eligible player come first, and only once all of them
    have answered does anyone's effect (sharers' or the active
    player's) actually run -- not interleaved one decision at a time.
    """
    calls: list[int] = []

    def record_and_draw(state: GameState, player_index: int) -> GameState:
        calls.append(player_index)
        state, _ = draw(state, player_index, age=1)
        return state

    active_card = _card_with_dogmas(
        "Effectful", Dogma(text="Draw a 1.", icon=Icon.CROWN, effect=record_and_draw)
    )
    active = PlayerState(name="Active", board={Color.RED: Pile(cards=(active_card,))})
    sharer_a = PlayerState(name="A", board={Color.YELLOW: _crown_pile("A", Color.YELLOW)})
    sharer_b = PlayerState(name="B", board={Color.GREEN: _crown_pile("B", Color.GREEN)})
    state = GameState(
        players=(active, sharer_a, sharer_b),
        supply={1: tuple(_card(f"Card{i}") for i in range(4))},
    )

    state = dogma(state, player_index=0, card_name="Effectful")
    assert pending_decision(state).player_index == 1

    # First sharer says yes -- nothing has run yet, including for them.
    state = answer_share(state, share=True)
    assert calls == []
    assert pending_decision(state).player_index == 2

    # Second (last) sharer says yes -- only now does everything run, in
    # turn order (both sharers, then the active player).
    state = answer_share(state, share=True)
    assert calls == [1, 2, 0]
    assert pending_decision(state) is None


def _noop(state: GameState, player_index: int) -> GameState:
    return state


def test_a_share_queues_one_bonus_draw_at_the_active_players_highest_top_card_age() -> None:
    low_card = _card("Low", age=1)
    high_card = _card("High", age=3)
    active_card = _card_with_dogmas(
        "Effectful", Dogma(text="Do nothing.", icon=Icon.CROWN, effect=_noop)
    )
    active = PlayerState(
        name="Active",
        board={
            Color.RED: Pile(cards=(active_card,)),
            Color.GREEN: Pile(cards=(low_card,)),
            Color.BLUE: Pile(cards=(high_card,)),
        },
    )
    sharer = PlayerState(name="Sharer", board={Color.YELLOW: _crown_pile("Sharer", Color.YELLOW)})
    bonus_card = _card("Bonus", age=3)
    state = GameState(players=(active, sharer), supply={3: (bonus_card,)})

    state = dogma(state, player_index=0, card_name="Effectful")
    state = answer_share(state, share=True)

    assert state.players[0].hand == (bonus_card,)
    assert state.supply[3] == ()
    assert pending_decision(state) is None
    assert state.pending_steps == ()


def test_declining_a_share_does_not_queue_a_bonus_draw() -> None:
    active_card = _card_with_dogmas(
        "Effectful", Dogma(text="Do nothing.", icon=Icon.CROWN, effect=_noop)
    )
    active = PlayerState(name="Active", board={Color.RED: Pile(cards=(active_card,))})
    sharer = PlayerState(name="Sharer", board={Color.YELLOW: _crown_pile("Sharer", Color.YELLOW)})
    state = GameState(players=(active, sharer), supply={1: (_card("Unused"),)})

    state = dogma(state, player_index=0, card_name="Effectful")
    state = answer_share(state, share=False)

    assert state.players[0].hand == ()
    assert state.supply[1] == (_card("Unused"),)


def test_score_pile_value_sums_the_ages_of_scored_cards() -> None:
    player = PlayerState(name="Ada", score_pile=(_card("A", age=1), _card("B", age=3)))

    assert score_pile_value(player) == 4


def test_score_pile_value_is_zero_for_an_empty_score_pile() -> None:
    assert score_pile_value(PlayerState(name="Ada")) == 0


def _qualifying_player(name: str, age: int, achievements: tuple[Card, ...] = ()) -> PlayerState:
    """A player with a top card and score pile just barely enough to
    achieve the given age (a top card of that age, and a score pile
    totaling exactly 5x it)."""
    top_card = _card(f"{name}-top", age=age, color=Color.RED)
    score_cards = tuple(_card(f"{name}-score{i}", age=age) for i in range(5))
    return PlayerState(
        name=name,
        board={Color.RED: Pile(cards=(top_card,))},
        score_pile=score_cards,
        achievements=achievements,
    )


def test_achieve_claims_the_matching_achievement() -> None:
    achievement = _card("Achievement", age=1)
    player = _qualifying_player("Ada", age=1)
    state = GameState(players=(player,), achievements_available=(achievement,))

    new_state, claimed = achieve(state, player_index=0, age=1)

    assert claimed is achievement
    assert new_state.players[0].achievements == (achievement,)
    assert new_state.achievements_available == ()


def test_achieve_does_not_modify_the_original_state() -> None:
    achievement = _card("Achievement", age=1)
    player = _qualifying_player("Ada", age=1)
    state = GameState(players=(player,), achievements_available=(achievement,))

    achieve(state, player_index=0, age=1)

    assert state.players[0].achievements == ()
    assert state.achievements_available == (achievement,)


def test_achieve_only_removes_the_matching_achievement() -> None:
    achievement_1 = _card("Achievement1", age=1)
    achievement_2 = _card("Achievement2", age=2)
    player = _qualifying_player("Ada", age=2)
    state = GameState(players=(player,), achievements_available=(achievement_1, achievement_2))

    new_state, claimed = achieve(state, player_index=0, age=2)

    assert claimed is achievement_2
    assert new_state.achievements_available == (achievement_1,)


def test_achieve_appends_after_existing_achievements() -> None:
    already_claimed = _card("Already", age=1)
    achievement = _card("Achievement", age=2)
    player = _qualifying_player("Ada", age=2, achievements=(already_claimed,))
    state = GameState(players=(player,), achievements_available=(achievement,))

    new_state, _ = achieve(state, player_index=0, age=2)

    assert new_state.players[0].achievements == (already_claimed, achievement)


def test_achieve_raises_when_no_achievement_is_available_for_that_age() -> None:
    player = _qualifying_player("Ada", age=1)
    state = GameState(players=(player,), achievements_available=())

    with pytest.raises(ValueError, match="age 1"):
        achieve(state, player_index=0, age=1)


def test_achieve_raises_when_the_achievement_was_already_claimed_by_someone_else() -> None:
    achievement = _card("Achievement", age=1)
    claimant = replace(_qualifying_player("Claimant", age=1), achievements=(achievement,))
    hopeful = _qualifying_player("Ada", age=1)
    state = GameState(players=(claimant, hopeful), achievements_available=())

    with pytest.raises(ValueError, match="age 1"):
        achieve(state, player_index=1, age=1)


def test_achieve_raises_when_the_score_pile_total_is_below_five_times_the_age() -> None:
    achievement = _card("Achievement", age=2)
    top_card = _card("Top", age=2, color=Color.RED)
    player = PlayerState(
        name="Ada",
        board={Color.RED: Pile(cards=(top_card,))},
        score_pile=(_card("S", age=2),),  # value 2, needs 10
    )
    state = GameState(players=(player,), achievements_available=(achievement,))

    with pytest.raises(ValueError, match="score pile"):
        achieve(state, player_index=0, age=2)


def test_achieve_raises_when_no_top_card_meets_the_achievements_age() -> None:
    achievement = _card("Achievement", age=2)
    top_card = _card("Top", age=1, color=Color.RED)
    score_cards = tuple(_card(f"S{i}", age=2) for i in range(5))
    player = PlayerState(
        name="Ada", board={Color.RED: Pile(cards=(top_card,))}, score_pile=score_cards
    )
    state = GameState(players=(player,), achievements_available=(achievement,))

    with pytest.raises(ValueError, match="top card"):
        achieve(state, player_index=0, age=2)


def test_achieve_raises_when_the_player_has_no_top_cards_at_all() -> None:
    achievement = _card("Achievement", age=1)
    score_cards = tuple(_card(f"S{i}", age=1) for i in range(5))
    player = PlayerState(name="Ada", score_pile=score_cards)
    state = GameState(players=(player,), achievements_available=(achievement,))

    with pytest.raises(ValueError, match="top card"):
        achieve(state, player_index=0, age=1)


def test_multiple_shares_only_queue_a_single_bonus_draw() -> None:
    active_card = _card_with_dogmas(
        "Effectful", Dogma(text="Do nothing.", icon=Icon.CROWN, effect=_noop)
    )
    active = PlayerState(name="Active", board={Color.RED: Pile(cards=(active_card,))})
    sharer_a = PlayerState(name="A", board={Color.YELLOW: _crown_pile("A", Color.YELLOW)})
    sharer_b = PlayerState(name="B", board={Color.GREEN: _crown_pile("B", Color.GREEN)})
    bonus_card = _card("Bonus", age=1)
    state = GameState(players=(active, sharer_a, sharer_b), supply={1: (bonus_card,)})

    state = dogma(state, player_index=0, card_name="Effectful")
    state = answer_share(state, share=True)
    assert pending_decision(state) is not None  # second sharer still needs to decide

    state = answer_share(state, share=True)

    assert state.players[0].hand == (bonus_card,)
    assert state.supply[1] == ()
