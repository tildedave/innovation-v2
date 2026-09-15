"""Pure geometry: where things go on screen.

No drawing happens here -- every function takes a bounding
``pygame.Rect`` and returns the ``pygame.Rect``(s) inside it, so the
draw modules (``card_view``, ``board_view``, ``game_view``) can be
reasoned about, or re-laid-out, independently of the actual
``pygame.draw``/``blit`` calls.
"""

from __future__ import annotations

import pygame

from innovation.model.enums import Color, Splay
from innovation.ui.theme import (
    CARD_HEIGHT,
    CARD_SPACING,
    CARD_WIDTH,
    PANEL_MARGIN,
    PILE_SLOT_WIDTH,
    SECTION_GAP,
    SPLAY_OFFSET,
)

HEADER_HEIGHT = 40
FOOTER_HEIGHT = 60

BOARD_COLOR_ORDER = (Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE, Color.PURPLE)


def header_rect(screen: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(screen.left, screen.top, screen.width, HEADER_HEIGHT)


def footer_rect(screen: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(screen.left, screen.bottom - FOOTER_HEIGHT, screen.width, FOOTER_HEIGHT)


def players_area_rect(screen: pygame.Rect) -> pygame.Rect:
    top = screen.top + HEADER_HEIGHT
    bottom = screen.bottom - FOOTER_HEIGHT
    return pygame.Rect(screen.left, top, screen.width, bottom - top)


def player_panel_rects(area: pygame.Rect, num_players: int) -> list[pygame.Rect]:
    """One rect per player, stacked top to bottom, evenly dividing ``area``."""
    if num_players <= 0:
        return []
    panel_height = area.height // num_players
    return [
        pygame.Rect(area.left, area.top + index * panel_height, area.width, panel_height)
        for index in range(num_players)
    ]


def name_label_rect(panel: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(panel.left + PANEL_MARGIN, panel.top + 6, panel.width - 2 * PANEL_MARGIN, 20)


def hand_rect(panel: pygame.Rect) -> pygame.Rect:
    top = panel.top + 6 + 20 + SECTION_GAP
    return pygame.Rect(panel.left + PANEL_MARGIN, top, panel.width - 2 * PANEL_MARGIN, CARD_HEIGHT)


def board_rect(panel: pygame.Rect) -> pygame.Rect:
    top = hand_rect(panel).bottom + SECTION_GAP
    bottom = panel.bottom - PANEL_MARGIN
    return pygame.Rect(
        panel.left + PANEL_MARGIN, top, panel.width - 2 * PANEL_MARGIN, max(0, bottom - top)
    )


def hand_card_rects(hand: pygame.Rect, num_cards: int) -> list[pygame.Rect]:
    """Left-to-right row of card rects for a player's hand."""
    return [
        pygame.Rect(
            hand.left + index * (CARD_WIDTH + CARD_SPACING),
            hand.top,
            CARD_WIDTH,
            CARD_HEIGHT,
        )
        for index in range(num_cards)
    ]


def pile_slot_rects(board: pygame.Rect) -> dict[Color, pygame.Rect]:
    """One slot per board color, left to right in a fixed order."""
    return {
        color: pygame.Rect(
            board.left + index * (PILE_SLOT_WIDTH + CARD_SPACING),
            board.top,
            PILE_SLOT_WIDTH,
            CARD_HEIGHT,
        )
        for index, color in enumerate(BOARD_COLOR_ORDER)
    }


def splayed_card_rects(slot: pygame.Rect, num_cards: int, splay: Splay) -> list[pygame.Rect]:
    """Card rects within one pile ``slot``, top card first (index 0).

    Matches ``Pile.cards`` ordering (index 0 = top, fully visible).
    Covered cards are offset per ``splay`` so the icons ``engine.board``
    treats as visible line up with what's actually drawn; unsplayed
    piles stack every card in the same spot, showing only the top one.
    The caller is responsible for painting in reverse (bottom card
    first) so the top card ends up drawn last, on top.
    """
    if num_cards <= 0:
        return []
    dx, dy = {
        Splay.NONE: (0, 0),
        Splay.LEFT: (-SPLAY_OFFSET, 0),
        Splay.RIGHT: (SPLAY_OFFSET, 0),
        Splay.UP: (0, SPLAY_OFFSET),
    }[splay]
    return [
        pygame.Rect(
            slot.left + dx * index,
            slot.top + dy * index,
            CARD_WIDTH,
            CARD_HEIGHT,
        )
        for index in range(num_cards)
    ]


def supply_rect(footer: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(
        footer.left + PANEL_MARGIN, footer.top + 6, footer.width - 2 * PANEL_MARGIN, 18
    )
