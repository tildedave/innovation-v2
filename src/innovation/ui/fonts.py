"""Loading the pygame fonts the draw modules share.

Separate from ``theme`` because constructing a ``pygame.font.Font``
requires ``pygame.font`` to already be initialized -- ``theme`` stays
import-safe (no pygame subsystem side effects) so it can be imported
anywhere, including by ``layout``, without needing a display or font
module set up first.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from innovation.ui.theme import FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_NORMAL, FONT_SIZE_SMALL


@dataclass(frozen=True)
class Fonts:
    normal: pygame.font.Font
    small: pygame.font.Font
    large: pygame.font.Font


def load_fonts() -> Fonts:
    """Load the shared font set. Requires ``pygame.font.init()`` to have run."""
    return Fonts(
        normal=pygame.font.Font(FONT_NAME, FONT_SIZE_NORMAL),
        small=pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL),
        large=pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE),
    )
