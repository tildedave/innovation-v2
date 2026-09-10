"""Drawing one player's panel: name, hand, board piles, score pile, achievements."""

from __future__ import annotations

import pygame

from innovation.model.player import PlayerState
from innovation.ui import layout
from innovation.ui.card_view import draw_card, draw_empty_slot
from innovation.ui.fonts import Fonts
from innovation.ui.theme import (
    CURRENT_PLAYER_HIGHLIGHT,
    MUTED_TEXT,
    PANEL_BACKGROUND,
    TEXT,
)


def draw_player(
    surface: pygame.Surface,
    fonts: Fonts,
    player: PlayerState,
    panel: pygame.Rect,
    *,
    is_current: bool,
) -> None:
    pygame.draw.rect(surface, PANEL_BACKGROUND, panel)
    if is_current:
        pygame.draw.rect(surface, CURRENT_PLAYER_HIGHLIGHT, panel, width=2)

    _draw_name(surface, fonts, player, panel, is_current=is_current)
    _draw_hand(surface, fonts, player, panel)
    _draw_board(surface, fonts, player, panel)


def _draw_name(
    surface: pygame.Surface,
    fonts: Fonts,
    player: PlayerState,
    panel: pygame.Rect,
    *,
    is_current: bool,
) -> None:
    label_rect = layout.name_label_rect(panel)
    color = CURRENT_PLAYER_HIGHLIGHT if is_current else TEXT
    suffix = "  (current turn)" if is_current else ""
    text = fonts.normal.render(f"{player.name}{suffix}", True, color)
    surface.blit(text, label_rect.topleft)

    summary = (
        f"hand {len(player.hand)}  |  score pile {len(player.score_pile)}  |  "
        f"achievements {len(player.achievements)}"
    )
    summary_surface = fonts.small.render(summary, True, MUTED_TEXT)
    surface.blit(summary_surface, (label_rect.right + 16, label_rect.top + 2))


def _draw_hand(
    surface: pygame.Surface, fonts: Fonts, player: PlayerState, panel: pygame.Rect
) -> None:
    hand_area = layout.hand_rect(panel)
    for card, rect in zip(
        player.hand, layout.hand_card_rects(hand_area, len(player.hand)), strict=True
    ):
        draw_card(surface, fonts.normal, fonts.small, card, rect)


def _draw_board(
    surface: pygame.Surface, fonts: Fonts, player: PlayerState, panel: pygame.Rect
) -> None:
    board_area = layout.board_rect(panel)
    for color, slot in layout.pile_slot_rects(board_area).items():
        pile = player.board.get(color)
        if pile is None or not pile.cards:
            draw_empty_slot(surface, slot)
            continue
        card_rects = layout.splayed_card_rects(slot, len(pile.cards), pile.splay)
        for card, rect in reversed(list(zip(pile.cards, card_rects, strict=True))):
            draw_card(surface, fonts.normal, fonts.small, card, rect)
