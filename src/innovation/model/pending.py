"""Pending steps: queued work left to finish resolving a dogma activation.

TODO: only the "share" side of dogma resolution is modeled here -- no
demand step yet. See docs/rules/actions.md.

TODO: neither ``EffectStep`` nor ``DrawHighestStep`` carries enough to
describe itself for a UI beyond ``ShareStep``/``OptionalStep``'s
``card_name`` -- e.g. an ``EffectStep`` has no ``card_name`` of its
own, so there's nothing to render as "Player 2 draws and melds a 1."
Revisit once there's an actual board view to render for; GameState is
being kept renderable (whose turn, what's pending) for exactly that
eventual purpose -- see docs/architecture.md.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from innovation.model.card import Card, DogmaEffect

if TYPE_CHECKING:
    from innovation.model.game_state import GameState

CardAction = Callable[["GameState", int, str], tuple["GameState", "Card"]]
"""Given the game state, a player index, and a named card from that
player's hand, performs some action on it and returns the new state
plus the affected ``Card``. ``engine.actions.meld``, ``tuck``,
``score``, and ``return_card`` all match this shape -- see
``OptionalStep.action``.
"""

CardEffect = Callable[["GameState", int, "Card"], "GameState"]
"""Given the game state, a player index, and a card, returns the new
state. See ``OptionalStep.if_done``.
"""

CardChoiceValidator = Callable[["GameState", int, str], None]
"""Given the game state, the acting player's index, and the card name
they chose, raises ``ValueError`` if that choice isn't legal for this
particular decision (beyond just "is it in hand," which ``action``
already checks) -- otherwise returns normally. See
``OptionalStep.validate``.
"""


@dataclass(frozen=True)
class ShareStep:
    """The game is waiting on ``player_index`` to decide whether to share.

    If they choose to share, ``effect`` runs for them (for free, at no
    cost to their own turn) before the next step in the queue runs, and
    (if this is the first "yes" for this dogma activation) a
    ``DrawHighestStep`` for ``active_player_index`` is queued at the
    end -- see ``DrawHighestStep``. ``active_player_index`` is who
    activated the dogma (not who's being asked to share).
    ``card_name`` is carried along for display purposes (e.g. "Ask
    Player 3 if they want to share in Sailing?").
    """

    player_index: int
    active_player_index: int
    card_name: str
    effect: DogmaEffect


@dataclass(frozen=True)
class EffectStep:
    """Run ``effect`` for ``player_index`` -- no decision needed."""

    player_index: int
    effect: DogmaEffect


@dataclass(frozen=True)
class DrawHighestStep:
    """Run automatically: ``player_index`` draws a card of their
    highest top-card age.

    Queued (once, at most, per dogma activation) the first time any
    other player shares one of that activation's effects -- see
    ``ShareStep`` and ``innovation.engine.actions.answer_share``.
    """

    player_index: int


@dataclass(frozen=True)
class OptionalStep:
    """The game is waiting on ``player_index`` to decide whether to
    take an optional action on a card from their hand -- the "you may
    X a card from your hand. If you do, Y." pattern, e.g. Agriculture's
    "you may return a card from your hand. If you do, draw and score a
    card of value one higher than the card you return."

    ``action`` performs the choice if they take one (e.g.
    ``innovation.engine.actions.return_card`` for Agriculture -- any
    ``CardAction`` works, so a future "you may meld/tuck/score a card"
    effect reuses this same step with a different ``action``), then
    ``if_done`` runs with the resulting card. If they decline,
    ``if_declined`` runs instead (a no-op if ``None``). Both branches
    exist because "if you do .../ if you don't ..." recurs across
    cards, even though a given card may only use one side of it
    (Agriculture has no "if you don't," so its ``if_declined`` is
    ``None``).

    Deliberately separate from ``ShareStep``: sharing has its own
    ramifications (a bonus draw for the active player) that don't
    apply to an ordinary optional action.

    ``validate``, if set, runs before ``action`` and can reject an
    otherwise-in-hand card that isn't a legal choice for *this*
    decision specifically (e.g. a future card restricted to "a card of
    a color you don't have") -- see
    ``innovation.engine.actions.answer_optional``. Agriculture has no
    such restriction (any card in hand is fine), so its ``validate``
    is ``None``.
    """

    player_index: int
    card_name: str
    action: CardAction
    if_done: CardEffect
    if_declined: DogmaEffect | None = None
    validate: CardChoiceValidator | None = None


PendingStep = ShareStep | EffectStep | DrawHighestStep | OptionalStep
