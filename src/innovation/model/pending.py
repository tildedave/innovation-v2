"""Pending steps: queued work left to finish resolving a dogma activation.

TODO: only the "share" side of dogma resolution is modeled here -- no
demand step yet. See docs/rules/actions.md.

TODO: neither step type carries enough to describe itself for a UI
beyond ``ShareStep.card_name`` -- e.g. an ``EffectStep`` has no
``card_name`` of its own, so there's nothing to render as "Player 2
draws and melds a 1." Revisit once there's an actual board view to
render for; GameState is being kept renderable (whose turn, what's
pending) for exactly that eventual purpose -- see docs/architecture.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from innovation.model.card import DogmaEffect


@dataclass(frozen=True)
class ShareStep:
    """The game is waiting on ``player_index`` to decide whether to share.

    If they choose to share, ``effect`` runs for them (for free, at no
    cost to their own turn) before the next step in the queue runs.
    ``card_name`` is carried along for display purposes (e.g. "Ask
    Player 3 if they want to share in Sailing?").
    """

    player_index: int
    card_name: str
    effect: DogmaEffect


@dataclass(frozen=True)
class EffectStep:
    """Run ``effect`` for ``player_index`` -- no decision needed."""

    player_index: int
    effect: DogmaEffect


PendingStep = ShareStep | EffectStep
