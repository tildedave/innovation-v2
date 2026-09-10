"""Turn-loop orchestration.

TODO: Detect the achievement-count and special-achievement win
conditions -- ``is_over``/``Game`` below. See docs/rules/overview.md.
"""

from __future__ import annotations

from dataclasses import replace

from innovation.engine.actions import dogma, draw, meld, pending_decision
from innovation.model.game_state import GameState


def start_turn(state: GameState) -> GameState:
    """Grant the current player their turn's action budget.

    Two actions, except the very first turn of the whole game, which
    is only one (see ``GameState.first_turn_taken``) -- see
    docs/rules/overview.md. Raises ``ValueError`` if a turn is already
    in progress (``actions_remaining`` is nonzero) or a previous
    action's decision (see ``engine.actions.pending_decision``) hasn't
    been resolved yet.
    """
    if state.actions_remaining != 0:
        raise ValueError("a turn is already in progress")
    if pending_decision(state) is not None:
        raise ValueError("a previous action still has an unresolved decision")
    actions = 2 if state.first_turn_taken else 1
    return replace(state, actions_remaining=actions, first_turn_taken=True)


def take_draw_action(state: GameState, player_index: int) -> GameState:
    """The current player's base turn Draw action.

    Draws a card of the player's own highest melded top-card age (see
    ``engine.actions.draw``) and consumes one of the turn's actions.
    """
    _require_ready_for_action(state, player_index)
    state, _ = draw(state, player_index)
    return _consume_action(state)


def take_meld_action(state: GameState, player_index: int, card_name: str) -> GameState:
    """The current player's base turn Meld action.

    Melds ``card_name`` from hand (see ``engine.actions.meld``) and
    consumes one of the turn's actions.
    """
    _require_ready_for_action(state, player_index)
    state, _ = meld(state, player_index, card_name)
    return _consume_action(state)


def take_dogma_action(state: GameState, player_index: int, card_name: str) -> GameState:
    """The current player's base turn Dogma action.

    Activates ``card_name``'s dogma effects (see
    ``engine.actions.dogma``) and consumes one of the turn's actions
    immediately -- even though the dogma's own sharing decisions (see
    ``engine.actions.answer_share``) may still be pending afterward;
    resolving those is a separate, later concern from which *action*
    was taken this turn. ``current_player_index`` can therefore
    advance to the next player while a share decision from this
    action is still unresolved -- ``_require_ready_for_action`` blocks
    that next player from acting until it is.
    """
    _require_ready_for_action(state, player_index)
    state = dogma(state, player_index, card_name)
    return _consume_action(state)


def take_achieve_action(state: GameState, player_index: int) -> GameState:
    """The current player's base turn Achieve action.

    TODO: not implemented yet -- see ``engine.actions.achieve``.
    """
    _require_ready_for_action(state, player_index)
    raise NotImplementedError("Achieve is not implemented yet")


def _require_ready_for_action(state: GameState, player_index: int) -> None:
    if pending_decision(state) is not None:
        raise ValueError("a previous action still has an unresolved decision")
    if player_index != state.current_player_index:
        raise ValueError(
            f"it is player {state.current_player_index}'s turn, not player {player_index}'s"
        )
    if state.actions_remaining <= 0:
        raise ValueError("no actions remaining this turn -- call start_turn first")


def _consume_action(state: GameState) -> GameState:
    """Spend one of the turn's actions, advancing to the next player's
    turn once none are left."""
    actions_remaining = state.actions_remaining - 1
    if actions_remaining == 0:
        next_player_index = (state.current_player_index + 1) % len(state.players)
        return replace(state, actions_remaining=0, current_player_index=next_player_index)
    return replace(state, actions_remaining=actions_remaining)


class Game:
    """Owns a ``GameState`` and runs turns against it."""

    def __init__(self, state: GameState) -> None:
        self.state = state

    def is_over(self) -> bool:
        raise NotImplementedError
