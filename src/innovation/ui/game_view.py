"""Drawing a full ``GameState``: every player's panel, the supply, and
whatever decision (if any) is currently pending.
"""

from __future__ import annotations

import pygame

from innovation.engine.actions import pending_decision
from innovation.model.enums import Icon
from innovation.model.game_state import GameState
from innovation.model.pending import ChoiceStep, OptionalStep, ShareStep
from innovation.ui import layout
from innovation.ui.board_view import draw_player
from innovation.ui.fonts import Fonts
from innovation.ui.theme import BACKGROUND, MUTED_TEXT, PANEL_MARGIN, TEXT


def draw_game_state(
    surface: pygame.Surface,
    fonts: Fonts,
    icon_glyphs: dict[Icon, pygame.Surface],
    state: GameState,
    step_label: str,
) -> None:
    surface.fill(BACKGROUND)
    screen = surface.get_rect()

    _draw_header(surface, fonts, state, screen)

    players_area = layout.players_area_rect(screen)
    panels = layout.player_panel_rects(players_area, len(state.players))
    for index, (player, panel) in enumerate(zip(state.players, panels, strict=True)):
        draw_player(
            surface,
            fonts,
            icon_glyphs,
            player,
            panel,
            is_current=index == state.current_player_index,
        )

    _draw_footer(surface, fonts, state, screen, step_label)


def _draw_header(
    surface: pygame.Surface, fonts: Fonts, state: GameState, screen: pygame.Rect
) -> None:
    header = layout.header_rect(screen)
    decision = _describe_pending(state)
    text = decision if decision else "No decision pending."
    surface.blit(
        fonts.normal.render(text, True, TEXT), (header.left + PANEL_MARGIN, header.top + 10)
    )


def _draw_footer(
    surface: pygame.Surface,
    fonts: Fonts,
    state: GameState,
    screen: pygame.Rect,
    step_label: str,
) -> None:
    footer = layout.footer_rect(screen)
    pygame.draw.line(surface, MUTED_TEXT, footer.topleft, footer.topright, width=1)

    supply_area = layout.supply_rect(footer)
    supply_text = "supply: " + ", ".join(
        f"age {age}: {len(state.supply.get(age, ()))}" for age in sorted(state.supply)
    )
    surface.blit(fonts.small.render(supply_text, True, MUTED_TEXT), supply_area.topleft)

    step_surface = fonts.small.render(step_label, True, TEXT)
    surface.blit(step_surface, (supply_area.left, supply_area.bottom + 4))

    help_surface = fonts.small.render(
        "<- / -> to step through the timeline, Esc to quit", True, MUTED_TEXT
    )
    help_rect = help_surface.get_rect(bottomright=(footer.right - PANEL_MARGIN, footer.bottom - 6))
    surface.blit(help_surface, help_rect)


def _describe_pending(state: GameState) -> str | None:
    step = pending_decision(state)
    if step is None:
        return None
    player_name = state.players[step.player_index].name
    if isinstance(step, ShareStep):
        return f"Waiting on {player_name} to decide whether to share {step.card_name}."
    if isinstance(step, OptionalStep):
        return f"Waiting on {player_name} to decide whether to act on {step.card_name}."
    if isinstance(step, ChoiceStep):
        return f"Waiting on {player_name} to choose a card for {step.card_name}."
    return f"Waiting on {player_name}."
