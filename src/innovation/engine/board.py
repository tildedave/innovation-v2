"""Board queries and mutations: splaying piles and counting visible icons."""

from __future__ import annotations

from innovation.model.card import CardIcons
from innovation.model.enums import Color, Icon, Splay
from innovation.model.pile import Pile
from innovation.model.player import PlayerState


def splay_left(player: PlayerState, color: Color) -> None:
    """Splay a player's pile of the given color to the left.

    Splaying left exposes the bottom-right icon of every card in the
    pile except the top card, which is always fully visible.
    """
    pile = _require_pile(player, color)
    pile.splay = Splay.LEFT


def splay_right(player: PlayerState, color: Color) -> None:
    """Splay a player's pile of the given color to the right.

    Splaying right exposes the top-left and bottom-left icons of every
    card in the pile except the top card, which is always fully visible.
    """
    pile = _require_pile(player, color)
    pile.splay = Splay.RIGHT


def splay_up(player: PlayerState, color: Color) -> None:
    """Splay a player's pile of the given color up.

    Splaying up exposes every icon except the top-left icon (i.e. the
    bottom-left, bottom-center, and bottom-right icons) of every card
    in the pile except the top card, which is always fully visible.
    """
    pile = _require_pile(player, color)
    pile.splay = Splay.UP


def count_icons(player: PlayerState, icon: Icon) -> int:
    """Count how many of a given icon are currently visible on a player's board."""
    return sum(_visible_icons(pile).count(icon) for pile in player.board.values())


def _require_pile(player: PlayerState, color: Color) -> Pile:
    pile = player.board.get(color)
    if pile is None or not pile.cards:
        raise ValueError(f"player {player.name!r} has no {color.name} pile to splay")
    return pile


def _visible_icons(pile: Pile) -> list[Icon]:
    if not pile.cards:
        return []

    visible = list(pile.cards[0].icons.all_icons())
    for card in pile.cards[1:]:
        visible.extend(_covered_icons(card.icons, pile.splay))
    return visible


def _covered_icons(icons: CardIcons, splay: Splay) -> list[Icon]:
    match splay:
        case Splay.NONE:
            return []
        case Splay.LEFT:
            return [icons.bottom_right]
        case Splay.RIGHT:
            return [icons.top_left, icons.bottom_left]
        case Splay.UP:
            return [icons.bottom_left, icons.bottom_center, icons.bottom_right]
