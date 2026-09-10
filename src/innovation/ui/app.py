"""Entry point for the dev/debug visualizer.

Opens a pygame window, builds the demo timeline (see ``timeline``), and
lets you step through it with the arrow keys -- each ``GameState``
snapshot is rendered by ``game_view``. No game logic lives here: this
module only owns the event loop and which timeline index is current.
"""

from __future__ import annotations

import pygame

from innovation.ui.fonts import load_fonts
from innovation.ui.game_view import draw_game_state
from innovation.ui.timeline import build_demo_timeline

WINDOW_SIZE = (1280, 800)
WINDOW_TITLE = "Innovation -- dev visualizer"
FRAME_RATE = 30


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    fonts = load_fonts()

    timeline = build_demo_timeline()
    index = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_RIGHT, pygame.K_SPACE):
                    index = min(index + 1, len(timeline) - 1)
                elif event.key == pygame.K_LEFT:
                    index = max(index - 1, 0)
                elif event.key == pygame.K_HOME:
                    index = 0
                elif event.key == pygame.K_END:
                    index = len(timeline) - 1

        step = timeline[index]
        step_label = f"step {index + 1}/{len(timeline)}: {step.label}"
        draw_game_state(screen, fonts, step.state, step_label)
        pygame.display.flip()
        clock.tick(FRAME_RATE)

    pygame.quit()


if __name__ == "__main__":
    main()
