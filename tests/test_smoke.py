"""Smoke tests confirming the package skeleton is importable and wired up."""

from innovation.model.card import Card
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
        icons=(Icon.CASTLE, Icon.NONE, Icon.NONE, Icon.NONE),
    )

    assert card.age == 1


def test_empty_game_state_constructs() -> None:
    state = GameState()

    assert state.players == []
