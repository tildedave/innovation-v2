"""Game setup: opening draw, opening meld, and first-player determination.

TODO: special achievements and the "junk" pile aren't modeled yet --
this only covers what's needed to get from an empty ``GameState`` to
whoever's turn it is first. See docs/rules/overview.md.
"""

from __future__ import annotations

from dataclasses import replace

from innovation.engine.actions import draw, meld
from innovation.model.card import Card
from innovation.model.game_state import GameState
from innovation.model.pending import ChoiceStep, EffectStep
from innovation.model.player import PlayerState


def start_game(state: GameState) -> GameState:
    """Deal every player's opening hand and queue their opening meld.

    Each player draws two age-1 cards into their hand, then a
    ``ChoiceStep`` is queued for each of them (in player order) to
    meld one of the two -- resolved via
    ``engine.actions.answer_choice`` like any other choice, so a UI
    can render "Player N: choose a card to meld" the same way it would
    any other pending decision. Both drawn cards are equally legal, so
    there's nothing to ``validate``.

    Once every player's opening meld is resolved, a final queued step
    (see ``_set_first_player``) sets ``current_player_index`` to
    whoever melded the lexicographically-first card by name --
    ``answer_choice`` runs it automatically as soon as the last
    ``ChoiceStep`` is answered.
    """
    for player_index in range(len(state.players)):
        state, _ = draw(state, player_index, age=1)
        state, _ = draw(state, player_index, age=1)

    opening_melds = [
        ChoiceStep(
            player_index=player_index,
            card_name="Opening meld",
            action=meld,
            if_done=lambda state, player_index, melded_card: state,
        )
        for player_index in range(len(state.players))
    ]
    set_first_player = EffectStep(player_index=0, effect=_set_first_player)
    return replace(state, pending_steps=(*state.pending_steps, *opening_melds, set_first_player))


def _set_first_player(state: GameState, player_index: int) -> GameState:
    """Set ``current_player_index`` to whoever melded the
    lexicographically-first card by name during the opening meld.

    Ties (two players' opening melds sharing a name) go to the lower
    player index, since ``min`` is stable over ``range``.
    """
    first_player_index = min(
        range(len(state.players)),
        key=lambda index: _opening_meld(state.players[index]).name,
    )
    return replace(state, current_player_index=first_player_index)


def _opening_meld(player: PlayerState) -> Card:
    """The single card a player melded during ``start_game``'s opening meld.

    Assumes ``player``'s board holds exactly the one pile/card they
    just melded -- true right after the opening meld, since a fresh
    game starts with empty boards.
    """
    (pile,) = player.board.values()
    (card,) = pile.cards
    return card
