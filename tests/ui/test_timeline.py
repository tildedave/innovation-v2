"""Tests for the scripted demo timeline (src/innovation/ui/timeline.py)."""

from innovation.engine.actions import pending_decision
from innovation.ui.timeline import build_demo_timeline


def test_build_demo_timeline_produces_a_distinct_snapshot_per_labeled_step() -> None:
    steps = build_demo_timeline()

    assert len(steps) > 1
    assert all(step.label for step in steps)


def test_build_demo_timeline_starts_with_two_players_and_empty_hands() -> None:
    steps = build_demo_timeline()

    initial = steps[0].state
    assert [player.name for player in initial.players] == ["Alice", "Bob"]
    assert all(player.hand == () for player in initial.players)


def test_build_demo_timeline_resolves_every_decision_it_raises() -> None:
    steps = build_demo_timeline()

    final_state = steps[-1].state
    assert pending_decision(final_state) is None


def test_build_demo_timeline_melds_the_scripted_cards_for_each_player() -> None:
    steps = build_demo_timeline()

    final_state = steps[-1].state
    alice, bob = final_state.players
    alice_melded = {card.name for pile in alice.board.values() for card in pile.cards}
    bob_melded = {card.name for pile in bob.board.values() for card in pile.cards}

    assert {"Sailing", "Domestication"} <= alice_melded
    assert {"Metalworking", "Agriculture"} <= bob_melded
