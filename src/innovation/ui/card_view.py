"""Drawing a single ``Card`` (or an empty/face-down placeholder) to a surface."""

from __future__ import annotations

import pygame

from innovation.model.card import Card
from innovation.model.enums import Icon
from innovation.ui.theme import (
    CARD_BACK,
    CARD_BORDER,
    CARD_COLORS,
    CARD_CORNER_RADIUS,
    EMPTY_SLOT_BORDER,
    TEXT,
)


def draw_card(
    surface: pygame.Surface,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    icon_glyphs: dict[Icon, pygame.Surface],
    card: Card,
    rect: pygame.Rect,
) -> None:
    """Draw ``card`` face up in ``rect``: name, age, and its four corner icons."""
    color = CARD_COLORS[card.color]
    pygame.draw.rect(surface, color, rect, border_radius=CARD_CORNER_RADIUS)
    pygame.draw.rect(surface, CARD_BORDER, rect, width=2, border_radius=CARD_CORNER_RADIUS)

    age_surface = font.render(str(card.age), True, TEXT)
    surface.blit(age_surface, (rect.left + 6, rect.top + 4))

    name_band = pygame.Rect(rect.left + 4, rect.top + 38, rect.width - 8, rect.height - 78)
    _draw_wrapped_name(surface, small_font, card.name, name_band)

    _draw_icon(surface, icon_glyphs, card.icons.top_left, (rect.left + 8, rect.top + 24))
    _draw_icon(surface, icon_glyphs, card.icons.bottom_left, (rect.left + 8, rect.bottom - 20))
    _draw_icon(surface, icon_glyphs, card.icons.bottom_center, (rect.centerx, rect.bottom - 20))
    _draw_icon(surface, icon_glyphs, card.icons.bottom_right, (rect.right - 8, rect.bottom - 20))


def draw_card_back(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draw a face-down card placeholder (e.g. a supply pile) in ``rect``."""
    pygame.draw.rect(surface, CARD_BACK, rect, border_radius=CARD_CORNER_RADIUS)
    pygame.draw.rect(surface, CARD_BORDER, rect, width=2, border_radius=CARD_CORNER_RADIUS)


def draw_empty_slot(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draw a dashed-looking outline where a card could be but isn't."""
    pygame.draw.rect(surface, EMPTY_SLOT_BORDER, rect, width=1, border_radius=CARD_CORNER_RADIUS)


def _draw_wrapped_name(
    surface: pygame.Surface,
    font: pygame.font.Font,
    name: str,
    band: pygame.Rect,
) -> None:
    """Render ``name`` centered in ``band``, wrapped onto as many lines
    as fit -- card names routinely exceed the card's width (e.g.
    "Metalworking" at the small font size used here), so this breaks
    mid-word rather than letting text spill past the card's edge."""
    lines = _wrap_to_width(font, name, band.width)
    line_height = font.get_linesize()
    max_lines = max(1, band.height // line_height)
    for index, line in enumerate(lines[:max_lines]):
        line_surface = font.render(line, True, TEXT)
        surface.blit(
            line_surface,
            line_surface.get_rect(midtop=(band.centerx, band.top + index * line_height)),
        )


def _wrap_to_width(font: pygame.font.Font, text: str, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and font.size(candidate)[0] > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _draw_icon(
    surface: pygame.Surface,
    icon_glyphs: dict[Icon, pygame.Surface],
    icon: Icon,
    center: tuple[int, int],
) -> None:
    if icon is Icon.NONE:
        return
    glyph = icon_glyphs[icon]
    surface.blit(glyph, glyph.get_rect(center=center))
