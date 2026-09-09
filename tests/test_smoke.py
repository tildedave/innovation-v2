"""Smoke tests confirming the package skeleton is importable and wired up."""

import dataclasses

import pytest

from innovation.model.card import Card, CardIcons
from innovation.model.enums import Color, Icon
from innovation.model.game_state import GameState


def test_package_exposes_a_version() -> None:
    import innovation

    assert innovation.__version__


def test_card_is_constructible() -> None:
    card = Card(
        name="Placeholder",
        age=1,
        color=Color.RED,
        icons=CardIcons(
            top_left=Icon.CASTLE,
            bottom_left=Icon.NONE,
            bottom_center=Icon.NONE,
            bottom_right=Icon.NONE,
        ),
    )

    assert card.age == 1


def test_empty_game_state_constructs() -> None:
    state = GameState()

    assert state.players == ()


def test_game_state_is_immutable() -> None:
    state = GameState()

    with pytest.raises(dataclasses.FrozenInstanceError):
        state.players = (None,)  # type: ignore[misc]
