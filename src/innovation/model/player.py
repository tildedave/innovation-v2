"""Per-player game state."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from innovation.model.card import Card
from innovation.model.enums import Color
from innovation.model.pile import Pile


@dataclass(frozen=True)
class PlayerState:
    """Immutable snapshot of state owned by a single player.

    Every change is expressed as a new ``PlayerState`` -- see
    ``innovation.engine.actions``, which builds one with
    ``dataclasses.replace`` rather than mutating this one.

    ``board`` only holds entries for colors the player has melded at
    least one card of -- see ``innovation.engine.board`` for splaying
    and icon-visibility queries. It's typed as a read-only ``Mapping``
    so mypy rejects ``player.board[color] = ...``; nothing at runtime
    stops a caller from mutating the underlying ``dict`` directly, so
    don't -- treat it as immutable like every other field here.

    TODO: Add achievement/special-achievement bookkeeping details once
    the engine's action logic (see docs/rules/actions.md) is designed.
    """

    name: str
    hand: tuple[Card, ...] = field(default_factory=tuple)
    score_pile: tuple[Card, ...] = field(default_factory=tuple)
    board: Mapping[Color, Pile] = field(default_factory=dict)
    achievements: tuple[Card, ...] = field(default_factory=tuple)
