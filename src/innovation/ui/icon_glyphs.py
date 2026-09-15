"""Pre-rendering the emoji glyphs used for board icons.

Color emoji fonts (e.g. Apple Color Emoji) are fixed-size bitmap
fonts -- SDL_ttf renders them at their native strike size regardless
of the requested point size, so each glyph is rendered and scaled down
to ``theme.ICON_GLYPH_SIZE`` once here, rather than re-rendered (and
re-scaled) on every frame. Falls back to the plain-text labels in
``theme.ICON_LABELS`` if no emoji-capable font is installed.
"""

from __future__ import annotations

import pygame

from innovation.model.enums import Icon
from innovation.ui.theme import ICON_EMOJI, ICON_GLYPH_SIZE, ICON_LABELS, TEXT

_EMOJI_FONT_CANDIDATES = ("Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", "Noto Emoji")


def load_icon_glyphs(fallback_font: pygame.font.Font) -> dict[Icon, pygame.Surface]:
    """Render every ``Icon`` once, scaled to a ``theme.ICON_GLYPH_SIZE``
    square. ``Icon.NONE`` maps to an empty (fully transparent) surface.
    Uses ``fallback_font`` to render ``theme.ICON_LABELS`` instead if no
    emoji-capable font is found on this system.
    """
    emoji_font = _find_emoji_font()
    glyphs: dict[Icon, pygame.Surface] = {}
    for icon, emoji in ICON_EMOJI.items():
        if not emoji:
            glyphs[icon] = pygame.Surface((ICON_GLYPH_SIZE, ICON_GLYPH_SIZE), pygame.SRCALPHA)
        elif emoji_font is not None:
            glyphs[icon] = _render_emoji(emoji_font, emoji)
        else:
            glyphs[icon] = fallback_font.render(ICON_LABELS[icon], True, TEXT)
    return glyphs


def _find_emoji_font() -> pygame.font.Font | None:
    for name in _EMOJI_FONT_CANDIDATES:
        path = pygame.font.match_font(name)
        if path:
            return pygame.font.Font(path, ICON_GLYPH_SIZE)
    return None


def _render_emoji(font: pygame.font.Font, emoji: str) -> pygame.Surface:
    """Render ``emoji`` and fit it, aspect-preserved, into an
    ``ICON_GLYPH_SIZE`` square -- the font's native strike is rarely
    square (e.g. Apple Color Emoji's is 160x210), so scaling to the
    square directly would distort it."""
    rendered = font.render(emoji, True, TEXT)
    scale = min(ICON_GLYPH_SIZE / rendered.get_width(), ICON_GLYPH_SIZE / rendered.get_height())
    scaled_size = (
        max(1, round(rendered.get_width() * scale)),
        max(1, round(rendered.get_height() * scale)),
    )
    scaled = pygame.transform.smoothscale(rendered, scaled_size)
    surface = pygame.Surface((ICON_GLYPH_SIZE, ICON_GLYPH_SIZE), pygame.SRCALPHA)
    surface.blit(scaled, scaled.get_rect(center=(ICON_GLYPH_SIZE // 2, ICON_GLYPH_SIZE // 2)))
    return surface
