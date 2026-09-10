"""Tests for pure layout geometry (src/innovation/ui/layout.py)."""

import pygame

from innovation.model.enums import Color, Splay
from innovation.ui import layout
from innovation.ui.theme import CARD_HEIGHT, CARD_SPACING, CARD_WIDTH, SPLAY_OFFSET


def test_player_panel_rects_divides_area_evenly_by_player_count() -> None:
    area = pygame.Rect(0, 0, 1000, 300)

    panels = layout.player_panel_rects(area, num_players=3)

    assert [panel.height for panel in panels] == [100, 100, 100]
    assert [panel.top for panel in panels] == [0, 100, 200]


def test_player_panel_rects_returns_nothing_for_zero_players() -> None:
    area = pygame.Rect(0, 0, 1000, 300)

    assert layout.player_panel_rects(area, num_players=0) == []


def test_hand_card_rects_returns_one_rect_per_card_left_to_right() -> None:
    hand = pygame.Rect(0, 0, 1000, CARD_HEIGHT)

    rects = layout.hand_card_rects(hand, num_cards=3)

    assert len(rects) == 3
    assert [rect.left for rect in rects] == [
        0,
        CARD_WIDTH + CARD_SPACING,
        2 * (CARD_WIDTH + CARD_SPACING),
    ]
    assert all(rect.width == CARD_WIDTH and rect.height == CARD_HEIGHT for rect in rects)


def test_pile_slot_rects_returns_one_slot_per_color_in_a_fixed_order() -> None:
    board = pygame.Rect(0, 0, 2000, CARD_HEIGHT)

    slots = layout.pile_slot_rects(board)

    assert list(slots.keys()) == [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE, Color.PURPLE]
    assert slots[Color.RED].left < slots[Color.YELLOW].left < slots[Color.GREEN].left


def test_splayed_card_rects_returns_nothing_for_an_empty_pile() -> None:
    slot = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)

    assert layout.splayed_card_rects(slot, num_cards=0, splay=Splay.NONE) == []


def test_unsplayed_pile_stacks_every_card_at_the_same_position() -> None:
    slot = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)

    rects = layout.splayed_card_rects(slot, num_cards=3, splay=Splay.NONE)

    assert all(rect.topleft == slot.topleft for rect in rects)


def test_splay_up_offsets_each_covered_card_downward() -> None:
    slot = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)

    rects = layout.splayed_card_rects(slot, num_cards=3, splay=Splay.UP)

    assert [rect.top for rect in rects] == [0, SPLAY_OFFSET, 2 * SPLAY_OFFSET]
    assert all(rect.left == slot.left for rect in rects)
