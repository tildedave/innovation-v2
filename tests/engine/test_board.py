"""Tests for splaying and icon counting (src/innovation/engine/board.py)."""

import pytest

from innovation.engine.board import count_icons, splay_left, splay_right, splay_up
from innovation.model.card import Card, CardIcons
from innovation.model.enums import Color, Icon, Splay
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


def _card(
    name: str, top_left: Icon, bottom_left: Icon, bottom_center: Icon, bottom_right: Icon
) -> Card:
    return Card(
        name=name,
        age=1,
        color=Color.RED,
        icons=CardIcons(
            top_left=top_left,
            bottom_left=bottom_left,
            bottom_center=bottom_center,
            bottom_right=bottom_right,
        ),
    )


def test_unsplayed_pile_only_counts_top_card_icons() -> None:
    top = _card("Top", Icon.CROWN, Icon.CROWN, Icon.CROWN, Icon.CROWN)
    covered = _card("Covered", Icon.LEAF, Icon.LEAF, Icon.LEAF, Icon.LEAF)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=[top, covered])})

    assert count_icons(player, Icon.CROWN) == 4
    assert count_icons(player, Icon.LEAF) == 0


def test_splay_left_exposes_only_bottom_right_icon_of_covered_cards() -> None:
    top = _card("Top", Icon.CROWN, Icon.CROWN, Icon.CROWN, Icon.CROWN)
    covered = _card("Covered", Icon.LEAF, Icon.LEAF, Icon.LEAF, Icon.FACTORY)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=[top, covered])})

    splay_left(player, Color.RED)

    assert player.board[Color.RED].splay is Splay.LEFT
    assert count_icons(player, Icon.FACTORY) == 1
    assert count_icons(player, Icon.LEAF) == 0
    assert count_icons(player, Icon.CROWN) == 4


def test_splay_left_counts_bottom_right_icon_of_every_covered_card() -> None:
    top = _card("Top", Icon.NONE, Icon.NONE, Icon.NONE, Icon.NONE)
    covered_a = _card("A", Icon.NONE, Icon.NONE, Icon.NONE, Icon.BULB)
    covered_b = _card("B", Icon.NONE, Icon.NONE, Icon.NONE, Icon.BULB)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=[top, covered_a, covered_b])})

    splay_left(player, Color.RED)

    assert count_icons(player, Icon.BULB) == 2


def test_splay_right_exposes_top_left_and_bottom_left_icons_of_covered_cards() -> None:
    top = _card("Top", Icon.CROWN, Icon.CROWN, Icon.CROWN, Icon.CROWN)
    covered = _card("Covered", Icon.FACTORY, Icon.BULB, Icon.LEAF, Icon.LEAF)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=[top, covered])})

    splay_right(player, Color.RED)

    assert player.board[Color.RED].splay is Splay.RIGHT
    assert count_icons(player, Icon.FACTORY) == 1
    assert count_icons(player, Icon.BULB) == 1
    assert count_icons(player, Icon.LEAF) == 0
    assert count_icons(player, Icon.CROWN) == 4


def test_splay_right_counts_left_column_icons_of_every_covered_card() -> None:
    top = _card("Top", Icon.NONE, Icon.NONE, Icon.NONE, Icon.NONE)
    covered_a = _card("A", Icon.BULB, Icon.NONE, Icon.NONE, Icon.NONE)
    covered_b = _card("B", Icon.NONE, Icon.BULB, Icon.NONE, Icon.NONE)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=[top, covered_a, covered_b])})

    splay_right(player, Color.RED)

    assert count_icons(player, Icon.BULB) == 2


def test_splay_right_raises_for_a_color_with_no_pile() -> None:
    player = PlayerState(name="Ada")

    with pytest.raises(ValueError, match="RED"):
        splay_right(player, Color.RED)


def test_splay_right_raises_for_an_empty_pile() -> None:
    player = PlayerState(name="Ada", board={Color.RED: Pile()})

    with pytest.raises(ValueError, match="RED"):
        splay_right(player, Color.RED)


def test_splay_up_exposes_every_icon_except_top_left_of_covered_cards() -> None:
    top = _card("Top", Icon.CROWN, Icon.CROWN, Icon.CROWN, Icon.CROWN)
    covered = _card("Covered", Icon.CASTLE, Icon.BULB, Icon.FACTORY, Icon.LEAF)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=[top, covered])})

    splay_up(player, Color.RED)

    assert player.board[Color.RED].splay is Splay.UP
    assert count_icons(player, Icon.CASTLE) == 0
    assert count_icons(player, Icon.BULB) == 1
    assert count_icons(player, Icon.FACTORY) == 1
    assert count_icons(player, Icon.LEAF) == 1
    assert count_icons(player, Icon.CROWN) == 4


def test_splay_up_counts_bottom_row_icons_of_every_covered_card() -> None:
    top = _card("Top", Icon.NONE, Icon.NONE, Icon.NONE, Icon.NONE)
    covered_a = _card("A", Icon.NONE, Icon.BULB, Icon.NONE, Icon.NONE)
    covered_b = _card("B", Icon.NONE, Icon.NONE, Icon.BULB, Icon.NONE)
    player = PlayerState(name="Ada", board={Color.RED: Pile(cards=[top, covered_a, covered_b])})

    splay_up(player, Color.RED)

    assert count_icons(player, Icon.BULB) == 2


def test_splay_up_raises_for_a_color_with_no_pile() -> None:
    player = PlayerState(name="Ada")

    with pytest.raises(ValueError, match="RED"):
        splay_up(player, Color.RED)


def test_splay_up_raises_for_an_empty_pile() -> None:
    player = PlayerState(name="Ada", board={Color.RED: Pile()})

    with pytest.raises(ValueError, match="RED"):
        splay_up(player, Color.RED)


def test_count_icons_sums_across_multiple_piles() -> None:
    red_top = _card("RedTop", Icon.CASTLE, Icon.NONE, Icon.NONE, Icon.NONE)
    blue_top = _card("BlueTop", Icon.CASTLE, Icon.NONE, Icon.NONE, Icon.NONE)
    player = PlayerState(
        name="Ada",
        board={
            Color.RED: Pile(cards=[red_top]),
            Color.BLUE: Pile(cards=[blue_top]),
        },
    )

    assert count_icons(player, Icon.CASTLE) == 2


def test_splay_left_raises_for_a_color_with_no_pile() -> None:
    player = PlayerState(name="Ada")

    with pytest.raises(ValueError, match="RED"):
        splay_left(player, Color.RED)


def test_splay_left_raises_for_an_empty_pile() -> None:
    player = PlayerState(name="Ada", board={Color.RED: Pile()})

    with pytest.raises(ValueError, match="RED"):
        splay_left(player, Color.RED)
