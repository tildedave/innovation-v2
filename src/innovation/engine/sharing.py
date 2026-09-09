"""Dogma effect sharing/demanding eligibility.

TODO: demanding isn't implemented yet -- only the share side of dogma
resolution (see docs/rules/actions.md). Sharing is optional for each
eligible player, so activating a dogma with sharing involved is a
multi-step process; ``eligible_to_share`` only answers "who *may*
share," not the step-by-step resolution itself.
"""

from __future__ import annotations

from innovation.engine.board import count_icons
from innovation.model.enums import Icon
from innovation.model.game_state import GameState


def eligible_to_share(state: GameState, active_player_index: int, icon: Icon) -> list[int]:
    """Return the indices of players eligible to share a dogma effect.

    A player other than the active one is eligible to share when they
    have at least as many visible ``icon`` icons on their board as the
    active player does (ties are eligible). Indices are returned in
    turn order starting from the player after the active player
    (``active_player_index + 1``, wrapping around via player count)
    and ending just before the active player -- i.e. clockwise turn
    order, not ascending index order.
    """
    player_count = len(state.players)
    # e.g. active_player_index=2 in a 4-player game gives turn_order
    # [3, 0, 1] (offsets 1, 2, 3 wrapped via % player_count), not
    # ascending index order.
    turn_order = [
        (active_player_index + offset) % player_count for offset in range(1, player_count)
    ]
    active_count = count_icons(state.players[active_player_index], icon)
    return [
        index for index in turn_order if count_icons(state.players[index], icon) >= active_count
    ]
