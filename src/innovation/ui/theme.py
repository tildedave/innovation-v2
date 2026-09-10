"""Colors, fonts, and sizing constants shared by the visualizer's drawing code.

Kept separate from the drawing functions themselves (see ``card_view``,
``board_view``, ``game_view``) so a palette or size tweak doesn't touch
layout math or draw calls.
"""

from __future__ import annotations

from innovation.model.enums import Color, Icon

BACKGROUND = (24, 28, 22)
PANEL_BACKGROUND = (34, 39, 32)
CURRENT_PLAYER_HIGHLIGHT = (90, 200, 120)
TEXT = (235, 235, 230)
MUTED_TEXT = (160, 160, 155)
CARD_BACK = (60, 65, 70)
CARD_BORDER = (10, 10, 10)
EMPTY_SLOT_BORDER = (70, 75, 70)

CARD_COLORS: dict[Color, tuple[int, int, int]] = {
    Color.RED: (196, 60, 50),
    Color.YELLOW: (222, 186, 55),
    Color.GREEN: (70, 145, 80),
    Color.BLUE: (60, 110, 190),
    Color.PURPLE: (135, 80, 160),
}

ICON_LABELS: dict[Icon, str] = {
    Icon.CASTLE: "Cs",
    Icon.CROWN: "Cr",
    Icon.LEAF: "Lf",
    Icon.FACTORY: "Fy",
    Icon.CLOCK: "Ck",
    Icon.BULB: "Bb",
    Icon.NONE: "",
}
"""Fallback used in place of ``ICON_EMOJI`` on a system with no emoji
font available -- see ``innovation.ui.icon_glyphs``."""

ICON_EMOJI: dict[Icon, str] = {
    Icon.CASTLE: "🏰",
    Icon.CROWN: "👑",
    Icon.LEAF: "🍃",
    Icon.FACTORY: "🏭",
    Icon.CLOCK: "⏰",
    Icon.BULB: "💡",
    Icon.NONE: "",
}

ICON_GLYPH_SIZE = 18
"""Side length, in pixels, of a pre-rendered icon glyph -- see
``innovation.ui.icon_glyphs``."""

CARD_WIDTH = 84
CARD_HEIGHT = 118
CARD_CORNER_RADIUS = 6
CARD_SPACING = 10

SPLAY_OFFSET = 22
"""Horizontal offset between stacked cards in a splayed pile."""

PILE_SLOT_WIDTH = CARD_WIDTH + 3 * SPLAY_OFFSET
"""Width reserved for one board pile slot, wide enough for a fully
splayed stack's cascade of covered cards."""

PANEL_MARGIN = 16
SECTION_GAP = 10

FONT_NAME = None
"""``None`` selects pygame's default font."""

FONT_SIZE_NORMAL = 16
FONT_SIZE_SMALL = 13
FONT_SIZE_LARGE = 20
