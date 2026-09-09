"""Tests for the Draw, Meld, Tuck, and Dogma actions (src/innovation/engine/actions.py)."""

import pytest

from innovation.engine.actions import (
    SupplyExhaustedError,
    answer_share,
    dogma,
    draw,
    draw_and_meld,
    draw_and_tuck,
    meld,
    pending_decision,
    tuck,
)
from innovation.model.card import Card, CardIcons, Dogma
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
    card_z, card_y, card_x = _card("Z"), _card("Y"), _card("X")
    state = GameState(players=(p0, p1, active, p3), supply={1: (card_z, card_y, card_x)})

    state = dogma(state, player_index=2, card_name="Effectful")

    decision = pending_decision(state)
    assert decision is not None
    assert decision.player_index == 3
    assert decision.card_name == "Effectful"

    # Player 3 shares: draws a card, then it's Player 1's turn to decide.
    state = answer_share(state, share=True)
    assert state.players[3].hand == (card_z,)
    decision = pending_decision(state)
    assert decision is not None
    assert decision.player_index == 1

    # Player 1 declines: no card for them, and the active player's own
    # effect then runs automatically (no decision needed for it).
    state = answer_share(state, share=False)
    assert state.players[1].hand == ()
    assert state.players[2].hand == (card_y,)
    assert state.supply[1] == (card_x,)
    assert pending_decision(state) is None
    assert state.pending_steps == ()
