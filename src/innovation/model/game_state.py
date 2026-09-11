"""Top-level game state."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from innovation.model.card import Card
from innovation.model.pending import PendingStep
from innovation.model.player import PlayerState


@dataclass(frozen=True)
class GameState:
    """Immutable snapshot of the full state of a single game in progress.

    Every change is expressed as a new ``GameState`` -- see
    ``innovation.engine.actions``, which builds one with
    ``dataclasses.replace`` rather than mutating this one. That's
    deliberate: cheap, copy-free "apply a move and get a new state" is
    what search algorithms (minimax, MCTS, ...) need to branch and
    backtrack without deep-copying or writing undo logic. It also
    means the state a UI needs to render (whose turn it is, what
    decision is pending) is always just a field read, not something
    reconstructed from a mutation log.

    ``current_player_index`` is whose turn it is -- see
    ``innovation.engine.game.start_turn``/``take_*_action`` for the
    turn loop that advances it (a player's actions run out, or the
    lexicographically-first opening meld picks it initially, see
    ``innovation.engine.setup``).

    ``actions_remaining`` is how many of the current player's turn
    actions (Draw, Meld, Dogma, Achieve) are left to take. Zero means
    no turn is in progress -- ``engine.game.start_turn`` must be called
    to begin one. Two per turn, except the very first turn of the
    game, which is one (see ``first_turn_taken`` and
    docs/rules/overview.md).

    ``first_turn_taken`` marks whether the game's one-action opening
    turn has already happened, so every later call to
    ``engine.game.start_turn`` knows to grant two actions instead.

    ``pending_steps`` is the queue of work left to finish resolving an
    in-progress dogma activation (see ``innovation.model.pending`` and
    ``innovation.engine.actions.dogma``/``answer_share``) or the
    opening meld (see ``innovation.engine.setup.start_game``). Empty
    means nothing is waiting on a decision.

    ``supply`` maps age -> that age's remaining deck, with ``[0]`` the
    next card to be drawn (see ``innovation.engine.actions.draw``).
    ``supply`` and ``board`` (on ``PlayerState``) are typed as
    read-only ``Mapping`` for the same reason and with the same
    runtime caveat -- see ``innovation.model.player``.

    TODO: Add the special-achievements pool once Achieve (see
    ``innovation.engine.actions.achieve``) is designed.
    """

    players: tuple[PlayerState, ...] = field(default_factory=tuple)
    current_player_index: int = 0
    actions_remaining: int = 0
    first_turn_taken: bool = False
    pending_steps: tuple[PendingStep, ...] = field(default_factory=tuple)
    supply: Mapping[int, tuple[Card, ...]] = field(default_factory=dict)
    achievements_available: tuple[Card, ...] = field(default_factory=tuple)
