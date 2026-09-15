"""Building a scripted sequence of ``GameState`` snapshots to visualize.

There's no turn loop or legal-move enumeration yet (see
``innovation.engine.game``), so nothing can offer a player real
choices. Instead, this drives ``innovation.engine.actions`` through a
fixed demo script and records the resulting state after each action,
labeled with what just happened -- the visualizer then just steps
through the list. Immutable ``GameState`` makes this "time travel"
free: every entry is a distinct, already-computed snapshot, not
something replayed or diffed on the fly.

This module is the one place in ``innovation.ui`` that calls into
``innovation.engine`` to *change* state rather than just read it for
rendering -- see docs/architecture.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from innovation.cards.registry import AGRICULTURE, DOMESTICATION, METALWORKING, SAILING
from innovation.engine.actions import (
    answer_choice,
    answer_optional,
    answer_share,
    dogma,
    draw,
    meld,
    pending_decision,
)
from innovation.model.game_state import GameState
from innovation.model.pending import ChoiceStep, OptionalStep, ShareStep
from innovation.model.player import PlayerState


@dataclass(frozen=True)
class TimelineStep:
    """One entry in the demo timeline: a snapshot plus a description of
    the action that just produced it (see ``build_demo_timeline``)."""

    label: str
    state: GameState


def build_demo_timeline() -> list[TimelineStep]:
    """Script a small two-player game through the four implemented
    cards and return every intermediate ``GameState`` along the way.
    """
    steps: list[TimelineStep] = []
    supply = {1: (SAILING, DOMESTICATION, METALWORKING, AGRICULTURE) * 8}
    state = GameState(players=(PlayerState(name="Alice"), PlayerState(name="Bob")), supply=supply)
    steps.append(TimelineStep("Initial state: two players, empty hands.", state))

    for player_index in (0, 1):
        for _ in range(2):
            state, card = draw(state, player_index, age=1)
            name = state.players[player_index].name
            steps.append(TimelineStep(f"{name} draws {card.name}.", state))

    state, _ = meld(state, 0, "Sailing")
    steps.append(TimelineStep("Alice melds Sailing.", state))

    state, _ = meld(state, 1, "Metalworking")
    steps.append(TimelineStep("Bob melds Metalworking.", state))

    state, _ = meld(state, 0, "Domestication")
    steps.append(TimelineStep("Alice melds Domestication.", state))

    state = _activate(state, steps, player_index=0, card_name="Domestication", share=True)
    state = _activate(state, steps, player_index=0, card_name="Sailing", share=True)
    state = _activate(state, steps, player_index=1, card_name="Agriculture", share=False)
    state = _activate(state, steps, player_index=1, card_name="Metalworking", share=True)

    return steps


def _activate(
    state: GameState,
    steps: list[TimelineStep],
    *,
    player_index: int,
    card_name: str,
    share: bool,
) -> GameState:
    """Activate ``card_name``'s dogma for ``player_index`` and resolve
    every decision it raises (sharing, optional actions, mandatory
    choices), recording a labeled snapshot after each step."""
    player_name = state.players[player_index].name
    state = dogma(state, player_index, card_name)
    steps.append(TimelineStep(f"{player_name} activates {card_name}'s dogma.", state))
    return _resolve_pending_decisions(state, steps, share=share)


def _resolve_pending_decisions(
    state: GameState, steps: list[TimelineStep], *, share: bool
) -> GameState:
    while True:
        step = pending_decision(state)
        if step is None:
            return state
        player_name = state.players[step.player_index].name
        if isinstance(step, ShareStep):
            state = answer_share(state, share)
            verb = "agrees to share" if share else "declines to share"
            steps.append(TimelineStep(f"{player_name} {verb} {step.card_name}.", state))
        elif isinstance(step, OptionalStep):
            state = answer_optional(state, None)
            steps.append(
                TimelineStep(
                    f"{player_name} declines the optional action for {step.card_name}.", state
                )
            )
        elif isinstance(step, ChoiceStep):
            hand = state.players[step.player_index].hand
            chosen = min(hand, key=lambda card: card.age).name
            state = answer_choice(state, chosen)
            steps.append(
                TimelineStep(f"{player_name} chooses {chosen} for {step.card_name}.", state)
            )
